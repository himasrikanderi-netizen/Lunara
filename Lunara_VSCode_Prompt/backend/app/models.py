from datetime import datetime, timezone
from enum import StrEnum
from typing import Literal
from pydantic import BaseModel, Field, field_validator

class Category(StrEnum):
    stalking="stalking"; harassment="harassment"; suspicious_following="suspicious_following"
    verbal_harassment="verbal_harassment"; unsafe_transport_location="unsafe_transport_location"
    poor_lighting="poor_lighting"; isolated_road="isolated_road"; suspicious_activity="suspicious_activity"
    infrastructure_problem="infrastructure_problem"; other_safety_concern="other_safety_concern"
class Coordinate(BaseModel):
    lat: float = Field(ge=-90, le=90); lng: float = Field(ge=-180, le=180)
class TravelMode(StrEnum):
    walking="walking"; driving="driving"; cycling="cycling"
    rapido_bike="rapido_bike"; rapido_auto="rapido_auto"; rapido_cab="rapido_cab"

    @property
    def routing_profile(self) -> "TravelMode":
        return TravelMode.driving if self.value.startswith("rapido_") else self

    @property
    def is_rapido(self) -> bool:
        return self.value.startswith("rapido_")
class RouteSearch(BaseModel):
    origin: str = Field(min_length=2,max_length=160); destination: str = Field(min_length=2,max_length=160)
    departure_time: datetime; preference: int = Field(50,ge=0,le=100); travel_mode: TravelMode = TravelMode.driving; preferences:list[str]=Field(default_factory=list,max_length=10)
    @field_validator("departure_time")
    @classmethod
    def timezone_required(cls,v:datetime)->datetime:
        if v.tzinfo is None: raise ValueError("departure_time must include a timezone")
        return v
class RiskSegment(BaseModel):
    from_: Coordinate = Field(alias="from"); to: Coordinate; level: str
    model_config={"populate_by_name":True}
class RouteOption(BaseModel):
    id:str; label:str; duration_minutes:int; distance_km:float; safety_score:int=Field(ge=0,le=100)
    confidence_score:int=Field(ge=0,le=100); confidence_label:str; summary:str; factors:list[str]
    geometry:list[Coordinate]; risk_segments:list[RiskSegment]
    geometry_source:str="OpenStreetMap via OSRM"
    travel_mode: TravelMode = TravelMode.driving
    routing_profile: Literal["walking", "driving", "cycling"] = "driving"
    resolved_origin: Coordinate | None = None
    resolved_destination: Coordinate | None = None
    traffic_included: bool = False
    data_sources:list[str]=Field(default_factory=list)
    unavailable_factors:list[str]=Field(default_factory=list)
class ReportCreate(BaseModel):
    category:Category; severity:int=Field(ge=1,le=5); description:str|None=Field(None,max_length=500)
    latitude:float=Field(ge=-90,le=90); longitude:float=Field(ge=-180,le=180); occurred_at:datetime
class Report(ReportCreate):
    id:str; status:str="pending"; reliability_score:int=35; created_at:datetime=Field(default_factory=lambda:datetime.now(timezone.utc))
class VerificationCreate(BaseModel):
    verdict:str
    @field_validator("verdict")
    @classmethod
    def valid_verdict(cls,v:str)->str:
        if v not in {"still_relevant","no_longer_present","duplicate_inaccurate"}: raise ValueError("invalid verdict")
        return v
class JourneyCreate(BaseModel):
    route_id:str; expected_arrival:datetime; share_with_contacts:bool=False
class SafePlace(BaseModel):
    id: str; category: Literal["hospital","police","transport"]; name: str
    location: Coordinate; distance_m: int; osm_url: str
class SafePlaceResults(BaseModel):
    places: list[SafePlace]; data_status: str; source: str = "OpenStreetMap via Overpass"
