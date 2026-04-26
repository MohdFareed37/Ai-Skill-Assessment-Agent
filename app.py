import streamlit as st
import os
from dotenv import load_dotenv
from agent import Agent
import pandas as pd

# Load environment variables
load_dotenv()

# --- Page Configuration ---
st.set_page_config(
    page_title="AI Skill Assessment Agent",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS ---
st.markdown("""
<style>
.skill-tag {
    display: inline-block;
    padding: 0.3em 0.8em;
    margin: 0.2em;
    border-radius: 15px;
    background-color: #2e3b4e;
    color: white;
    font-size: 0.9em;
}
.score-badge {
    padding: 0.4em 0.8em;
    border-radius: 5px;
    font-weight: bold;
    color: white;
    display: inline-block;
    width: 100px;
    text-align: center;
}
.bg-red { background-color: #ff4b4b; }
.bg-yellow { background-color: #fca311; }
.bg-green { background-color: #00cc66; }
</style>
""", unsafe_allow_html=True)

# --- State Management ---
if 'phase' not in st.session_state:
    st.session_state.phase = 'input'
if 'agent' not in st.session_state:
    st.session_state.agent = None
if 'current_skill_idx' not in st.session_state:
    st.session_state.current_skill_idx = 0
if 'questions_asked' not in st.session_state:
    st.session_state.questions_asked = 0
if 'current_question' not in st.session_state:
    st.session_state.current_question = None
if 'messages' not in st.session_state:
    st.session_state.messages = [] # For rendering chat UI

def reset_app():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.session_state.phase = 'input'

# --- API Key Check ---
if not os.getenv("GEMINI_API_KEY"):
    st.error("Missing GEMINI_API_KEY! Please add it to your .env file.")
    st.stop()

# --- Sidebar ---
with st.sidebar:
    st.title("🎓 AI Assessor")
    st.markdown("Assess skills interactively and generate a personalized learning plan.")
    if st.session_state.phase != 'input':
        if st.button("Start Over", on_click=reset_app):
            pass

# --- PHASE 1: INPUT ---
if st.session_state.phase == 'input':
    st.header("Upload Candidate Information")
    
    col1, col2 = st.columns(2)
    with col1:
        job_description = st.text_area("Job Description (JD)", height=300, placeholder="Paste the job description here...")
    with col2:
        candidate_resume = st.text_area("Candidate Resume", height=300, placeholder="Paste the candidate's resume here...")
    
    if st.button("Start Assessment", type="primary", use_container_width=True):
        if job_description and candidate_resume:
            st.session_state.agent = Agent(job_description, candidate_resume)
            st.session_state.phase = 'extract'
            st.rerun()
        else:
            st.warning("Please provide both Job Description and Resume.")

# --- PHASE 2: EXTRACTION ---
elif st.session_state.phase == 'extract':
    with st.spinner("Analyzing Resume and Job Description..."):
        try:
            agent = st.session_state.agent
            
            # Run Step 1
            extracted = agent.step_1_extract_skills()
            # Run Step 2
            mapping = agent.step_2_map_skills()
            
            st.session_state.phase = 'chat_init'
            st.rerun()
        except Exception as e:
            st.error(f"An API error occurred: {e}")
            if st.button("Go Back"):
                reset_app()
                st.rerun()

# --- PHASE 3: INTERVIEW (CHAT) ---
elif st.session_state.phase.startswith('chat'):
    agent = st.session_state.agent
    skills_to_assess = agent.get_skills_to_assess()
    
    if not skills_to_assess:
        st.warning("No core technical skills extracted to assess.")
        st.session_state.phase = 'dashboard'
        st.rerun()
        
    idx = st.session_state.current_skill_idx
    
    if idx >= len(skills_to_assess):
        # All skills assessed!
        st.session_state.phase = 'dashboard'
        st.rerun()

    # --- Display Extracted Skills as Tags ---
    st.subheader("🎯 Identified Skills")
    skills_html = ""
    for s in agent.extracted_skills.core_technical:
        skills_html += f"<span class='skill-tag'>{s}</span>"
    for s in agent.extracted_skills.tools_technologies:
        skills_html += f"<span class='skill-tag' style='background-color:#4a5568;'>{s}</span>"
    st.markdown(skills_html, unsafe_allow_html=True)
    st.divider()
        
    current_skill = skills_to_assess[idx]

    
    # UI Header for Chat
    st.header(f"Live Interview")
    st.info(f"**Currently Assessing:** {current_skill} (Skill {idx+1} of {len(skills_to_assess)})")
    
    # Initialize chat for current skill
    if st.session_state.phase == 'chat_init':
        st.session_state.questions_asked = 0
        st.session_state.messages = []
        with st.spinner("Generating question..."):
            try:
                q = agent.generate_next_question(current_skill)
                st.session_state.current_question = q
                st.session_state.messages.append({"role": "assistant", "content": q})
                st.session_state.phase = 'chat_active'
                st.rerun()
            except Exception as e:
                st.error(f"Failed to generate question: {e}")

    # Render Chat History
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            
    # Chat Input
    if prompt := st.chat_input("Type your answer here..."):
        # Display user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
            
        # Submit to agent
        agent.submit_answer(current_skill, st.session_state.current_question, prompt)
        st.session_state.questions_asked += 1
        
        # Check if we move to next skill (after 2 questions)
        if st.session_state.questions_asked >= 2:
            st.session_state.current_skill_idx += 1
            st.session_state.phase = 'chat_init'
            st.rerun()
        else:
            # Generate next question for same skill
            with st.spinner("Evaluating and generating next question..."):
                try:
                    q = agent.generate_next_question(current_skill)
                    st.session_state.current_question = q
                    st.session_state.messages.append({"role": "assistant", "content": q})
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to generate next question: {e}")

# --- PHASE 4: DASHBOARD ---
elif st.session_state.phase == 'dashboard':
    agent = st.session_state.agent
    
    if not agent.skill_scores:
        with st.spinner("Scoring skills and generating learning plan..."):
            try:
                agent.step_4_score_skills()
                agent.step_5_gap_analysis()
                agent.step_6_generate_learning_plan()
                agent.step_7_final_report() # Generates JSON report internally
            except Exception as e:
                st.error(f"Error generating dashboard: {e}")
                st.stop()
    
    st.header("📊 Assessment Dashboard")
    
    # -- Skills & Scores --
    st.subheader("Skill Proficiency")
    for score_obj in agent.skill_scores:
        skill = score_obj.skill
        score = score_obj.score
        pct = (score / 5) * 100
        
        color_class = "bg-green" if score >= 4 else ("bg-yellow" if score == 3 else "bg-red")
        
        col1, col2, col3 = st.columns([2, 6, 2])
        with col1:
            st.markdown(f"**{skill}**")
        with col2:
            st.progress(int(pct), text=f"Level: {score_obj.strength_level}")
        with col3:
            st.markdown(f"<div class='score-badge {color_class}'>{score}/5</div>", unsafe_allow_html=True)
            
        with st.expander("View Evaluation Evidence"):
            st.write(score_obj.evidence)
    
    st.divider()
    
    # -- Gap Analysis --
    st.subheader("Gap Analysis")
    col1, col2 = st.columns(2)
    with col1:
        st.error("**Critical Gaps**")
        for g in agent.gap_analysis.critical_gaps:
            st.markdown(f"- {g}")
    with col2:
        st.warning("**Improvement Areas**")
        for g in agent.gap_analysis.improvement_areas:
            st.markdown(f"- {g}")
            
    st.divider()
    
    # -- Learning Plan --
    st.subheader("Personalized Learning Plan")
    for item in agent.learning_plan:
        with st.container(border=True):
            st.markdown(f"### {item.skill}")
            st.markdown(f"**Priority:** {item.priority} | **Time Estimate:** {item.time_estimate}")
            st.markdown(f"**Why it matters:** {item.why_it_matters}")
            
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("**What to learn:**")
                for t in item.what_to_learn:
                    st.markdown(f"- {t}")
            with c2:
                st.markdown("**Resources:**")
                for r in item.resources:
                    st.markdown(f"- {r}")
            st.info(f"**Expected Outcome:** {item.expected_outcome}")

    # -- Download Report --
    st.divider()
    report_json = agent.step_7_final_report()
    st.download_button(
        label="📄 Download Full JSON Report",
        data=report_json,
        file_name="assessment_report.json",
        mime="application/json",
        type="primary"
    )
