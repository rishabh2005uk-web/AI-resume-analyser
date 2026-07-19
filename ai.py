import json
import ollama

def analyze_resume(resume_text, user_goal):
    # Rewritten prompt specifically optimized for small 1B models
    prompt = f"""
Analyze this resume for the role of: {user_goal}

You MUST output ONLY a valid JSON object. You must fill in ALL four arrays with at least 3 items each. 
Do not include any conversational text, introductions, or explanations. Use this EXACT format:

{{
  "skills": ["skill 1 found in resume", "skill 2 found in resume"],
  "missing_skills": ["skill 1 they need", "skill 2 they need"],
  "roadmap": ["Step 1: Learn X", "Step 2: Build Y project", "Step 3: Apply for Z"],
  "interview_questions": ["Question about their skills?", "Technical question about role?"]
}}

Resume text:
{resume_text}
"""
    try:
        response = ollama.chat(
            model="gemma3:1b", 
            messages=[
                {"role": "system", "content": "You are a JSON-only data extraction bot. You only output pure JSON."},
                {"role": "user", "content": prompt}
            ],
            options={
                "temperature": 0.2, # Lowered slightly to make the model more predictable
                "num_predict": 1000 # Forces the model to generate enough tokens to finish the lists
            }
        )

        content = response['message']['content'].strip()

        if content.startswith("```json"):
            content = content[7:]
        if content.endswith("```"):
            content = content[:-3]

        return json.loads(content.strip())

    except Exception as e:
        return {
            "skills": [],
            "missing_skills": [],
            "roadmap": [],
            "interview_questions": [],
            "error": f"Ollama error: {str(e)}"
        }