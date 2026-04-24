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

    def run_pipeline(self):
        print("\n--- Starting Skill Assessment Pipeline ---")
        
        print("\n[Step 1] Extracting skills from Job Description...")
        self.step_1_extract_skills()
        
        print("\n[Step 2] Mapping Resume to JD Skills...")
        self.step_2_map_skills()
        
        print("\n[Step 3] Starting Adaptive Assessment...")
        self.step_3_adaptive_assessment()
        
        print("\n[Step 4] Scoring Skills...")
        self.step_4_score_skills()
        
        print("\n[Step 5] Performing Gap Analysis...")
        self.step_5_gap_analysis()
        
        print("\n[Step 6] Generating Personalized Learning Plan...")
        self.step_6_generate_learning_plan()
        
        print("\n[Step 7] Compiling Final Report...")
        report_json = self.step_7_final_report()
        
        print("\n--- FINAL REPORT ---")
        print(report_json)

    def step_1_extract_skills(self):
        prompt = STEP_1_PROMPT.format(job_description=self.job_description)
        result = self.llm.extract_skills(prompt, SYSTEM_PROMPT)
        self.extracted_skills = result.skills
        print("Extracted Skills:")
        print(self.extracted_skills.model_dump_json(indent=2))

    def step_2_map_skills(self):
        prompt = STEP_2_PROMPT.format(
            extracted_skills=self.extracted_skills.model_dump_json(),
            candidate_resume=self.candidate_resume
        )
        result = self.llm.map_skills(prompt, SYSTEM_PROMPT)
        self.skill_mapping = result.skill_mapping
        print("Skill Mapping:")
        print(self.skill_mapping.model_dump_json(indent=2))

    def step_3_adaptive_assessment(self):
        # Assess ONLY core_technical skills based on instructions
        skills_to_assess = self.extracted_skills.core_technical
        
        if not skills_to_assess:
            print("No core technical skills found to assess.")
            return

        for skill in skills_to_assess:
            print(f"\n>> Assessing Skill: {skill}")
            self.assessment_history[skill] = []
            
            # Ask 2-3 questions per skill
            # For simplicity, we ask 2 questions: conceptual/scenario, and maybe advanced
            for i in range(2):
                history_str = json.dumps(self.assessment_history[skill])
                prompt = STEP_3_GENERATE_QUESTION_PROMPT.format(
                    current_skill=skill,
                    conversation_history=history_str
                )
                
                question_data = self.llm.generate_question(prompt, SYSTEM_PROMPT)
                question_text = question_data.question
                
                print(f"\nInterviewer: {question_text}")
                
                # Wait for user input
                while True:
                    user_answer = input("Candidate (or 'skip'): ").strip()
                    if user_answer:
                        break
                    print("Please provide an answer, or type 'skip' to skip this question.")
                
                if user_answer.lower() == 'skip':
                    print("Skipping remaining questions for this skill.")
                    break
                    
                self.assessment_history[skill].append({
                    "question": question_text,
                    "answer": user_answer
                })

    def step_4_score_skills(self):
        prompt = STEP_4_SCORE_SKILLS_PROMPT.format(
            assessment_history=json.dumps(self.assessment_history)
        )
        result = self.llm.score_skills(prompt, SYSTEM_PROMPT)
        self.skill_scores = result.skill_scores
        print("Skill Scores:")
        for score in self.skill_scores:
            print(f"- {score.skill}: {score.score}/5 ({score.strength_level})")

    def step_5_gap_analysis(self):
        prompt = STEP_5_GAP_ANALYSIS_PROMPT.format(
            skill_scores=json.dumps([s.model_dump() for s in self.skill_scores]),
            extracted_skills=self.extracted_skills.model_dump_json()
        )
        result = self.llm.analyze_gaps(prompt, SYSTEM_PROMPT)
        self.gap_analysis = result.gap_analysis
        print("Gap Analysis Results Generated.")

    def step_6_generate_learning_plan(self):
        prompt = STEP_6_LEARNING_PLAN_PROMPT.format(
            critical_gaps=self.gap_analysis.critical_gaps,
            improvement_areas=self.gap_analysis.improvement_areas,
            adjacent_skills=self.gap_analysis.adjacent_skills
        )
        result = self.llm.generate_learning_plan(prompt, SYSTEM_PROMPT)
        self.learning_plan = result.learning_plan
        print("Learning Plan Generated.")

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
