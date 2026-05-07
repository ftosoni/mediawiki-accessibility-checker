from pydantic import BaseModel, Field
from typing import List, Optional, Any
from enum import Enum

class ExportFormat(str, Enum):
    JSON = "json"
    CSV = "csv"
    WIKITEXT = "wikitext"
    PDF = "pdf"

class AccessibilityRequest(BaseModel):
    url: Optional[str] = Field(None, description="The URL to check for accessibility", examples=["https://it.wikipedia.org/wiki/Ciao"])
    html: Optional[str] = Field(None, description="Raw HTML content to check (use only if URL is not provided)", examples=[None])
    standard: str = Field("wcag22aa", description="The accessibility standard to check against", examples=["wcag22aa"])
    export: Optional[ExportFormat] = Field(None, description="Directly export results to a specific format")

class AxeNode(BaseModel):
    html: str = Field(..., examples=["<img src=\"logo.png\">"])
    target: Any = Field(..., examples=[["img"]])
    failureSummary: Optional[str] = Field(None, examples=["Fix any of the following: Element does not have an alt attribute"])
    impact: Optional[str] = Field(None, examples=["critical"])

class AxeResultItem(BaseModel):
    id: str = Field(..., examples=["image-alt"])
    impact: Optional[str] = Field(None, examples=["critical"])
    tags: List[str] = Field(..., examples=[["cat.text-alternatives", "wcag2a", "wcag111"]])
    description: str = Field(..., examples=["Ensures <img> elements have alternative text"])
    help: str = Field(..., examples=["Images must have alternative text"])
    helpUrl: str = Field(..., examples=["https://dequeuniversity.com/rules/axe/4.9/image-alt"])
    nodes: List[AxeNode]

class AccessibilityResponse(BaseModel):
    url: Optional[str] = Field(..., examples=["https://it.wikipedia.org/wiki/Ciao"])
    title: Optional[str] = Field(None, examples=["Ciao - Wikipedia"])
    timestamp: str = Field(..., examples=["2026-05-07T12:52:39Z"])
    violations: List[AxeResultItem]
    passes: List[AxeResultItem]
    incomplete: List[AxeResultItem]
    inapplicable: List[AxeResultItem]
    summary: dict = Field(..., description="Count of violations, passes, etc.", examples=[{"violations": 5, "passes": 20, "incomplete": 2}])

class ExportRequest(BaseModel):
    results: AccessibilityResponse
    format: ExportFormat = Field(..., examples=["pdf"])
