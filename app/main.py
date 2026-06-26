"""
Smart Resume Screening System — FastAPI Application.

AI-powered resume screening matching resumes against a job description
using:
  - pdfplumber for PDF extraction
  - Custom local TF-IDF RAG pipeline
  - Groq API Llama 3 model (with local scoring engine fallback)
  - Premium Dark/Glassmorphic Web Interface
"""

import os
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.models import ResumeResult, ScreeningResponse
from app.parser import parse_document, extract_text_from_pdf
from app.matcher import compute_match
from app.rag_pipeline import build_rag_context
from app.groq_client import screen_with_groq, is_groq_available

# ── FastAPI App Setup ──────────────────────────────────────────────────
app = FastAPI(
    title="Smart Resume Screening System",
    description="Intelligent AI resume screening engine leveraging pdfplumber, local RAG, and Groq Llama-3.",
    version="1.1.0"
)

# Enable CORS for all domains
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Serve Static UI Assets ─────────────────────────────────────────────
# Get path to the static folder
static_dir = os.path.join(os.path.dirname(__file__), "static")
if not os.path.exists(static_dir):
    os.makedirs(static_dir)

# Mount the static directory for CSS and JS
app.mount("/static", StaticFiles(directory=static_dir), name="static")


# ── Render UI Frontend on Root ─────────────────────────────────────────
@app.get("/", tags=["UI"])
def get_home():
    """Serves the main screening web application interface."""
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    raise HTTPException(status_code=404, detail="Frontend interface not found.")


# ── Health Check ───────────────────────────────────────────────────────
@app.get("/health", tags=["Health"])
def health_check():
    """Health check endpoint with system connectivity info."""
    return {
        "status": "healthy",
        "service": "Smart Resume Screening System",
        "version": "1.1.0",
        "groq_api_available": is_groq_available(),
    }


# ── Main Screening Endpoint (Multipart Upload) ─────────────────────────
@app.post(
    "/screen-resumes",
    response_model=ScreeningResponse,
    tags=["Screening"],
    summary="Screen PDF and text resumes against a job description",
)
async def screen_resumes(
    job_description: str = Form(..., description="Job requirements description text"),
    resumes: list[UploadFile] = File(..., description="Resumes to screen (PDF or TXT files)")
) -> ScreeningResponse:
    """
    Accepts job description text and a list of upload files (PDF or TXT).
    
    Processing flow:
      1. Extract text using pdfplumber (for PDFs) or string decoding (for TXT).
      2. If Groq API is available:
         - Build RAG Context: Extract top-3 relevant chunks matching the JD query.
         - Call Groq Llama 3 (JSON Mode) using RAG context.
         - Return structured results.
      3. If Groq API is missing/fails:
         - Automatically falls back to the local matcher (TF-IDF + Skill Recall).
    """
    if not resumes:
        raise HTTPException(status_code=400, detail="No resume files uploaded.")
        
    try:
        # Parse Job Description
        jd_parsed = parse_document(job_description)
        results: list[ResumeResult] = []

        for resume_file in resumes:
            # Clean filename
            filename = resume_file.filename or "Unnamed_Candidate"
            ext = filename.split('.')[-1].lower() if '.' in filename else ""
            
            # Read file bytes
            file_bytes = await resume_file.read()
            
            # Extract Text
            text = ""
            if ext == "pdf":
                text = extract_text_from_pdf(file_bytes)
            elif ext == "txt":
                try:
                    text = file_bytes.decode("utf-8")
                except UnicodeDecodeError:
                    text = file_bytes.decode("latin-1", errors="ignore")
            else:
                # Unsupported files skipped or treated as plain string
                text = file_bytes.decode("utf-8", errors="ignore")

            if not text.strip():
                # Skip files with empty text
                continue

            # Run RAG & Matching Logic
            match_score = 0
            matched_skills = []
            missing_skills = []
            explanation = ""

            # Attempt screening with Groq (RAG)
            groq_result = None
            if is_groq_available():
                # Extract top-3 chunks matching JD
                rag_context = build_rag_context(job_description, text, top_k=3)
                # Query LLM
                groq_result = screen_with_groq(job_description, rag_context)

            if groq_result:
                match_score = groq_result["match_score"]
                matched_skills = groq_result["matched_skills"]
                missing_skills = groq_result["missing_skills"]
                explanation = groq_result["explanation"]
            else:
                # Fallback to local scoring engine
                resume_parsed = parse_document(text)
                local_result = compute_match(jd_parsed, resume_parsed)
                match_score = local_result["match_score"]
                matched_skills = local_result["matched_skills"]
                missing_skills = local_result["missing_skills"]
                explanation = local_result["explanation"]

            # Standardize output schemas
            results.append(
                ResumeResult(
                    name=filename,
                    match_score=match_score,
                    matched_skills=matched_skills,
                    missing_skills=missing_skills,
                    explanation=explanation,
                )
            )

        # Sort results by match score descending
        results.sort(key=lambda r: r.match_score, reverse=True)

        return ScreeningResponse(
            total_resumes=len(results),
            results=results,
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing resume screening: {str(e)}"
        )
