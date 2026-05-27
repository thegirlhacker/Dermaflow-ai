import json
import logging
import PIL.Image
import google.generativeai as genai

from config import config
from vision.prompts import EXTRACTION_PROMPT

logger = logging.getLogger("vision_agent")

def extract_features(image_path: str) -> dict:
    """
    Call Gemini Vision to extract structured visual features.
    Handles JSON parsing defensively.
    """
    image    = PIL.Image.open(image_path)
    model    = genai.GenerativeModel(config.LLM_MODEL)
    response = model.generate_content([EXTRACTION_PROMPT, image])
    text     = response.text.strip()

    # strip markdown if Gemini adds it despite instructions
    if "```" in text:
        for part in text.split("```"):
            part = part.strip().lstrip("json").strip()
            if part.startswith("{"):
                text = part
                break

    features = json.loads(text)

    # ensure all expected keys exist — fill missing with "unknown"
    expected = ["lesion_type", "color", "location", "texture", "pattern", "severity"]
    for key in expected:
        if key not in features or not features[key]:
            features[key] = "unknown"

    return features
