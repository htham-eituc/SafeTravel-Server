# ai_route.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
import httpx
from google import genai
from google.genai import types

from dotenv import load_dotenv
import os

load_dotenv()
GEOAPIFY_KEY = os.getenv("GEOAPIFY_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


# ==========================
# Pydantic Models
# ==========================
class WeatherInfo(BaseModel):
    date: str
    temperature: str
    condition: str

class NewsItem(BaseModel):
    date: str
    title: str
    snippet: str

class ProvinceData(BaseModel):
    province_name: str
    weather_forecast: List[WeatherInfo]
    recent_news: List[NewsItem]
    executive_summary: str
    sources: List[str]
    score: Optional[int] = Field(
        None, description="Điểm an toàn 0-100. Thấp nếu thiên tai/tội phạm."
    )

class VietnamReport(BaseModel):
    provinces: List[ProvinceData]

class LocationRequest(BaseModel):
    lat: float = Field(..., description="Latitude")
    long: float = Field(..., description="Longitude")

# ========================== 
# Google Gemini config
# ==========================
client = genai.Client(api_key=GEMINI_API_KEY)

grounding_tool = types.Tool(
    google_search=types.GoogleSearch()
)

config_search = types.GenerateContentConfig(
    tools=[grounding_tool]
)

config_json = types.GenerateContentConfig(
    response_mime_type="application/json",
    response_json_schema=VietnamReport.model_json_schema(),
    temperature=0.1
)

# ==========================
# Router setup
# ==========================
router = APIRouter(prefix="/api", tags=["AI Report"])


async def geocode_location(lat: float, lon: float) -> str:
    if not (8 <= lat <= 23 and 102 <= lon <= 110):
        raise HTTPException(status_code=400, detail="Tọa độ ngoài lãnh thổ Việt Nam")

    url = "https://api.geoapify.com/v1/geocode/reverse"
    params = {
        "lat": lat,
        "lon": lon,
        "apiKey": GEOAPIFY_KEY,
        "format": "json"
    }

    async with httpx.AsyncClient(timeout=5) as client:
        try:
            r = await client.get(url, params=params)
            r.raise_for_status()
            data = r.json()
            # Lấy tên tỉnh/thành phố
            results = data.get("results", [])
            if not results:
                raise HTTPException(status_code=404, detail="Không tìm thấy địa chỉ")
            # Tìm trường "state" hoặc fallback "county"
            province = results[0].get("state") or results[0].get("county")
            if not province:
                raise HTTPException(status_code=404, detail="Không tìm thấy tỉnh/thành phố")
            return province
        except httpx.RequestError as e:
            raise HTTPException(status_code=500, detail=f"Lỗi kết nối Geoapify: {e}")

# --------------------------
# API route
# --------------------------
@router.post("/weather", response_model=VietnamReport)
async def get_weather_report(location: LocationRequest):

    province_name = await geocode_location(location.lat, location.long)

    prompt = f"""
    Hãy tạo báo cáo thời tiết và tin tức cho tỉnh/thành phố: {province_name}

    Bước thực hiện:
    1. Tìm dự báo thời tiết 3 ngày tới.
    2. Tìm 3 tin tức quan trọng trong 3 ngày gần đây.
    3. Tổng hợp thành đoạn văn ngắn.
    4. Liệt kê các nguồn URL.
    5. Đánh giá mức độ an toàn/thích hợp du lịch, trả về `score` trên 0-100
       - 0-50: nguy hiểm, thiên tai, tội phạm
       - 51-70: cảnh báo vàng
       - 71-100: an toàn
       
    Trình bày kết quả đúng JSON schema:
    - weather_forecast, recent_news, executive_summary, sources, score
    """

    try:
        # Step 1: AI tìm kiếm raw content
        response_raw = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=config_search,
        )
        raw_text = response_raw.text

        # Step 2: Trích xuất JSON + score
        prompt_extract = f"""
        Dựa vào văn bản dưới đây, trích xuất thành JSON chuẩn cho tỉnh {province_name}.
        Nếu thiếu thông tin, để trống hoặc ghi "Không có dữ liệu".
        Vui lòng trả luôn `score` đánh giá an toàn du lịch.

        VĂN BẢN NGUỒN:
        {raw_text}
        """

        response_json = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt_extract,
            config=config_json,
        )

        if not response_json.parsed:
            raise HTTPException(status_code=400, detail="Không trích xuất được JSON từ AI")

        return response_json.parsed

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/weather_place", response_model=VietnamReport)
async def get_weather_report(province_name: str):

    prompt = f"""
    Hãy tạo báo cáo thời tiết và tin tức cho tỉnh/thành phố: {province_name}

    Bước thực hiện:
    1. Tìm dự báo thời tiết 3 ngày tới.
    2. Tìm 3 tin tức quan trọng trong 3 ngày gần đây.
    3. Tổng hợp thành đoạn văn ngắn.
    4. Liệt kê các nguồn URL.
    5. Đánh giá mức độ an toàn/thích hợp du lịch, trả về `score` trên 0-100
       - 0-50: nguy hiểm, thiên tai, tội phạm
       - 51-70: cảnh báo vàng
       - 71-100: an toàn
       
    Trình bày kết quả đúng JSON schema:
    - weather_forecast, recent_news, executive_summary, sources, score
    """

    try:
        # Step 1: AI tìm kiếm raw content
        response_raw = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=config_search,
        )
        raw_text = response_raw.text

        # Step 2: Trích xuất JSON + score
        prompt_extract = f"""
        Dựa vào văn bản dưới đây, trích xuất thành JSON chuẩn cho tỉnh {province_name}.
        Nếu thiếu thông tin, để trống hoặc ghi "Không có dữ liệu".
        Vui lòng trả luôn `score` đánh giá an toàn du lịch.

        VĂN BẢN NGUỒN:
        {raw_text}
        """

        response_json = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt_extract,
            config=config_json,
        )

        if not response_json.parsed:
            raise HTTPException(status_code=400, detail="Không trích xuất được JSON từ AI")

        return response_json.parsed

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))