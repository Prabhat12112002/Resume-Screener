"""
Smart Resume Screening System — FastAPI Application.

AI-powered resume screening that matches resumes against a job description
using TF-IDF + Cosine Similarity combined with skill-based matching.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.models import ResumeScreenRequest, ResumeResult, ScreeningResponse
from app.parser import parse_document
from app.matcher import compute_match


# ── FastAPI App ────────────────────────────────────────────────────────
app = FastAPI(
    title="Smart Resume Screening System",
    description=(
        "AI-powered resume screening API that matches resumes against a job description "
        "using a hybrid approach: TF-IDF cosine similarity + skill-based matching. "
        "Returns relevance scores (0–100), matched/missing skills, and brief explanations."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS Middleware ────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Health Check ───────────────────────────────────────────────────────
@app.get("/", tags=["Health"])
def health_check():
    """Health check endpoint with API information."""
    return {
        "status": "healthy",
        "service": "Smart Resume Screening System",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoint": "POST /screen-resumes",
    }


# ── Main Screening Endpoint ───────────────────────────────────────────
@app.post(
    "/screen-resumes",
    response_model=ScreeningResponse,
    tags=["Screening"],
    summary="Screen resumes against a job description",
    description=(
        "Accepts a job description and a list of resumes, then returns each resume's "
        "relevance score (0–100), matched skills, missing skills, and a brief explanation. "
        "Results are sorted by match score in descending order."
    ),
)
def screen_resumes(request: ResumeScreenRequest) -> ScreeningResponse:
    """
    Screen one or more resumes against a job description.

    The matching engine uses a hybrid approach:
      - 60% weight: Skill-based matching (Jaccard similarity)
      - 40% weight: Text-based matching (TF-IDF cosine similarity)

    Returns results sorted by match score (highest first).
    """
    try:
        # ── Parse the Job Description ──────────────────────────────────
        jd_parsed = parse_document(request.job_description)

        # ── Process each resume ────────────────────────────────────────
        results: list[ResumeResult] = []

        for resume in request.resumes:
            resume_parsed = parse_document(resume.text)
            match_result = compute_match(jd_parsed, resume_parsed)

            results.append(
                ResumeResult(
                    name=resume.name,
                    match_score=match_result["match_score"],
                    matched_skills=match_result["matched_skills"],
                    missing_skills=match_result["missing_skills"],
                    explanation=match_result["explanation"],
                )
            )

        # ── Sort by score descending ───────────────────────────────────
        results.sort(key=lambda r: r.match_score, reverse=True)

        return ScreeningResponse(
            total_resumes=len(results),
            results=results,
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred during resume screening: {str(e)}",
        )


# ── Run with: uvicorn app.main:app --reload ────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
