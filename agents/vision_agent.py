import json
import logging
import time
from pathlib import Path

import google.generativeai as genai

from agents.state import DermaFlowState
from config import config
from vision.extractor import extract_features
from utils.query_builder import build_search_query
from vision.scorer import retrieve_and_score
from vision.interpreter import interpret_scores, filter_relevant_chunks
from vision.prompts import build_response_prompt

logger = logging.getLogger("vision_agent")
genai.configure(api_key=config.GEMINI_API_KEY)

def vision_agent(state: DermaFlowState) -> DermaFlowState:
    start = time.time()

    logger.info(
        "Vision agent started | session=%s image='%s'",
        state["session_id"],
        state.get("image_path")
    )

    image_path = state.get("image_path")

    # ── guard ─────────────────────────────────
    if not image_path or not Path(image_path).exists():
        logger.error(
            "Invalid image path | '%s' | session=%s",
            image_path, state["session_id"]
        )
        return {
            **state,
            "response":                "No valid image provided for analysis.",
            "confident":               False,
            "chunks":                  [],
            "agent_used":              "vision_agent",
            "latency_ms":              round((time.time() - start) * 1000, 2),
            "vision_features":         None,
            "vision_condition_scores": None
        }

    # ── Stage 1: extract features ─────────────
    try:
        features = extract_features(image_path)
        logger.info("Features extracted | %s | session=%s", features, state["session_id"])

    except json.JSONDecodeError as e:
        logger.error("JSON parse failed | %s | session=%s", str(e), state["session_id"])
        features = {k: "unknown" for k in
                    ["lesion_type", "color", "location", "texture", "pattern", "severity"]}

    except Exception as e:
        logger.error("Feature extraction failed | %s | session=%s", str(e), state["session_id"])
        return {
            **state,
            "response":                "Image analysis failed. Please try with a clearer, well-lit photo.",
            "confident":               False,
            "chunks":                  [],
            "agent_used":              "vision_agent",
            "latency_ms":              round((time.time() - start) * 1000, 2),
            "vision_features":         None,
            "vision_condition_scores": None
        }

    # ── Stage 2: build search query ───────────
    search_query = build_search_query(state.get("query", ""), features)

    # ── Stage 3+4: retrieve and score ─────────
    chunks, condition_scores = retrieve_and_score(search_query)

    logger.info(
        "Scores | %s | session=%s",
        condition_scores, state["session_id"]
    )

    # ── Stage 4: interpret ────────────────────
    interpretation = interpret_scores(condition_scores)

    logger.info(
        "Interpretation | tier=%d confidence=%s conclusion='%s' | session=%s",
        interpretation["tier"],
        interpretation["confidence"],
        interpretation["conclusion"],
        state["session_id"]
    )

    # ── Tier 3: no match ──────────────────────
    if interpretation["tier"] == 3:
        logger.warning("No match | session=%s", state["session_id"])
        
        symptoms_desc = (
            f"Based on the image, I observe a **{features.get('color', 'unknown')}** area "
            f"with a **{features.get('texture', 'unknown')}** texture, appearing as "
            f"**{features.get('lesion_type', 'unknown')}** on the **{features.get('location', 'unknown')}**."
        )
        
        warning_message = (
            '<span style="color: red; font-weight: bold;">'
            '🚨 We do not have verified information about this specific presentation in our knowledge base. '
            'Concerning medical conditions, we cannot take the risk of guessing. '
            'Please consult a dermatologist or doctor nearby for a proper evaluation.'
            '</span>'
        )

        return {
            **state,
            "response": f"{symptoms_desc}\n\n{warning_message}",
            "confident":               False,
            "chunks":                  [],
            "agent_used":              "vision_agent",
            "latency_ms":              round((time.time() - start) * 1000, 2),
            "vision_features":         features,
            "vision_condition_scores": condition_scores
        }

    # ── Stage 5: filter relevant chunks ───────
    relevant_chunks = filter_relevant_chunks(chunks, interpretation)

    # ── Stage 6: generate response ────────────
    if relevant_chunks:
        prompt   = build_response_prompt(state.get("query", ""), features, interpretation, relevant_chunks)
        model    = genai.GenerativeModel(config.LLM_MODEL)
        response = model.generate_content(prompt)
        answer   = response.text
        confident = True
    else:
        answer = (
            f"{interpretation['message']}\n\n"
            f"Observed: {features.get('lesion_type')} lesions, "
            f"{features.get('color')} color, "
            f"{features.get('texture')} texture on {features.get('location')}.\n\n"
            f"Severity: {features.get('severity')}.\n\n"
            f"Please consult a dermatologist for accurate diagnosis."
        )
        confident = False

    latency = round((time.time() - start) * 1000, 2)

    logger.info(
        "Vision agent complete | tier=%d confident=%s latency=%sms | session=%s",
        interpretation["tier"], confident, latency, state["session_id"]
    )

    return {
        **state,
        "chunks":                  relevant_chunks,
        "confident":               confident,
        "response":                answer,
        "agent_used":              "vision_agent",
        "latency_ms":              latency,
        "vision_features":         features,
        "vision_condition_scores": condition_scores
    }
