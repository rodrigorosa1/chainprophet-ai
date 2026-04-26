from langchain.tools import tool


CODEBASE_CONTEXT = {
    "app/services/forecast_service.py": """
Main forecast generation service.
Important methods:
- _get_model_config
- _build_prophet_model
- _calculate_confidence
- _calculate_dynamic_range_percent
- _forecast_single_asset
- forecast_prices
- save_forecast_response
""",
    "app/services/forecast_failure_classifier_service.py": """
Deterministic classifier for forecast failure diagnostics.
Important methods:
- classify_pending_assets
- _classify_asset
""",
    "app/services/forecast_evaluation_service.py": """
Evaluates forecast points after actual price is collected.
Important methods:
- evaluate_pending_points
- _evaluate_point
- _get_direction
- _resolve_reference_price
""",
    "app/services/forecast_llm_analyst_service.py": """
Current LLM analyst service.
Will be replaced/evolved with LangChain agent.
""",
}


@tool
def list_forecast_code_targets() -> dict:
    """List known forecast-related code files and their responsibilities."""
    return CODEBASE_CONTEXT


@tool
def get_forecast_code_context(file_path: str) -> str:
    """Return summarized context for a known forecast code file."""
    return CODEBASE_CONTEXT.get(file_path, "Unknown file_path.")
