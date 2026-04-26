import os
from google import genai
from google.genai import types
from models import (
    Step1Output,
    Step2Output,
    NextQuestionOutput,
    Step4Output,
    Step5Output,
    Step6Output,
    FinalReport,
    DashboardOutput,
)

class LLMService:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is missing.")
        self.client = genai.Client(api_key=api_key)
        self.model_name = "gemini-2.5-flash-lite" # Switched to 2.5-flash-lite as it has a working free tier quota

    def generate_structured(self, prompt: str, system_instruction: str, response_schema):
        config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            response_mime_type="application/json",
            response_schema=response_schema,
            temperature=0.2, # Low temperature for more deterministic output
        )
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config=config,
        )
        return response.text

    def extract_skills(self, prompt: str, system_instruction: str) -> Step1Output:
        result = self.generate_structured(prompt, system_instruction, Step1Output)
        return Step1Output.model_validate_json(result)

    def map_skills(self, prompt: str, system_instruction: str) -> Step2Output:
        result = self.generate_structured(prompt, system_instruction, Step2Output)
        return Step2Output.model_validate_json(result)

    def generate_question(self, prompt: str, system_instruction: str) -> NextQuestionOutput:
        result = self.generate_structured(prompt, system_instruction, NextQuestionOutput)
        return NextQuestionOutput.model_validate_json(result)

    def score_skills(self, prompt: str, system_instruction: str) -> Step4Output:
        result = self.generate_structured(prompt, system_instruction, Step4Output)
        return Step4Output.model_validate_json(result)

    def analyze_gaps(self, prompt: str, system_instruction: str) -> Step5Output:
        result = self.generate_structured(prompt, system_instruction, Step5Output)
        return Step5Output.model_validate_json(result)

    def generate_learning_plan(self, prompt: str, system_instruction: str) -> Step6Output:
        result = self.generate_structured(prompt, system_instruction, Step6Output)
        return Step6Output.model_validate_json(result)

    def generate_final_report(self, prompt: str, system_instruction: str) -> FinalReport:
        result = self.generate_structured(prompt, system_instruction, FinalReport)
        return FinalReport.model_validate_json(result)

    def generate_dashboard_data(self, prompt: str, system_instruction: str) -> DashboardOutput:
        result = self.generate_structured(prompt, system_instruction, DashboardOutput)
        return DashboardOutput.model_validate_json(result)
