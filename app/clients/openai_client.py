import json

from openai import OpenAI
from app.clients.interfaces.i_ai_client import IAiClient
from app.core.config import get_settings


class OpenAiClient(IAiClient):
    def __init__(self):
        settings = get_settings()
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL
        self.timeout_seconds = settings.OPENAI_TIMEOUT_SECONDS

    def analyze_forecast_failure(self, payload: dict) -> dict:
        prompt = self._build_prompt(payload)

        response = self.client.responses.create(
            model=self.model,
            input=prompt,
            temperature=0.2,
        )

        text_output = self._extract_text(response)

        try:
            return json.loads(text_output)
        except json.JSONDecodeError:
            return {
                "analysis_summary": "The model response was not in valid JSON. Parsing fallback maintained.",
                "technical_explanation": text_output,
                "business_explanation": None,
                "evidence": [],
                "recommended_actions": payload.get("classifier_result", {}).get(
                    "recommended_actions", []
                ),
                "code_review_targets": [],
                "experiment_suggestions": [],
                "risk_level": "unknown",
            }

    def _build_prompt(self, payload: dict) -> str:
        return f"""
You are a technical analyst specialized in financial asset forecasting systems.

Your role is to interpret deterministic diagnostics generated from forecast evaluations and provide technical, operational, and business-oriented recommendations.

You will receive:
- asset context
- request context
- backtest metrics
- evaluation summary
- deterministic classifier result

Your tasks:
1. explain what the diagnosis means
2. describe the likely technical limitation of the model
3. translate it into business language
4. suggest concrete improvement actions
5. identify code modules that should be reviewed
6. suggest controlled experiments

Rules:
- do not invent bugs without evidence
- do not contradict the deterministic classification unless clearly justified
- if confidence is low, state that explicitly
- always return valid JSON

Required format:
{{
  "analysis_summary": "string",
  "technical_explanation": "string ou null",
  "business_explanation": "string ou null",
  "evidence": ["string"],
  "recommended_actions": ["string"],
  "code_review_targets": ["string"],
  "experiment_suggestions": ["string"],
  "risk_level": "low|medium|high|unknown"
}}

Payload:
{json.dumps(payload, ensure_ascii=False)}
""".strip()

    def _extract_text(self, response) -> str:
        if hasattr(response, "output_text") and response.output_text:
            return response.output_text.strip()

        try:
            return response.output[0].content[0].text.strip()
        except Exception:
            raise ValueError(
                "We were unable to extract the text from OpenAI's response."
            )
