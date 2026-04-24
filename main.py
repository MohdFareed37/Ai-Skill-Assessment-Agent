import os
from dotenv import load_dotenv
from agent import Agent

def main():
    print("Welcome to the AI Skill Assessment Agent")
    print("-" * 40)
    
    # Check for API key
    if not os.getenv("GEMINI_API_KEY"):
        api_key = input("Please enter your GEMINI_API_KEY: ").strip()
        if not api_key:
            print("Error: GEMINI_API_KEY is required to proceed.")
            return
        os.environ["GEMINI_API_KEY"] = api_key

    print("\nPlease enter the Job Description (enter 'EOF' on a new line when done):")
    jd_lines = []
    while True:
        line = input()
        if line.strip() == "EOF":
            break
        jd_lines.append(line)
    job_description = "\n".join(jd_lines)

    if not job_description.strip():
        print("Job Description cannot be empty.")
        return

    print("\nPlease enter the Candidate Resume (enter 'EOF' on a new line when done):")
    resume_lines = []
    while True:
        line = input()
        if line.strip() == "EOF":
            break
        resume_lines.append(line)
    candidate_resume = "\n".join(resume_lines)
    
    if not candidate_resume.strip():
        print("Candidate Resume cannot be empty.")
        return

    try:
        agent = Agent(job_description=job_description, candidate_resume=candidate_resume)
        agent.run_pipeline()
    except Exception as e:
        print(f"\nAn error occurred during the assessment: {e}")

if __name__ == "__main__":
    load_dotenv()
    main()
