import google.generativeai as genai
from config import config
import json
import logging

logger = logging.getLogger("reranker")

def rerank_chunks(query: str, chunks: list[dict], top_n: int = 4) -> list[dict]:
    """
    Reranks document chunks based on actual semantic relevance to the query.
    Uses the fast Gemini model to evaluate and score each chunk from 0 to 10.
    """
    if not chunks:
        return []

    # Configure genai (in case it wasn't done globally)
    genai.configure(api_key=config.GEMINI_API_KEY)
    model = genai.GenerativeModel(config.LLM_MODEL)

    # Format chunks cleanly for the LLM
    formatted_chunks = []
    for i, c in enumerate(chunks):
        text_content = c.get("text", "")
        # Remove excessive newlines for prompt compactness
        clean_text = " ".join(text_content.split())
        formatted_chunks.append(f"Chunk Index {i}:\n{clean_text}")

    chunks_str = "\n---\n".join(formatted_chunks)

    prompt = f"""You are a clinical RAG reranking assistant.
Evaluate the direct relevance of each document chunk below to the user query: "{query}"

For each chunk, assign a score from 0.0 to 10.0 based on how well it answers the query or provides necessary clinical context (10.0 is extremely relevant, 0.0 is completely irrelevant).

Document Chunks:
{chunks_str}

Return ONLY a raw JSON array of objects representing the scores:
[
  {{"index": 0, "score": 9.2}},
  {{"index": 1, "score": 1.5}}
]
Do not include any explanation, markdown formatting (like ```json), or trailing characters."""

    try:
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.1  # Low temperature for deterministic scoring
            )
        )
        text = response.text.strip()
        
        # Strip markdown formatting if the model output wrapped it in backticks
        if text.startswith("```"):
            lines = text.splitlines()
            if lines[0].startswith("```"):
                lines = lines[1:-1]
            text = "\n".join(lines).strip()
            if text.startswith("json"):
                text = text[4:].strip()

        scores = json.loads(text)
        
        # Map LLM scores back to chunks and calculate a blended score
        for item in scores:
            idx = item.get("index")
            if 0 <= idx < len(chunks):
                llm_score = float(item.get("score", 0.0)) / 10.0  # Scale to 0.0 - 1.0
                vector_score = chunks[idx]["score"]
                
                # Blended score: 70% LLM relevance, 30% Vector cosine similarity
                chunks[idx]["score"] = round((0.7 * llm_score) + (0.3 * vector_score), 3)

        # Sort chunks based on the new blended score descending
        sorted_chunks = sorted(chunks, key=lambda x: x["score"], reverse=True)
        logger.info(f"Successfully reranked {len(chunks)} chunks down to {top_n}.")
        return sorted_chunks[:top_n]

    except Exception as e:
        logger.error(f"Reranking failed: {e}. Falling back to default vector similarity ranking.")
        # Safe fallback: sort by original vector similarity and return top_n
        return sorted(chunks[:top_n])
