# AI Skill Assessment Agent

This is an AI Skill Assessment & Personalized Learning Plan Agent built for evaluating candidates against a Job Description (JD). It uses an adaptive multi-turn questioning process, quantifies proficiency, identifies precise skill gaps, and generates a realistic, time-bound learning plan with curated resources.

## Features
- **Skill Extraction**: Automatically extracts and normalizes skills from a Job Description.
- **Skill Mapping**: Maps the candidate's resume against the extracted skills to identify matches and gaps.
- **Adaptive Assessment**: Conducts a multi-turn terminal-based interview, dynamically adjusting question difficulty based on the candidate's responses.
- **Skill Scoring**: Scores candidate skills on a 0-5 scale.
- **Gap Analysis & Learning Plan**: Generates a detailed gap analysis and a personalized learning plan based on the assessment results.

## Requirements
- Python 3.8+
- A Google Gemini API Key

## Setup & Installation (For Hackathon Judges)

Follow these steps to set up and run the agent locally.

1. **Clone the repository**
   ```bash
   git clone https://github.com/MohdFareed37/Ai-Skill-Assessment-Agent.git
   cd Ai-Skill-Assessment-Agent
   ```

2. **Install Dependencies**
   It's highly recommended to use a virtual environment.
   ```bash
   pip install -r requirements.txt
   ```

3. **Get a Gemini API Key**
   - Go to [Google AI Studio](https://aistudio.google.com/) and sign in.
   - Click **"Get API key"** on the left menu.
   - Click **"Create API key"** and copy the generated key. (It's completely free to use the generous free tier).

4. **Environment Setup**
   - Copy the `.env.example` file to create a `.env` file:
     ```bash
     # On Windows (Command Prompt):
     copy .env.example .env
     
     # On Mac/Linux:
     cp .env.example .env
     ```
   - Open the `.env` file and replace `your_api_key_here` with the API key you copied.

5. **Run the Agent**
   ```bash
   python main.py
   ```

## Usage
Once you run `python main.py`, the CLI will guide you through the process:
1. It will prompt you to paste a Job Description (Type `EOF` on a new line when done).
2. It will prompt you to paste a Candidate Resume (Type `EOF` on a new line when done).
3. The agent will process the inputs and begin the interactive technical interview in the terminal.
4. Answer the questions as the candidate to test the assessment logic.
5. After the questions are complete, a final structured JSON report will be printed out with scores, gap analysis, and the learning plan.
