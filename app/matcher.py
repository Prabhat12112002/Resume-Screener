"""
Matching Engine — Hybrid TF-IDF + Skill-Based Scoring.

Implements TF-IDF from scratch (no scikit-learn/numpy dependency) to ensure
maximum portability across environments.

Combines two complementary approaches:
  1. Skill-based matching (60% weight):  Jaccard similarity between JD and resume skills.
  2. Text-based matching (40% weight):   TF-IDF cosine similarity on full document text.

This hybrid approach captures both explicit skill overlap and contextual relevance.
"""

import math
import re
from collections import Counter

from app.parser import ParsedDocument

# ── Weights ────────────────────────────────────────────────────────────
SKILL_WEIGHT = 0.60
TEXT_WEIGHT = 0.40

# ── English Stop Words ─────────────────────────────────────────────────
STOP_WORDS = frozenset({
    "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "as", "is", "was", "are", "were", "been",
    "be", "have", "has", "had", "do", "does", "did", "will", "would",
    "could", "should", "may", "might", "shall", "can", "need", "must",
    "it", "its", "this", "that", "these", "those", "i", "me", "my",
    "we", "our", "you", "your", "he", "him", "his", "she", "her",
    "they", "them", "their", "what", "which", "who", "whom", "how",
    "when", "where", "why", "if", "then", "so", "no", "not", "only",
    "very", "just", "about", "above", "after", "before", "between",
    "into", "through", "during", "each", "few", "more", "most", "other",
    "some", "such", "than", "too", "also", "both", "same", "all", "any",
    "up", "out", "over", "under", "again", "further", "once", "here",
    "there", "am", "being", "having", "doing", "own", "because",
})


def _tokenize(text: str) -> list[str]:
    """Tokenize text into lowercase words, removing stop words and short tokens."""
    text = text.lower()
    # Extract words (alphanumeric + some special chars for tech terms)
    words = re.findall(r"[a-z0-9#+\.\-]+", text)
    # Filter stop words and very short tokens
    return [w for w in words if w not in STOP_WORDS and len(w) > 1]


def _get_ngrams(tokens: list[str], n: int = 2) -> list[str]:
    """Generate n-grams from a list of tokens."""
    ngrams = []
    for i in range(len(tokens) - n + 1):
        ngrams.append(" ".join(tokens[i:i + n]))
    return ngrams


def _compute_tf(tokens: list[str]) -> dict[str, float]:
    """Compute sublinear term frequency: 1 + log(count) if count > 0, else 0."""
    counts = Counter(tokens)
    tf = {}
    for term, count in counts.items():
        tf[term] = 1 + math.log(count) if count > 0 else 0
    return tf


def _compute_idf(documents: list[list[str]]) -> dict[str, float]:
    """Compute inverse document frequency: log(N / df) for each term."""
    n_docs = len(documents)
    df: dict[str, int] = {}

    for doc_tokens in documents:
        unique_terms = set(doc_tokens)
        for term in unique_terms:
            df[term] = df.get(term, 0) + 1

    idf = {}
    for term, doc_freq in df.items():
        idf[term] = math.log(n_docs / doc_freq) if doc_freq > 0 else 0
    return idf


def _cosine_similarity(vec_a: dict[str, float], vec_b: dict[str, float]) -> float:
    """Compute cosine similarity between two sparse vectors (dicts)."""
    # Find common terms
    common_terms = set(vec_a.keys()) & set(vec_b.keys())

    if not common_terms:
        return 0.0

    dot_product = sum(vec_a[t] * vec_b[t] for t in common_terms)
    magnitude_a = math.sqrt(sum(v * v for v in vec_a.values()))
    magnitude_b = math.sqrt(sum(v * v for v in vec_b.values()))

    if magnitude_a == 0 or magnitude_b == 0:
        return 0.0

    return dot_product / (magnitude_a * magnitude_b)


def compute_skill_similarity(jd_skills: list[str], resume_skills: list[str]) -> float:
    """
    Compute skill recall: what fraction of JD-required skills does the resume cover?

    Recall = |intersection| / |jd_skills|

    This is more appropriate than Jaccard for resume screening because we care about
    how well the resume covers the JD requirements, not penalizing extra skills.

    Returns a float between 0.0 and 1.0.
    """
    jd_set = set(s.lower() for s in jd_skills)
    resume_set = set(s.lower() for s in resume_skills)

    if not jd_set:
        return 0.0

    intersection = jd_set & resume_set
    return len(intersection) / len(jd_set)


def compute_text_similarity(jd_text: str, resume_text: str) -> float:
    """
    Compute TF-IDF cosine similarity between JD and resume text.

    Uses a from-scratch TF-IDF implementation with unigrams + bigrams.
    Returns a float between 0.0 and 1.0.
    """
    if not jd_text.strip() or not resume_text.strip():
        return 0.0

    # Tokenize both documents
    jd_tokens = _tokenize(jd_text)
    resume_tokens = _tokenize(resume_text)

    if not jd_tokens or not resume_tokens:
        return 0.0

    # Add bigrams for better contextual matching
    jd_all = jd_tokens + _get_ngrams(jd_tokens)
    resume_all = resume_tokens + _get_ngrams(resume_tokens)

    # Compute IDF across both documents
    idf = _compute_idf([jd_all, resume_all])

    # Compute TF-IDF vectors
    jd_tf = _compute_tf(jd_all)
    resume_tf = _compute_tf(resume_all)

    jd_tfidf = {term: tf_val * idf.get(term, 0) for term, tf_val in jd_tf.items()}
    resume_tfidf = {term: tf_val * idf.get(term, 0) for term, tf_val in resume_tf.items()}

    return _cosine_similarity(jd_tfidf, resume_tfidf)


def get_matched_skills(jd_skills: list[str], resume_skills: list[str]) -> list[str]:
    """Return skills present in both the JD and the resume."""
    jd_set = set(s.lower() for s in jd_skills)
    resume_set = set(s.lower() for s in resume_skills)
    return sorted(jd_set & resume_set)


def get_missing_skills(jd_skills: list[str], resume_skills: list[str]) -> list[str]:
    """Return skills required by the JD but missing from the resume."""
    jd_set = set(s.lower() for s in jd_skills)
    resume_set = set(s.lower() for s in resume_skills)
    return sorted(jd_set - resume_set)


def generate_explanation(
    score: int,
    matched: list[str],
    missing: list[str],
    experience_years: float | None,
) -> str:
    """
    Generate a human-readable 2-3 line explanation of the match assessment.

    Considers the overall score, skill overlap, and experience.
    """
    total_jd_skills = len(matched) + len(missing)

    # ── Score-based opening line ───────────────────────────────────────
    if score >= 80:
        opening = "Strong match for this role."
    elif score >= 60:
        opening = "Good match with some skill gaps."
    elif score >= 40:
        opening = "Moderate match — several key skills are missing."
    elif score >= 20:
        opening = "Weak match — significant skill gaps identified."
    else:
        opening = "Poor match — the candidate's profile does not align well with this role."

    # ── Skills detail line ─────────────────────────────────────────────
    if total_jd_skills > 0:
        match_pct = (len(matched) / total_jd_skills) * 100
        skills_line = (
            f"The candidate matches {len(matched)} out of {total_jd_skills} "
            f"identified skills ({match_pct:.0f}% skill overlap)."
        )
    else:
        skills_line = "No specific skills could be identified from the job description."

    # ── Experience line (optional) ─────────────────────────────────────
    if experience_years is not None:
        exp_line = f" The resume indicates approximately {experience_years:.0f} years of experience."
    else:
        exp_line = ""

    return f"{opening} {skills_line}{exp_line}"


def compute_match(jd_parsed: ParsedDocument, resume_parsed: ParsedDocument) -> dict:
    """
    Compute the full match result between a JD and a resume.

    Combines skill-based and text-based similarity into a weighted score,
    then generates matched/missing skills lists and an explanation.

    Args:
        jd_parsed:     Parsed job description.
        resume_parsed: Parsed resume.

    Returns:
        Dictionary with keys: match_score, matched_skills, missing_skills, explanation.
    """
    # ── Compute individual similarities ────────────────────────────────
    skill_sim = compute_skill_similarity(jd_parsed.skills, resume_parsed.skills)
    text_sim = compute_text_similarity(jd_parsed.raw_text, resume_parsed.raw_text)

    # ── Weighted combination → scale to 0–100 ─────────────────────────
    combined = (SKILL_WEIGHT * skill_sim) + (TEXT_WEIGHT * text_sim)
    match_score = int(round(combined * 100))
    match_score = max(0, min(100, match_score))  # Clamp

    # ── Skill lists ────────────────────────────────────────────────────
    matched = get_matched_skills(jd_parsed.skills, resume_parsed.skills)
    missing = get_missing_skills(jd_parsed.skills, resume_parsed.skills)

    # ── Explanation ────────────────────────────────────────────────────
    explanation = generate_explanation(
        score=match_score,
        matched=matched,
        missing=missing,
        experience_years=resume_parsed.experience_years,
    )

    return {
        "match_score": match_score,
        "matched_skills": matched,
        "missing_skills": missing,
        "explanation": explanation,
    }
