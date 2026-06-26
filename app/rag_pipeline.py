"""
RAG (Retrieval-Augmented Generation) Pipeline for Resume Screening.

Chunks the parsed resume, indexes chunks using custom local TF-IDF,
retrieves the top-k relevant chunks based on the job description,
and constructs the prompt for LLM evaluation.
"""

from app.matcher import (
    _tokenize,
    _get_ngrams,
    _compute_tf,
    _compute_idf,
    _cosine_similarity
)


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 150) -> list[str]:
    """
    Split text into chunks of roughly `chunk_size` characters,
    with a sliding window overlap of `overlap` characters.
    
    Tries to split on word or sentence boundaries where possible.
    """
    text = text.strip()
    if not text:
        return []

    chunks = []
    start = 0
    text_len = len(text)

    while start < text_len:
        end = start + chunk_size
        
        # If we aren't at the end, try to find a natural boundary (newline or space)
        if end < text_len:
            # Look for a boundary in the last 50 chars of the window
            boundary = -1
            for offset in range(50):
                char_idx = end - offset
                if text[char_idx] in ('\n', '.', ';', ','):
                    boundary = char_idx + 1
                    break
                elif text[char_idx] == ' ' and boundary == -1:
                    boundary = char_idx
            
            if boundary != -1:
                end = boundary
        
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
            
        # Move forward by window size minus overlap
        start = end - overlap
        if start >= text_len or (end - start) <= 0:
            break

    return chunks


def retrieve_relevant_chunks(jd_text: str, chunks: list[str], top_k: int = 3) -> list[str]:
    """
    Retrieve the top-k chunks from the list of chunks that are most relevant
    to the job description using custom TF-IDF cosine similarity.
    """
    if not chunks:
        return []
    
    # If the number of chunks is less than top_k, return all of them
    if len(chunks) <= top_k:
        return chunks

    # Tokenize the query (JD) and all chunks
    jd_tokens = _tokenize(jd_text)
    if not jd_tokens:
        return chunks[:top_k]

    # Combine JD tokens and n-grams
    jd_all = jd_tokens + _get_ngrams(jd_tokens)

    # Tokenize and compute n-grams for each chunk
    chunk_tokens_list = []
    for chunk in chunks:
        tokens = _tokenize(chunk)
        chunk_tokens_list.append(tokens + _get_ngrams(tokens))

    # Compute IDF across the corpus: query + all chunks
    corpus = [jd_all] + chunk_tokens_list
    idf = _compute_idf(corpus)

    # Compute TF-IDF vector for query (JD)
    jd_tf = _compute_tf(jd_all)
    jd_tfidf = {term: tf_val * idf.get(term, 0) for term, tf_val in jd_tf.items()}

    # Compute TF-IDF vectors for each chunk and calculate similarity
    scored_chunks = []
    for idx, chunk_tokens in enumerate(chunk_tokens_list):
        chunk_tf = _compute_tf(chunk_tokens)
        chunk_tfidf = {term: tf_val * idf.get(term, 0) for term, tf_val in chunk_tf.items()}
        
        sim = _cosine_similarity(jd_tfidf, chunk_tfidf)
        scored_chunks.append((sim, chunks[idx]))

    # Sort chunks by similarity score descending
    scored_chunks.sort(key=lambda x: x[0], reverse=True)

    # Return the text of the top-k chunks
    return [chunk for _, chunk in scored_chunks[:top_k]]


def build_rag_context(jd_text: str, resume_text: str, top_k: int = 3) -> str:
    """
    Splits the resume into chunks, retrieves the top-k relevant chunks,
    and returns a formatted context string.
    """
    chunks = chunk_text(resume_text)
    relevant_chunks = retrieve_relevant_chunks(jd_text, chunks, top_k=top_k)
    
    if not relevant_chunks:
        return "No relevant resume sections could be retrieved."
        
    context = ""
    for idx, chunk in enumerate(relevant_chunks):
        context += f"--- Resume Context Chunk #{idx + 1} ---\n{chunk}\n\n"
    
    return context.strip()
