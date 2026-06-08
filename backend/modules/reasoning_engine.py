"""
reasoning_engine.py

Generates human‑readable deception reasoning using Groq LLM.

Class:
    ReasoningEngine
        explain(segment_data) -> str
"""

import os
import json
import time
from typing import Dict, Any

try:
    from groq import Groq
except ImportError:
    raise ImportError("Please install 'groq' package: pip install groq")


class ReasoningEngine:
    """Produces a natural‑language explanation for a deceptive segment."""

    def __init__(self, api_key=None):
        self.api_key = api_key or os.environ.get("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("Set GROQ_API_KEY env variable or pass api_key.")
        self.client = Groq(api_key=self.api_key)
        self.model = "llama-3.3-70b-versatile"

    def explain(self, segment_data: Dict[str, Any]) -> str:
        """Generate an explanation string.

        Args:
            segment_data: dict containing:
                - text: transcribed answer
                - face_cues: dict with aggregated behavioural metrics
                - voice_stress: dict with voice stress features
                - nlp_flags: list of triggered NLP deception flags
                - start_time, end_time: timestamp

        Returns:
            A human‑readable string explaining why this segment may indicate deception.
        """
        prompt = self._build_prompt(segment_data)
        for attempt in range(2):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system", 
                            "content": (
                                "You are an Elite Forensic Deception Analyst. Your job is to analyze multi-modal "
                                "forensic data (visual, vocal, and linguistic) to explain deceptive patterns. "
                                "You must act as a psychological expert who translates raw numbers into "
                                "clear, human-readable forensic insights."
                            )
                        },
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3,
                    max_tokens=600,
                )
                explanation = response.choices[0].message.content.strip()
                return explanation
            except Exception as e:
                print(f"Groq API attempt {attempt+1} failed: {e}")
                time.sleep(2 ** attempt)
        return "Could not generate explanation due to API error."

    def _build_prompt(self, data: Dict) -> str:
        # We pass the full nested data so the AI sees all scores
        full_data_json = json.dumps(data, indent=2)

        prompt = f"""
ANALYZE THIS FORENSIC DATA AND PROVIDE A BLUNT VERDICT:
------------------------------------------------------
{full_data_json}

TASK:
You are an expert Deception Catcher. Analyze the raw scores above and explain exactly WHY this person is lying or telling the truth.

If a 'question' field is present, ALWAYS check if the answer directly addresses the question. Evasion or deflection is a strong deception signal.

RULES:
1. Be DIRECT and REALISTIC. Mention specific scores (e.g., "The Voice Stress is 75%, which is critical").
2. Don't be "academic". Talk like a real investigator. (e.g., "This person is clearly hiding something because...")
3. Provide a FINAL VERDICT (e.g., "HIGHLY DECEPTIVE" or "TRUTHFUL").
4. Provide the analysis in both ENGLISH and ROMAN URDU.

REQUIRED OUTPUT FORMAT:
VERDICT: [TRUTHFUL / SUSPICIOUS / DECEPTIVE]
ENGLISH: [Detailed investigation report. Explain the mismatch between voice, face, and words. Mention the question context and whether the answer evades it.]
ROMAN URDU: [Direct explanation: "Ye banda jhoot bol raha hai kyunke..." or "Ye sach bol raha hai..."]

GUIDELINES:
- Use the data facts. If 'touch_score' is 100, say they touched their face. If 'blink_rate_spike' is true, mention it.
- Explain the psychological "Why" (e.g., 'High jaw tightness 80% shows they are suppressing anger/fear').
"""
        return prompt


# ---------------------------------------------------------------------
# Example usage
# ---------------------------------------------------------------------
if __name__ == "__main__":
    engine = ReasoningEngine()
    sample = {
        'text': "I was at home, watching Netflix, exactly at 9:15 PM, Stranger Things season 3 episode 4, and I had popcorn.",
        'face_cues': {
            'jaw_tightness': 78,
            'lip_compression': 82,
            'hand_touch': {'touched': True, 'region': 'NOSE'}
        },
        'voice_stress': {
            'jitter': 2.1,
            'pitch_std': 12,
            'pause_ratio': 35
        },
        'nlp_flags': ['over_explanation', 'improbable_details'],
        'start_time': 25.0,
        'end_time': 33.5
    }
    print(engine.explain(sample))