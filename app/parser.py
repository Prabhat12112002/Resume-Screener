"""
Resume & Job Description Parser.

Extracts skills and experience from plain text documents using
the curated skills database for reliable matching.
"""

import re
from dataclasses import dataclass, field

from app.skills_db import get_all_skills, get_multi_word_skills, get_single_word_skills


@dataclass
class ParsedDocument:
    """Structured representation of a parsed resume or job description."""
    skills: list[str] = field(default_factory=list)
    experience_years: float | None = None
    raw_text: str = ""


def _normalize_text(text: str) -> str:
    """Normalize text for processing: lowercase, collapse whitespace."""
    text = text.lower()
    # Replace common separators with spaces
    text = re.sub(r"[/|,;•·●►▸\-–—]", " ", text)
    # Collapse multiple whitespace
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def extract_skills(text: str) -> list[str]:
    """
    Extract skills from text by matching against the skills database.

    Strategy:
      1. First match multi-word skills (e.g., "machine learning", "spring boot")
         using substring search on the normalized text.
      2. Then match single-word skills using word-boundary regex to avoid
         partial matches (e.g., "r" shouldn't match "react").

    Returns a sorted, deduplicated list of matched skills.
    """
    normalized = _normalize_text(text)
    found_skills: set[str] = set()

    # ── Pass 1: Multi-word skills (substring match) ────────────────────
    multi_word = get_multi_word_skills()
    for skill in multi_word:
        # Normalize the skill itself for matching
        skill_normalized = skill.lower().strip()
        if skill_normalized in normalized:
            found_skills.add(skill)

    # ── Pass 2: Single-word skills (word-boundary match) ───────────────
    single_word = get_single_word_skills()
    for skill in single_word:
        skill_lower = skill.lower().strip()
        # Use word boundaries to prevent partial matches
        # Special handling for very short skills (1-2 chars like "r", "c")
        if len(skill_lower) <= 2:
            # For very short skills, require them to appear as standalone words
            # surrounded by spaces, start/end of string, or punctuation
            pattern = r"(?<![a-zA-Z])" + re.escape(skill_lower) + r"(?![a-zA-Z])"
        else:
            pattern = r"\b" + re.escape(skill_lower) + r"\b"

        if re.search(pattern, normalized):
            found_skills.add(skill)

    return sorted(found_skills)


def extract_experience_years(text: str) -> float | None:
    """
    Extract years of experience from text using common patterns.

    Matches patterns like:
      - "5 years of experience"
      - "3+ years"
      - "5+ years of expertise"
      - "over 7 years"
      - "2-3 years experience"

    Returns the maximum years found, or None if no pattern matches.
    """
    normalized = text.lower()
    years_found: list[float] = []

    patterns = [
        # "5+ years of experience/expertise"
        r"(\d+)\+?\s*(?:years?|yrs?)\s*(?:of\s+)?(?:experience|expertise|work)",
        # "over/more than 5 years"
        r"(?:over|more\s+than)\s+(\d+)\s*(?:years?|yrs?)",
        # "5-7 years" (take the higher number)
        r"(\d+)\s*[\-–—to]+\s*(\d+)\s*(?:years?|yrs?)",
        # "5 years in ..."
        r"(\d+)\s*(?:years?|yrs?)\s+(?:in|of|as|with)",
        # Standalone "X+ years"
        r"(\d+)\+\s*(?:years?|yrs?)",
    ]

    for pattern in patterns:
        matches = re.findall(pattern, normalized)
        for match in matches:
            if isinstance(match, tuple):
                # For range patterns, take all numeric groups
                for val in match:
                    if val:
                        try:
                            years_found.append(float(val))
                        except ValueError:
                            pass
            else:
                try:
                    years_found.append(float(match))
                except ValueError:
                    pass

    return max(years_found) if years_found else None


def parse_document(text: str) -> ParsedDocument:
    """
    Parse a resume or job description text into a structured document.

    Extracts:
      - Skills (from the curated skills database)
      - Experience years (via regex patterns)
      - Preserves the raw text for TF-IDF analysis

    Args:
        text: The full text content of the resume or JD.

    Returns:
        A ParsedDocument with extracted skills, experience, and raw text.
    """
    return ParsedDocument(
        skills=extract_skills(text),
        experience_years=extract_experience_years(text),
        raw_text=text.strip(),
    )
