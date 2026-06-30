import time
import google.generativeai as genai
from rag.vectordb import index
from config import config
from rag.reranker import rerank_chunks

genai.configure(api_key=config.GEMINI_API_KEY)

INTENT_THRESHOLDS = {
    "ingredient": 0.60,      # Strict threshold for ingredient interactions safety
    "condition_info": 0.45,  # Moderate threshold for general symptoms facts
}

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
    threshold: float = None,
    intent: str = None
) -> dict:
    """
    Core retrieval function.

    Args:
        query:     user query string
        condition: optional filter — "acne", "eczema", "ingredient", etc.
        top_k:     how many results to fetch (defaults to config)
        threshold: minimum confidence score (defaults to config)
        intent:    detected intent ("ingredient", "condition_info", etc.)

    Returns:
        {
            "chunks":    list of matched chunks with text + metadata + score
            "confident": bool — False means hand off to web search agent
            "query":     original query (useful for logging)
            "filter":    what condition filter was applied
        }
    """
    top_k     = top_k     or config.TOP_K_RETRIEVE
    
    # Determine confidence threshold dynamically based on intent safety constraints
    intent_threshold = INTENT_THRESHOLDS.get(intent, config.CONFIDENCE_THRESHOLD)
    threshold = threshold or intent_threshold

    start_time = time.time()

    query_vector = embed_query(query)

    # build filter
    filter_dict = {}
    
    # If intent is ingredient, strictly filter for ingredient type chunks
    if intent == "ingredient":
        filter_dict["type"] = {"$eq": "ingredient"}
    # Otherwise if a specific condition is provided, filter for it
    elif condition and condition not in ("general", "unknown", "none"):
        filter_dict["condition"] = {"$eq": condition}

    # If filter_dict is empty, set it to None for Pinecone
    if not filter_dict:
        filter_dict = None

    # Retrieve a larger set of candidates for reranking (e.g. 3x top_k)
    candidate_k = max(top_k * 3, 12)
    results = index.query(
        vector=query_vector,
        top_k=candidate_k,
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

    # Convert Pinecone matches to flat dicts for the reranker
    raw_chunks = [
        {
            "text":      m["metadata"].get("text", ""),
            "condition": m["metadata"].get("condition", "unknown"),
            "source":    m["metadata"].get("source", "unknown"),
            "score":     m["score"],
            "chunk_index": m["metadata"].get("chunk_index", -1)
        }
        for m in matches
    ]

    # Rerank and select the top_k most relevant chunks
    reranked_chunks = rerank_chunks(query, raw_chunks, top_n=top_k)

    # Filter the reranked chunks by the confidence threshold
    confident_chunks = [
        rc for rc in reranked_chunks if rc["score"] >= threshold
    ]

    return {
        "chunks":     confident_chunks,
        "confident":  len(confident_chunks) > 0,
        "query":      query,
        "filter":     condition,
        "latency_ms": latency_ms
    }

