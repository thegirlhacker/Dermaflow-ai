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
            "tier": 3,
            "conclusion": "unknown",
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

    # confidence and tier threshold
    if best_score >= 0.75:
        tier = 1
        confident = True
    elif best_score >= 0.4:
        tier = 2
        confident = False
    else:
        tier = 3
        confident = False

    return {
        "condition": best_condition,
        "confidence": round(best_score, 2),
        "confident": confident,
        "tier": tier,
        "conclusion": best_condition,
        "message": (
            f"Visual features may match "
            f"{best_condition.replace('_', ' ')}."
        )
    }


def filter_relevant_chunks(
    chunks: list[dict],
    condition: any
) -> list[dict]:
    """
    Keep only chunks related to predicted condition.
    Supports both a condition string or an interpretation dictionary.
    """
    if not condition:
        return []

    # Defensively extract the condition string if a dictionary is passed
    if isinstance(condition, dict):
        condition_str = condition.get("condition")
    else:
        condition_str = condition

    if not condition_str:
        return []

    filtered = [
        chunk for chunk in chunks
        if chunk.get("condition") == condition_str
    ]

    # fallback if nothing matched
    if not filtered:
        return chunks[:3]

    return filtered