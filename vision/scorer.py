import logging
from rag.retriever import retrieve

logger = logging.getLogger("vision_agent")

def retrieve_and_score(query: str) -> tuple[list[dict], dict[str, float]]:
    """
    Search Pinecone with no condition filter.
    Count which conditions appear most in top results.
    Score by both frequency AND retrieval score.
    """
    result = retrieve(query=query, condition=None)

    if not result["chunks"]:
        return [], {}

    chunks = result["chunks"]

    # count condition appearances weighted by retrieval score
    condition_weights: dict[str, float] = {}

    for chunk in chunks:
        condition = chunk.get("condition", "unknown")
        if condition == "unknown" or condition == "ingredient":
            continue
        score = chunk.get("score", 0.0)
        condition_weights[condition] = condition_weights.get(condition, 0.0) + score

    if not condition_weights:
        return chunks, {}

    # normalize to 0-1
    max_weight = max(condition_weights.values())
    condition_scores = {
        condition: round(weight / max_weight, 3)
        for condition, weight in condition_weights.items()
    }

    # sort descending
    condition_scores = dict(
        sorted(condition_scores.items(), key=lambda x: x[1], reverse=True)
    )

    logger.info("Condition scores from retrieval: %s", condition_scores)
    return chunks, condition_scores
