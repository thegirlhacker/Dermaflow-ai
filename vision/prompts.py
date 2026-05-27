import json

EXTRACTION_PROMPT = """You are a clinical dermatology image analyzer.
Look at this skin image and describe ONLY what you visually observe.
Do NOT name any condition or diagnose anything.

Return ONLY a valid JSON object:
{
  "lesion_type":  "primary lesion visible — papule/pustule/plaque/patch/vesicle/crust/scale/nodule/cyst/erythema/comedone/blister/unknown",
  "color":        "dominant color — red/pink/brown/white/skin-colored/dark/silvery/yellow/flushed/unknown",
  "location":     "body area visible — face/forehead/cheek/chin/nose/back/chest/arm/elbow/knee/leg/hand/wrist/neck/scalp/trunk/unknown",
  "texture":      "surface quality — smooth/rough/scaly/bumpy/weeping/crusted/dry/oily/cracked/thick/unknown",
  "pattern":      "distribution — localized/scattered/clustered/diffuse/patchy/linear/symmetric/bilateral/unknown",
  "severity":     "extent of involvement — mild/moderate/severe/unknown"
}

Return ONLY the JSON. No markdown. No explanation."""

def build_response_prompt(
    query:          str,
    features:       dict,
    interpretation: dict,
    chunks:         list[dict]
) -> str:
    context = "\n\n".join([
        f"[Source: {c.get('source', 'unknown')} | "
        f"Condition: {c.get('condition', 'unknown')}]\n{c['text']}"
        for c in chunks
    ])

    tier    = interpretation["tier"]
    message = interpretation["message"]

    if tier == 1:
        guidance = (
            f"The analysis points to {interpretation['conclusion'].replace('_', ' ')}. "
            f"Explain what in the features led to this and provide care guidance."
        )
    else:
        guidance = (
            f"The analysis is inconclusive. "
            f"Explain both possibilities and how they differ clinically."
        )

    return f"""You are DermaFlow AI, a dermatology assistant.

User's Query: {query}

Visual features extracted from the skin image:
{json.dumps(features, indent=2)}

Assessment: {message}

Relevant medical knowledge:
{context}

Provide a concise, focused response formatted neatly as a single cohesive message. 
Do NOT include large blank spaces, gaps between words, or excessive newlines.
Focus ONLY on returning the specific information the user asked for in their query. Do not add unrelated information.

Provide a response that includes:
1. A brief summary of the visual features observed
2. {guidance}
3. The specific information requested by the user, using general skincare and management steps from the knowledge base
4. A clear recommendation to see a dermatologist

End with: "This is not a medical diagnosis. Please consult a qualified dermatologist."
"""
