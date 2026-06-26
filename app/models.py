"""
Pydantic models for request/response validation.
"""

from pydantic import BaseModel, Field


# ── Request Models ─────────────────────────────────────────────────────

class ResumeInput(BaseModel):
    """A single resume input with a name/identifier and the full text content."""
    name: str = Field(
        ...,
        description="Name or identifier for the resume (e.g., candidate name or filename)",
        examples=["John_Doe_Resume"],
    )
    text: str = Field(
        ...,
        description="Full text content of the resume",
        min_length=10,
    )


class ResumeScreenRequest(BaseModel):
    """Request body for the resume screening endpoint."""
    job_description: str = Field(
        ...,
        description="Full text of the job description to match resumes against",
        min_length=10,
    )
    resumes: list[ResumeInput] = Field(
        ...,
        description="List of resumes to screen against the job description",
        min_length=1,
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "job_description": "We are looking for a Python developer with experience in FastAPI, PostgreSQL, and Docker...",
                    "resumes": [
                        {
                            "name": "Alice_Backend",
                            "text": "Experienced Python developer with 5 years in Django, FastAPI, PostgreSQL...",
                        }
                    ],
                }
            ]
        }
    }


# ── Response Models ────────────────────────────────────────────────────

class ResumeResult(BaseModel):
    """Screening result for a single resume."""
    name: str = Field(
        ...,
        description="Name/identifier of the resume",
    )
    match_score: int = Field(
        ...,
        ge=0,
        le=100,
        description="Relevance score from 0 (no match) to 100 (perfect match)",
    )
    matched_skills: list[str] = Field(
        default_factory=list,
        description="Skills found in both the JD and the resume",
    )
    missing_skills: list[str] = Field(
        default_factory=list,
        description="Skills required by the JD but not found in the resume",
    )
    explanation: str = Field(
        ...,
        description="Brief 2-3 line explanation of the match assessment",
    )
    engine: str = Field(
        ...,
        description="The matching engine used for this resume: 'groq' or 'local'",
    )


class ScreeningResponse(BaseModel):
    """Full response for the resume screening endpoint."""
    total_resumes: int = Field(
        ...,
        description="Total number of resumes screened",
    )
    results: list[ResumeResult] = Field(
        ...,
        description="Screening results sorted by match score (highest first)",
    )
