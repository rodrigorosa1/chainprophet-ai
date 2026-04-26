from typing import Literal
from pydantic import BaseModel, Field


class CodeChangeSuggestion(BaseModel):
    file_path: str
    target_symbol: str | None = None
    problem: str
    proposed_change: str
    patch_hint: str | None = None
    risk: Literal["low", "medium", "high"] = "medium"


class ForecastAgentReport(BaseModel):
    analysis_summary: str
    technical_explanation: str
    business_explanation: str | None = None
    root_cause: str
    risk_level: Literal["low", "medium", "high", "critical"]
    evidence: list[str] = Field(default_factory=list)
    recommended_actions: list[str] = Field(default_factory=list)
    code_review_targets: list[CodeChangeSuggestion] = Field(default_factory=list)
    experiment_suggestions: list[str] = Field(default_factory=list)
    should_open_pr: bool = False
