from pydantic import BaseModel, Field
from typing import List, Optional, Any

class AccessibilityRequest(BaseModel):
    url: Optional[str] = Field(None, description="The URL to check for accessibility")
    html: Optional[str] = Field(None, description="Raw HTML content to check")
    standard: str = Field("wcag22aa", description="The accessibility standard to check against")
    view_source: bool = Field(False, description="Whether to include source code in results")

class AxeNode(BaseModel):
    html: str
    target: Any
    failureSummary: Optional[str] = None
    impact: Optional[str] = None

class AxeResultItem(BaseModel):
    id: str
    impact: Optional[str]
    tags: List[str]
    description: str
    help: str
    helpUrl: str
    nodes: List[AxeNode]

class AccessibilityResponse(BaseModel):
    url: Optional[str]
    timestamp: str
    violations: List[AxeResultItem]
    passes: List[AxeResultItem]
    incomplete: List[AxeResultItem]
    inapplicable: List[AxeResultItem]
    summary: dict = Field(..., description="Count of violations, passes, etc.")
