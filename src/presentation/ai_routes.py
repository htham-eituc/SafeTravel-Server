# ai_route.py
import asyncio
import os
import re
from datetime import datetime, timedelta
from typing import List, Optional

import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from google import genai
from google.genai import types
from google.api_core import exceptions
from dotenv import load_dotenv

# ==========================
# 0. CONFIGURATION
# ==========================
load_dotenv()
GEOAPIFY_KEY = os.getenv("GEOAPIFY_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Cấu hình Model & Retry
# Lưu ý: Hiện tại Google mới public bản 2.0-flash-exp. 
# Nếu bạn có quyền truy cập 2.5, hãy đổi chuỗi này.
MODEL_NAME = "gemini-2.5-flash-lite " 
RETRY_DELAY_SECONDS = 2  # Yêu cầu: Timeout/Delay 2s khi lỗi
MAX_RETRIES = 3

# ==========================
# 1. STRICT PYDANTIC MODELS
# ==========================
class WeatherInfo(BaseModel):
    date: str = Field(
        ..., 
        description="Ngày dự báo, bắt buộc định dạng chuẩn 'YYYY-MM-DD' (Ví dụ: 2024-12-25)"
    )
    temperature: str = Field(
        ..., 
        description="Khoảng nhiệt độ trong ngày, format 'Thấp-Cao°C' (Ví dụ: 24-31°C)"
    )
    condition: str = Field(
        ..., 
        description="Mô tả ngắn gọn trạng thái thời tiết (Ví dụ: Mưa rào rải rác, Nắng nóng, Có mây)"
    )

class TravelTip(BaseModel):
    category: str = Field(
        ..., 
        description="Phân loại lời khuyên. Chỉ chọn trong: [Trang phục, Di chuyển, An toàn, Y tế, Ăn uống]"
    )
    advice: str = Field(
        ..., 
        description="Lời khuyên hành động cụ thể cho du khách dựa trên tình hình thực tế (Không chung chung)."
    )

class ProvinceData(BaseModel):
    province_name: str = Field(..., description="Tên chính thức của tỉnh/thành phố.")
    report_date: str = Field(..., description="Ngày tạo báo cáo (YYYY-MM-DD).")
    
    weather_forecast: List[WeatherInfo] = Field(
        ..., 
        description="Danh sách dự báo thời tiết chính xác cho 3 ngày tới."
    )
    
    travel_advice: List[TravelTip] = Field(
        ..., 
        description="Tối thiểu 3 lời khuyên quan trọng nhất dựa trên thời tiết và tin tức thu thập được."
    )
    
    executive_summary: str = Field(
        ..., 
        description="Đoạn văn khoảng 50-80 từ, tổng hợp ngắn gọn xem có nên đi du lịch lúc này không và tại sao."
    )
    
    sources: List[str] = Field(..., description="Danh sách các URL uy tín đã tham khảo.")
    
    score: int = Field(
        ..., 
        description="Điểm số an toàn du lịch (0-100). Phải tuân thủ nghiêm ngặt thang điểm quy định trong prompt."
    )

class VietnamReport(BaseModel):
    provinces: List[ProvinceData]

class LocationRequest(BaseModel):
    lat: float
    long: float

# ==========================
# 2. GEMINI CLIENT SETUP
# ==========================
client = genai.Client(api_key=GEMINI_API_KEY)

grounding_tool = types.Tool(
    google_search=types.GoogleSearch()
)

# Config Search: Cho phép sáng tạo nhẹ để tìm tin đa dạng
config_search = types.GenerateContentConfig(
    tools=[grounding_tool],
    temperature=0.3 
)

# Config JSON: Nhiệt độ thấp để đảm bảo đúng format
config_json = types.GenerateContentConfig(
    response_mime_type="application/json",
    response_schema=VietnamReport,
    temperature=0.1 
)

router = APIRouter(tags=["AI Report"])

# ==========================
# 3. HELPER FUNCTIONS
# ==========================

async def call_gemini_with_retry(contents, config, retries=MAX_RETRIES):
    """
    Hàm wrapper gọi Gemini có cơ chế Retry và Timeout 2s.
    """
    for attempt in range(retries):
        try:
            # Gọi SDK (Sync call wrapped in thread pool if needed, but SDK is fast enough here)
            # Lưu ý: SDK google-genai hiện tại gọi sync, nếu muốn async hoàn toàn cần run_in_executor
            # Tuy nhiên để đơn giản hoá logic retry, ta giữ flow này.
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=contents,
                config=config,
            )
            return response
            
        except exceptions.ResourceExhausted:
            # Lỗi 429 Quota
            if attempt < retries - 1:
                print(f"⚠️ Quota exceeded. Retrying in {RETRY_DELAY_SECONDS}s... (Attempt {attempt+1}/{retries})")
                await asyncio.sleep(RETRY_DELAY_SECONDS) # <--- TIMEOUT 2S THEO YÊU CẦU
            else:
                raise HTTPException(status_code=429, detail="Hệ thống AI đang quá tải, vui lòng thử lại sau.")
        except Exception as e:
            # Các lỗi khác (Mạng, Server...)
            if attempt < retries - 1:
                print(f"⚠️ Error: {e}. Retrying in {RETRY_DELAY_SECONDS}s...")
                await asyncio.sleep(RETRY_DELAY_SECONDS)
            else:
                raise HTTPException(status_code=500, detail=f"AI Error: {str(e)}")

async def geocode_location(lat: float, lon: float) -> str:
    if not (8 <= lat <= 23 and 102 <= lon <= 110):
        raise HTTPException(status_code=400, detail="Tọa độ ngoài lãnh thổ Việt Nam")

    url = "https://api.geoapify.com/v1/geocode/reverse"
    params = {"lat": lat, "lon": lon, "apiKey": GEOAPIFY_KEY, "format": "json"}

    async with httpx.AsyncClient(timeout=10) as client_http:
        try:
            r = await client_http.get(url, params=params)
            r.raise_for_status()
            data = r.json()
            results = data.get("results", [])
            if not results:
                raise HTTPException(status_code=404, detail="Không tìm thấy địa chỉ")
            
            # Ưu tiên lấy tên Thành phố hoặc Tỉnh
            province = results[0].get("state") or results[0].get("city") or results[0].get("county")
            if not province:
                raise HTTPException(status_code=404, detail="Không xác định được tên tỉnh/thành")
            return province
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Geoapify Error: {str(e)}")

async def generate_ai_report(province_name: str) -> VietnamReport:
    """
    Core Logic: Search -> Reason -> JSON Extract
    """
    current_date = datetime.now().strftime("%Y-%m-%d")
    next_3_days = (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d")

    # --- STEP 1: SEARCH PROMPT ---
    search_prompt = f"""
    Hôm nay là: {current_date}.
    Hãy tìm kiếm thông tin mới nhất trên Google cho địa điểm: {province_name}, Việt Nam.
    
    Yêu cầu thông tin cần tìm:
    1. Dự báo thời tiết chi tiết từ {current_date} đến {next_3_days} (Nhiệt độ, Mưa/Nắng).
    2. Các tin tức MỚI NHẤT (trong 7 ngày qua) về: An ninh trật tự, Tai nạn giao thông nghiêm trọng, Dịch bệnh, hoặc Sự kiện văn hóa lớn.
    3. Cảnh báo thiên tai: Bão, Lũ lụt, Sạt lở đất (nếu có).
    
    Chỉ cần trả về nội dung tìm thấy, không cần định dạng đẹp.
    """

    # Gọi AI bước 1
    response_raw = await call_gemini_with_retry(search_prompt, config_search)
    raw_text = response_raw.text

    # --- STEP 2: EXTRACT & SCORING PROMPT ---
    extract_prompt = f"""
    Bạn là chuyên gia đánh giá rủi ro du lịch. Dựa vào DỮ LIỆU THÔ bên dưới, hãy lập báo cáo JSON cho {province_name}.

    QUY ĐỊNH CHẤM ĐIỂM AN TOÀN (SCORE) - BẮT BUỘC TUÂN THỦ:
    - 00 - 30 (NGUY HIỂM - BÁO ĐỘNG ĐỎ): Có thiên tai đang diễn ra (Bão cấp 10+, Lũ quét), Bạo loạn, Dịch bệnh phong tỏa, hoặc Sạt lở nghiêm trọng. -> KHUYẾN CÁO: KHÔNG ĐẾN.
    - 31 - 50 (RỦI RO CAO - BÁO ĐỘNG CAM): Mưa to kéo dài gây ngập úng cục bộ, Ô nhiễm không khí mức nguy hại, Có tin tức về cướp giật/tội phạm gia tăng đột biến.
    - 51 - 70 (CẨN TRỌNG - BÁO ĐỘNG VÀNG): Thời tiết xấu (Mưa rào, Giông lốc nhẹ), Tắc đường nghiêm trọng, Giá cả leo thang mùa lễ hội.
    - 71 - 90 (TỐT - XANH DƯƠNG): Thời tiết ổn định (có thể có mưa nhẹ/mây), Tình hình an ninh bình thường.
    - 91 - 100 (LÝ TƯỞNG - XANH LÁ): Thời tiết đẹp (Nắng ấm/Mát mẻ), Có sự kiện văn hóa hấp dẫn, Không có tin tiêu cực.

    YÊU CẦU VỀ FORMAT DỮ LIỆU:
    1. travel_advice: Không được chép lại tin tức. Phải convert thành hành động. 
       (Ví dụ: Tin "Mưa to" -> Advice: "Mang theo áo mưa và tránh đi đèo dốc").
    2. weather_forecast: Phải đủ 3 ngày.
    3. Nếu không có tin tức tiêu cực, mặc định Score > 80.

    DỮ LIỆU THÔ:
    {raw_text}
    """

    # Gọi AI bước 2
    response_json = await call_gemini_with_retry(extract_prompt, config_json)
    
    if response_json.parsed:
        return response_json.parsed
    else:
        # Fallback manual parsing (phòng trường hợp AI trả về markdown)
        try:
            clean_str = re.sub(r'```json\s*|```', '', response_json.text).strip()
            return VietnamReport.model_validate_json(clean_str)
        except Exception:
            raise ValueError("AI không trả về đúng định dạng JSON.")

# ==========================
# 4. API ENDPOINTS
# ==========================
@router.post("/weather", response_model=VietnamReport)
async def get_weather_report_by_coords(location: LocationRequest):
    province_name = await geocode_location(location.lat, location.long)
    return await generate_ai_report(province_name)

@router.post("/weather_place", response_model=VietnamReport)
async def get_weather_report_by_name(province_name: str):
    return await generate_ai_report(province_name)