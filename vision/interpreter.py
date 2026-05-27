import logging

logger = logging.getLogger("vision_agent")


def interpret_scores(condition_scores: dict) -> dict:
    """
    Pick the best matching condition
    and decide whether confidence is good enough.
    """

    # no matches found
    if not condition_scores:
        return {
            "condition": None,
            "confidence": 0.0,
            "confident": False,
            "message": "No matching condition found."
        }

    # get highest scoring condition
    best_condition = max(
        condition_scores,
        key=condition_scores.get
    )

    best_score = condition_scores[best_condition]

    logger.info(
        "Best condition=%s score=%.2f",
        best_condition,
        best_score
    )

    # confidence threshold
    confident = best_score >= 0.6

    return {
        "condition": best_condition,
        "confidence": round(best_score, 2),
        "confident": confident,
        "message": (
            f"Visual features may match "
            f"{best_condition.replace('_', ' ')}."
        )
    }


def filter_relevant_chunks(
    chunks: list[dict],
    condition: str
) -> list[dict]:
    """
    Keep only chunks related
    to predicted condition.
    """

    if not condition:
        return []

    filtered = [
        chunk for chunk in chunks
        if chunk.get("condition") == condition
    ]

    # fallback if nothing matched
    if not filtered:
        return chunks[:3]

    return filtered