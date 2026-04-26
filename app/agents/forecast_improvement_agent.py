from langchain.agents import create_agent
from langchain_openai import ChatOpenAI

from app.agents.prompts.forecast_improvement_prompt import FORECAST_AGENT_SYSTEM_PROMPT
from app.schemas.forecast_agent_schema import ForecastAgentReport
from app.agents.tools.codebase_tools import (
    list_forecast_code_targets,
    get_forecast_code_context,
)


class ForecastImprovementAgent:
    def __init__(self):
        model = ChatOpenAI(
            model="gpt-4.1-mini",
            temperature=0.1,
            timeout=60,
        )

        self.agent = create_agent(
            model=model,
            tools=[
                list_forecast_code_targets,
                get_forecast_code_context,
            ],
            system_prompt=FORECAST_AGENT_SYSTEM_PROMPT,
            response_format=ForecastAgentReport,
        )

    def analyze(self, payload: dict) -> ForecastAgentReport:
        result = self.agent.invoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": (
                            "Analyze this forecast failure diagnostic and return "
                            "a structured improvement report:\n\n"
                            f"{payload}"
                        ),
                    }
                ]
            }
        )

        return result["structured_response"]
