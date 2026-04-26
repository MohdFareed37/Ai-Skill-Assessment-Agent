import json
from llm_service import LLMService
from prompts import (
    SYSTEM_PROMPT,
    STEP_1_PROMPT,
    STEP_2_PROMPT,
    STEP_3_GENERATE_QUESTION_PROMPT,
    STEP_4_SCORE_SKILLS_PROMPT,
    STEP_5_GAP_ANALYSIS_PROMPT,
    STEP_6_LEARNING_PLAN_PROMPT,
    STEP_7_FINAL_REPORT_PROMPT,
    GENERATE_DASHBOARD_PROMPT,
)

class Agent:
    def __init__(self, job_description: str, candidate_resume: str):
        self.llm = LLMService()
        self.job_description = job_description
        self.candidate_resume = candidate_resume
        
        # State
        self.extracted_skills = None
        self.skill_mapping = None
        self.assessment_history = {} # skill -> list of dicts {"question": ..., "answer": ...}
        self.skill_scores = None
        self.gap_analysis = None
        self.learning_plan = None

    def step_1_extract_skills(self):
        prompt = STEP_1_PROMPT.format(job_description=self.job_description)
        result = self.llm.extract_skills(prompt, SYSTEM_PROMPT)
        self.extracted_skills = result.skills
        return self.extracted_skills

    def step_2_map_skills(self):
        prompt = STEP_2_PROMPT.format(
            extracted_skills=self.extracted_skills.model_dump_json(),
            candidate_resume=self.candidate_resume
        )
        result = self.llm.map_skills(prompt, SYSTEM_PROMPT)
        self.skill_mapping = result.skill_mapping
        return self.skill_mapping

    def get_skills_to_assess(self):
        if not self.extracted_skills:
            return []
        return self.extracted_skills.core_technical

    def generate_next_question(self, skill: str) -> str:
        if skill not in self.assessment_history:
            self.assessment_history[skill] = []
            
        history_str = json.dumps(self.assessment_history[skill])
        prompt = STEP_3_GENERATE_QUESTION_PROMPT.format(
            current_skill=skill,
            conversation_history=history_str
        )
        question_data = self.llm.generate_question(prompt, SYSTEM_PROMPT)
        return question_data.question

    def submit_answer(self, skill: str, question: str, answer: str):
        if skill not in self.assessment_history:
            self.assessment_history[skill] = []
        self.assessment_history[skill].append({
            "question": question,
            "answer": answer
        })

    def step_4_score_skills(self):
        prompt = STEP_4_SCORE_SKILLS_PROMPT.format(
            assessment_history=json.dumps(self.assessment_history)
        )
        result = self.llm.score_skills(prompt, SYSTEM_PROMPT)
        self.skill_scores = result.skill_scores
        return self.skill_scores

    def step_5_gap_analysis(self):
        prompt = STEP_5_GAP_ANALYSIS_PROMPT.format(
            skill_scores=json.dumps([s.model_dump() for s in self.skill_scores]),
            extracted_skills=self.extracted_skills.model_dump_json()
        )
        result = self.llm.analyze_gaps(prompt, SYSTEM_PROMPT)
        self.gap_analysis = result.gap_analysis
        return self.gap_analysis

    def step_6_generate_learning_plan(self):
        prompt = STEP_6_LEARNING_PLAN_PROMPT.format(
            critical_gaps=self.gap_analysis.critical_gaps,
            improvement_areas=self.gap_analysis.improvement_areas,
            adjacent_skills=self.gap_analysis.adjacent_skills
        )
        result = self.llm.generate_learning_plan(prompt, SYSTEM_PROMPT)
        self.learning_plan = result.learning_plan
        return self.learning_plan

    def step_7_final_report(self) -> str:
        prompt = STEP_7_FINAL_REPORT_PROMPT.format(
            job_description=self.job_description,
            candidate_resume=self.candidate_resume,
            skills_extracted=self.extracted_skills.model_dump_json(),
            skill_mapping=self.skill_mapping.model_dump_json(),
            skill_scores=json.dumps([s.model_dump() for s in self.skill_scores]),
            gap_analysis=self.gap_analysis.model_dump_json(),
            learning_plan=json.dumps([lp.model_dump() for lp in self.learning_plan])
        )
        result = self.llm.generate_final_report(prompt, SYSTEM_PROMPT)
        return result.model_dump_json(indent=2)

    def generate_unified_dashboard(self):
        prompt = GENERATE_DASHBOARD_PROMPT.format(
            extracted_skills=self.extracted_skills.model_dump_json(),
            assessment_history=json.dumps(self.assessment_history)
        )
        dashboard_data = self.llm.generate_dashboard_data(prompt, SYSTEM_PROMPT)
        
        # Populate the state variables so the UI can render them
        self.skill_scores = dashboard_data.skill_scores
        self.gap_analysis = dashboard_data.gap_analysis
        self.learning_plan = dashboard_data.learning_plan
        
        # Return the raw JSON dump as the final report
        return dashboard_data.model_dump_json(indent=2)
