from pydantic import BaseModel, Field
from typing import List

# Step 1: Skill Extraction
class SkillsExtracted(BaseModel):
    core_technical: List[str] = Field(default_factory=list)
    secondary: List[str] = Field(default_factory=list)
    tools_technologies: List[str] = Field(default_factory=list)
    soft_skills: List[str] = Field(default_factory=list)

class Step1Output(BaseModel):
    skills: SkillsExtracted

# Step 2: Skill Mapping
class SkillMapping(BaseModel):
    matched_skills: List[str] = Field(default_factory=list)
    partial_skills: List[str] = Field(default_factory=list)
    missing_skills: List[str] = Field(default_factory=list)

class Step2Output(BaseModel):
    skill_mapping: SkillMapping

# Step 3: Adaptive Assessment (Questions)
class NextQuestionOutput(BaseModel):
    question: str
    is_advanced: bool

# Step 4: Skill Scoring
class SkillScore(BaseModel):
    skill: str
    score: int = Field(ge=0, le=5)
    strength_level: str = Field(description="Beginner | Basic | Intermediate | Advanced | Expert")
    evidence: str

class Step4Output(BaseModel):
    skill_scores: List[SkillScore]

# Step 5: Gap Analysis
class GapAnalysis(BaseModel):
    critical_gaps: List[str] = Field(default_factory=list)
    improvement_areas: List[str] = Field(default_factory=list)
    strong_areas: List[str] = Field(default_factory=list)
    adjacent_skills: List[str] = Field(default_factory=list)

class Step5Output(BaseModel):
    gap_analysis: GapAnalysis

# Step 6: Learning Plan
class LearningPlanItem(BaseModel):
    skill: str
    priority: str = Field(description="High | Medium | Low")
    why_it_matters: str
    what_to_learn: List[str] = Field(default_factory=list)
    resources: List[str] = Field(default_factory=list)
    time_estimate: str
    expected_outcome: str

class Step6Output(BaseModel):
    learning_plan: List[LearningPlanItem]

# Step 7: Final Report
class FinalReport(BaseModel):
    candidate_summary: str
    skills_extracted: SkillsExtracted
    skill_mapping: SkillMapping
    assessment_results: List[SkillScore]
    gap_analysis: GapAnalysis
    learning_plan: List[LearningPlanItem]
    estimated_total_time: str
    job_readiness_score: str
    final_recommendation: str = Field(description="Hire | Trainable | Not Ready")
