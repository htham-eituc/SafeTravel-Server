from __future__ import annotations

from datetime import datetime, timedelta
from typing import List, Optional
import os

import httpx
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field, HttpUrl

from src.application.news_incident.dto import NewsIncidentInDB
from src.domain.news_incident.entities import NewsIncident as NewsIncidentEntity
from src.domain.news_incident.repository_interface import INewsIncidentRepository


class ExtractedIncident(BaseModel):
    title: str
    summary: Optional[str] = None
    category: Optional[str] = Field(
        None, description="crime, disaster, accident, epidemic, protest, fire, flood, storm, etc"
    )
    location_name: str = Field(..., description="Human-readable location, e.g. 'Quận 1, TP.HCM'")
    source_url: HttpUrl
    published_at: Optional[datetime] = None
    severity: Optional[int] = Field(None, ge=0, le=100)


class ExtractedIncidentsReport(BaseModel):
    incidents: List[ExtractedIncident]


class NewsIncidentUseCases:
    def __init__(self, repo: INewsIncidentRepository):
        self.repo = repo

    def get_news_incidents_within_radius(
        self,
        db: Session,
        latitude: float,
        longitude: float,
        radius: float = 0.5
    ) -> List[NewsIncidentInDB]:
        if radius <= 0:
            raise ValueError("Radius must be greater than 0.")
        incidents = self.repo.get_within_radius(db, latitude, longitude, radius)
        return [NewsIncidentInDB.model_validate(i.model_dump()) for i in incidents]

    def extract_and_store(
        self,
        db: Session,
        query: str,
        days: int = 3,
        max_items: int = 20
    ) -> List[NewsIncidentInDB]:
        geoapify_key = os.getenv("GEOAPIFY_KEY")
        gemini_key = os.getenv("GEMINI_API_KEY")
        if not geoapify_key:
            raise ValueError("Missing GEOAPIFY_KEY in environment.")
        if not gemini_key:
            raise ValueError("Missing GEMINI_API_KEY in environment.")

        report = self._extract_incidents_via_gemini(query=query, days=days, max_items=max_items, api_key=gemini_key)

        stored: List[NewsIncidentInDB] = []
        for incident in report.incidents:
            coords = self._geocode_location(incident.location_name, geoapify_key=geoapify_key)
            if not coords:
                continue
            lat, lon = coords
            entity = NewsIncidentEntity(
                title=incident.title,
                summary=incident.summary,
                category=incident.category,
                location_name=incident.location_name,
                latitude=lat,
                longitude=lon,
                source_url=str(incident.source_url),
                published_at=incident.published_at,
                severity=incident.severity,
            )
            saved = self.repo.upsert_by_source_url(db, entity)
            stored.append(NewsIncidentInDB.model_validate(saved.model_dump()))

        return stored

    def _geocode_location(self, location_name: str, geoapify_key: str) -> Optional[tuple[float, float]]:
        url = "https://api.geoapify.com/v1/geocode/search"
        params = {
            "text": location_name,
            "format": "json",
            "apiKey": geoapify_key,
            "limit": 1,
        }
        with httpx.Client(timeout=8) as client:
            r = client.get(url, params=params)
            r.raise_for_status()
            data = r.json()
            results = data.get("results") or []
            if not results:
                return None
            return float(results[0]["lat"]), float(results[0]["lon"])

    def _extract_incidents_via_gemini(self, query: str, days: int, max_items: int, api_key: str) -> ExtractedIncidentsReport:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=api_key)

        grounding_tool = types.Tool(google_search=types.GoogleSearch())
        config_search = types.GenerateContentConfig(tools=[grounding_tool])
        config_json = types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=ExtractedIncidentsReport,
            temperature=0.1,
        )

        since = (datetime.utcnow() - timedelta(days=days)).date().isoformat()

        prompt_search = f"""
        Find recent negative safety-related incidents for travel warning context in: {query}
        Time window: from {since} to today.

        Focus on: crime, robbery, assault, kidnapping, scams, accidents, fires, floods, storms, landslides,
        epidemics, food poisoning, riots/protests, terrorism, infrastructure failures.

        Return a short bullet list with: title, location (district/province/city), date, and source URL.
        """

        response_raw = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt_search,
            config=config_search,
        )

        prompt_extract = f"""
        Convert the text below into JSON matching the schema `ExtractedIncidentsReport`.
        Rules:
        - `incidents` length <= {max_items}
        - `location_name` must be a usable place name for geocoding (include city/province if possible)
        - `source_url` must be a direct URL
        - `published_at` should be ISO8601 if available, otherwise null
        - `severity` 0-100 (higher = worse), otherwise null

        TEXT:
        {response_raw.text}
        """

        response_json = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt_extract,
            config=config_json,
        )

        if not response_json.parsed:
            raise ValueError("AI extraction failed to produce structured output.")
        return response_json.parsed

