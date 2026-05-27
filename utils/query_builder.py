import logging

logger = logging.getLogger("query_builder")

def build_search_query(query: str, features: dict = None) -> str:
    """
    Combine original query and extracted features into an optimized
    natural language search query for dermatology search.
    """
    parts = []
    
    if query and query.strip():
        parts.append(query.strip())
        
    if features:
        lesion   = features.get("lesion_type", "unknown")
        color    = features.get("color",       "unknown")
        location = features.get("location",    "unknown")
        texture  = features.get("texture",     "unknown")
        pattern  = features.get("pattern",     "unknown")

        feature_parts = []
        if color    != "unknown": feature_parts.append(color)
        if lesion   != "unknown": feature_parts.append(lesion)
        if location != "unknown": feature_parts.append(f"on {location}")
        if texture  != "unknown": feature_parts.append(f"{texture} texture")
        if pattern  != "unknown": feature_parts.append(pattern)
        
        if feature_parts:
            parts.append(" ".join(feature_parts))

    final_query = " ".join(parts)

    # fallback if everything was empty
    if not final_query.strip():
        final_query = "skin condition symptoms treatment"

    logger.info("Built search query: '%s'", final_query)
    return final_query
