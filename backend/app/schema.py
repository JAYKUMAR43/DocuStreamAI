from pydantic import BaseModel, Field
from typing import Optional, List

class LogMetrics(BaseModel):
    timestamp: str = Field(..., description="UTC ISO timestamp of the log")
    severity_level: str = Field(..., description="Classification of severity: INFO, WARNING, ERROR, or CRITICAL")
    service_name: str = Field(..., description="The name of the service that emitted the log")
    root_cause: str = Field(..., description="A concise diagnostic analysis explaining the primary trigger")
    severity_score: float = Field(..., description="A quantitative assessment of severity from 0.0 to 10.0")
    alert_triggered: bool = Field(..., description="True if alert is triggered")
    data_type: Optional[str] = Field("OTHER", description="Detected raw data type (LOG/CONFIG/PDF/CSV/CODE/IMAGE/JSON/OTHER)")
    extraction_layer: str = Field("Pydantic-JSON-Mode (Zero-Regex Schema Validation: PASSED)", description="Extraction layer validation label")

class LogIngestRequest(BaseModel):
    raw_log: str = Field(..., description="The raw system log stack trace or string")
    data_type: Optional[str] = Field("OTHER", description="Optionally provided data type from frontend")
    destination: Optional[str] = Field("postgresql", description="Optionally provided target destination")

class RouteRequest(BaseModel):
    destination: str = Field(..., description="Target routing system: postgresql, chromadb, or export")
    log_data: LogMetrics = Field(..., description="Structured schema payload extracted by Gemini")
    raw_log: Optional[str] = Field("", description="Raw log text source")

class SearchRequest(BaseModel):
    query: str = Field(..., description="Natural language search query")

class SearchResultItem(BaseModel):
    id: int
    raw_log: str
    timestamp: str
    severity_level: str
    service_name: str
    root_cause: str
    severity_score: float
    similarity: float

class SearchResponse(BaseModel):
    query: str
    results: List[SearchResultItem]
