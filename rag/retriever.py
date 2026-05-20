import time
import google.generativeai as genai
from rag.vectordb import index
from config import config

genai.configure(api_key=config.GEMINI_API_KEY)

def embed_query(query: str) -> list[float]:
    """Embed a single query string."""
    response = genai.embed_content(
        model=config.EMBEDDING_MODEL,
        content=query.lower().strip(),
        task_type="retrieval_query",
        output_dimensionality=config.EMBEDDING_DIMENSION
    )
    return response['embedding']

def retrieve(
    query: str,
    condition: str = None,
    top_k: int = None,
    threshold: float = None
) -> dict:
    """
    Core retrieval function.

    Args:
        query:     user query string
        condition: optional filter — "acne", "eczema", "ingredient", etc.
        top_k:     how many results to fetch (defaults to config)
        threshold: minimum confidence score (defaults to config)

    Returns:
        {
            "chunks":    list of matched chunks with text + metadata + score
            "confident": bool — False means hand off to web search agent
            "query":     original query (useful for logging)
            "filter":    what condition filter was applied
        }
    """
    top_k     = top_k     or config.TOP_K_RETRIEVE
    threshold = threshold or config.CONFIDENCE_THRESHOLD

    start_time = time.time()

    query_vector = embed_query(query)

    # build filter only if condition is specified and meaningful
    filter_dict = None
    if condition and condition not in ("general", "unknown", "none"):
        filter_dict = {"condition": {"$eq": condition}}

    results = index.query(
        vector=query_vector,
        top_k=top_k,
        filter=filter_dict,
        include_metadata=True
    )

    latency_ms = round((time.time() - start_time) * 1000, 2)

    matches = results.get("matches", [])

    if not matches:
        return {
            "chunks":    [],
            "confident": False,
            "query":     query,
            "filter":    condition,
            "latency_ms": latency_ms
        }

    # filter by confidence threshold
    confident_chunks = []
    for m in matches:
        if m["score"] >= threshold:
            confident_chunks.append({
                "text":      m["metadata"].get("text", ""),
                "condition": m["metadata"].get("condition", "unknown"),
                "source":    m["metadata"].get("source", "unknown"),
                "score":     round(m["score"], 3),
                "chunk_index": m["metadata"].get("chunk_index", -1)
            })

    return {
        "chunks":     confident_chunks,
        "confident":  len(confident_chunks) > 0,
        "query":      query,
        "filter":     condition,
        "latency_ms": latency_ms
    }

def retrieve_multi_condition(query: str, conditions: list[str]) -> dict:
    """
    Retrieve across multiple conditions and merge results.
    Useful when triage agent isn't sure which condition applies.

    Example: query about 'red itchy skin' might be eczema OR contact dermatitis
    """
    all_chunks = []
    for condition in conditions:
        result = retrieve(query, condition=condition)
        all_chunks.extend(result["chunks"])

    # deduplicate by text and re-sort by score
    seen = set()
    unique_chunks = []
    for chunk in sorted(all_chunks, key=lambda x: x["score"], reverse=True):
        if chunk["text"] not in seen:
            seen.add(chunk["text"])
            unique_chunks.append(chunk)

    return {
        "chunks":    unique_chunks[:config.TOP_K_RETRIEVE],
        "confident": len(unique_chunks) > 0,
        "query":     query,
        "filter":    conditions,
        "latency_ms": 0
    }
        
