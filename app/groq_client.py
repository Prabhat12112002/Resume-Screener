"""
Groq API Client for Intelligent Resume Matching.

Sends parsed resume RAG context and job description to Groq's Llama 3 model
to compute structured matching scores, skills lists, and explanations.

Falls back to the local matching engine if the API key is not configured
or if the network request fails.
"""

import os
import json
from dotenv import load_dotenv
from groq import Groq

# Load environment variables from .env
load_dotenv()

# Initialize Groq client if key is present
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = None

if GROQ_API_KEY:
    client = Groq(api_key=GROQ_API_KEY)


def is_groq_available() -> bool:
    """Check if the Groq API key is configured."""
    return client is not None


def screen_with_groq(jd_text: str, rag_context: str) -> dict | None:
    """
    Screen a resume's RAG context against a job description using Groq LLM (llama3-8b-8192).
    
    Enforces JSON mode so the response matches the expected structure.
    Returns:
        Dict with keys: match_score, matched_skills, missing_skills, explanation
        Or None if the request fails or isn't configured.
    """
    if not is_groq_available():
        return None

    system_prompt = (
        "You are an expert technical recruiter and resume screener. "
        "Analyze the candidate's resume context (provided as RAG chunks) against the job description text.\n\n"
        "You must return a valid JSON object matching this structure EXACTLY:\n"
        "{\n"
        '  "match_score": 85, // An integer between 0 and 100 representing job description alignment\n'
        '  "matched_skills": ["Python", "FastAPI"], // Skills requested in JD that are present in resume context\n'
        '  "missing_skills": ["Docker", "Kubernetes"], // Skills requested in JD but missing in resume context\n'
        '  "explanation": "Brief 2-3 sentence recruiter overview of the candidate fit."\n'
        "}\n\n"
        "Keep the explanation under 3 sentences. Be strict, objective, and precise with skills."
    )

    user_prompt = f"### JOB DESCRIPTION:\n{jd_text}\n\n### RETRIEVED RESUME CONTEXT CHUNKS:\n{rag_context}"

    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            model="llama3-8b-8192",  # Fast, cost-efficient, and supports JSON mode
            response_format={"type": "json_object"},
            temperature=0.2,         # Low temperature for highly objective, structured output
            max_tokens=500
        )
        
        # Parse the JSON response
        response_content = chat_completion.choices[0].message.content
        result = json.loads(response_content)
        
        # Validate output schema fields
        required_keys = ["match_score", "matched_skills", "missing_skills", "explanation"]
        if all(key in result for key in required_keys):
            return {
                "match_score": int(result["match_score"]),
                "matched_skills": list(result["matched_skills"]),
                "missing_skills": list(result["missing_skills"]),
                "explanation": str(result["explanation"])
            }
            
    except Exception as e:
        # If anything fails (network issue, parse error), fail gracefully
        # so the application falls back to the local matching engine.
        print(f"[Groq Error] Failed to screen resume RAG context: {str(e)}")
        
    return None
