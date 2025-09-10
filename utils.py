# utils.py
import re
import random
from typing import List, Dict, Tuple

MANIPULATION_RULES = {
    "guilt-tripping": ["after all", "because i", "you owed me", "you owe me", "you should have"],
    "flattery": ["you're the only one", "you're the best", "no one else like you", "only you can"],
    "fear-pressure": ["if you don't", "or else", "you will regret", "you'll regret"],
}

ACCEPTANCE_KEYWORDS = ["okay", "ok", "fine", "i'll", "i will", "sure", "alright", "accepted", "yes"]

# Helper: normalize text
def _norm(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())

def preprocess_chat(chat_text: str) -> List[Dict[str, str]]:
    """
    Convert a pasted chat export into a list of {"speaker": "A", "text": "..."}.
    Handles lines like:
      "A: message here"
      "B: message here"
    If no explicit speaker found, marks speaker as "Unknown".
    """
    lines = chat_text.splitlines()
    messages = []
    speaker_pattern = re.compile(r'^\s*([A-Za-z0-9_]+)\s*:\s*(.+)$')  # e.g., "A: Hello" or "Alice: Hello"

    for raw in lines:
        line = raw.strip()
        if not line:
            continue
        m = speaker_pattern.match(line)
        if m:
            speaker = m.group(1)
            text = m.group(2)
        else:
            # No speaker label — mark as Unknown but keep the line
            speaker = "Unknown"
            text = line
        messages.append({"speaker": speaker, "text": text})
    return messages

def analyze_message(text: str) -> Tuple[str, float, str]:
    """
    Rule-based detection:
      - If contains phrases from MANIPULATION_RULES -> corresponding label
      - Else neutral
    Returns (label, confidence, explanation)
    Confidence is random between 0.7 and 0.95 for demo.
    """
    n = _norm(text)
    for label, triggers in MANIPULATION_RULES.items():
        for trig in triggers:
            if trig in n:
                confidence = round(random.uniform(0.7, 0.95), 2)
                explanation = f"Phrase '{trig}' detected; suggests {label.replace('-', ' ')}."
                return label, confidence, explanation

    # nothing matched -> neutral
    confidence = round(random.uniform(0.7, 0.95), 2)
    return "neutral", confidence, "No manipulation keyword detected."

def analyze_chat(messages: List[Dict[str, str]]) -> Dict:
    """
    Analyze a list of messages (each: {"speaker","text"}) and return structured result.
    Also attempts a simple 'pressured acceptance' heuristic:
      - if a message contains an acceptance keyword and previous message (other speaker)
        was labeled manipulative, mark this message 'pressured acceptance'.
    Influence score = manipulative_messages_count / total_messages
    """
    analyzed = []
    manipulative_count = 0
    prev_analysis = None

    for i, msg in enumerate(messages):
        speaker = msg.get("speaker", "Unknown")
        text = msg.get("text", "")
        label, confidence, explanation = analyze_message(text)

        # Simple "pressured acceptance" detection:
        n_text = _norm(text)
        contains_acceptance = any(k in n_text for k in ACCEPTANCE_KEYWORDS)
        if contains_acceptance and prev_analysis and prev_analysis["label"] != "neutral" and prev_analysis["speaker"] != speaker:
            # mark as pressured acceptance instead of neutral/other
            label = "pressured acceptance"
            confidence = round(random.uniform(0.75, 0.97), 2)
            explanation = (
                "Message contains acceptance keywords and was preceded by a manipulative message "
                f"from {prev_analysis['speaker']}. This suggests pressured acceptance."
            )

        if label != "neutral":
            manipulative_count += 1

        analysis = {
            "speaker": speaker,
            "text": text,
            "label": label,
            "confidence": confidence,
            "explanation": explanation,
        }
        analyzed.append(analysis)
        prev_analysis = analysis

    total = max(len(messages), 1)
    influence_score = round(manipulative_count / total, 2)

    return {"messages": analyzed, "influence_score": influence_score}
