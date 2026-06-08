"""
nlp_deception_module.py

Text-based deception analysis using Groq's Llama-3.3-70B-versatile.
Detects evasion, over-explanation, irrelevance, contradiction, vagueness,
improbable details, and emotion mismatch with a voice stress score.

Class:
    NLPDeceptionAnalyzer
        analyze(text, voice_stress=0, question_context="", previous_segments=None) -> dict
"""

import sys
import os
import json
import time
import re
import hashlib
from typing import Optional, Dict, Any, List
from pathlib import Path
try:
    from groq import Groq
except ImportError:
    raise ImportError("Please install 'groq' package: pip install groq")

try:
    from dotenv import load_dotenv
    
    # Handle PyInstaller frozen path for .env
    if getattr(sys, 'frozen', False):
        env_path = Path(sys._MEIPASS) / ".env"
    else:
        # Search in the root backend folder (parent of modules/)
        env_path = Path(__file__).resolve().parent.parent / ".env"
        
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
    else:
        load_dotenv() # Fallback to default
except ImportError:
    pass  # python-dotenv not installed


class NLPDeceptionAnalyzer:
    """Uses Groq's LLM to detect deception indicators in a transcript."""

    # Common Urdu/English filler words for cognitive load pre-processing
    FILLER_WORDS = {
        'umm', 'uhh', 'uh', 'ah', 'er', 'hmm', 'like', 'actually', 'basically',
        'essentially', 'literally', 'honestly', 'truthfully', 'frankly',
        'you know', 'i mean', 'sort of', 'kind of', 'well', 'so', 'anyway',
        'um', 'ahem', 'err', 'hmmm', 'yeah', 'mmm',
        'matlab', 'mtlb', 'yani', 'yaani', "ya'ni", 'arey', 'arre',
        'achha', 'accha', 'theek hai', 'dekho', 'sunno', 'jaanay do',
        'kya kehna', 'fir', 'phir', 'toh', 'to', 'haan', 'nahi'
    }

    FILLER_REGEX = re.compile(
        r'\b(' + '|'.join(re.escape(w) for w in FILLER_WORDS) + r')\b',
        re.IGNORECASE
    )

    def __init__(self, api_key: Optional[str] = None):
        """Initialize with Groq API key.

        Args:
            api_key: If None, reads from environment variable GROQ_API_KEY.
        """
        self.api_key = api_key or os.environ.get("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Groq API key not provided. Set GROQ_API_KEY environment variable "
                "or pass api_key to constructor."
            )
        self.client = Groq(api_key=self.api_key)
        self.model = "llama-3.3-70b-versatile"
        self.temperature = 0.1
        # Simple in-memory cache: keyed by text hash
        self._cache: Dict[str, Dict[str, Any]] = {}

    def analyze(
        self, text: str, voice_stress: float = 0, question_context: str = "",
        previous_segments: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Analyze a transcript for deception indicators.

        Args:
            text: The transcript (can be English, Roman Urdu, or Urdu).
            voice_stress: Score from 0 to 100 from external voice stress module.
            question_context: Optional question that was asked (for context).
            previous_segments: List of previous segment data dicts (each containing
                'transcript_original', 'transcript_english', and optionally 'question')
                for cross-segment contradiction detection.

        Returns:
            A dict with all deception indicators, translations, and overall score.
        """
        if not text.strip():
            return self._unanalyzable_result("Empty input.")

        # Cache check
        cache_key = hashlib.md5(text.strip().lower().encode()).hexdigest()
        if cache_key in self._cache:
            return self._cache[cache_key].copy()

        # Pre-process text: count filler words, build cleaned version
        processed = self._preprocess_text(text)

        # Build the prompt with few-shot examples and optional cross-segment context
        prompt = self._build_prompt(
            text, voice_stress, question_context, processed, previous_segments
        )

        # Call Groq API with retries
        response_json = self._call_groq_with_retries(prompt)

        if response_json is None:
            return self._unanalyzable_result("API call failed.")

        # Parse and validate
        result = self._parse_response(response_json, text)

        # Inject pre-processing insights (filler count, cognitive load baseline)
        if result.get('is_analyzable', False):
            self._inject_preprocessing_insights(result, processed)

        # Cache and return
        self._cache[cache_key] = result.copy()
        return result

    # ------------------------------------------------------------------
    #   Text Pre-processing
    # ------------------------------------------------------------------
    def _preprocess_text(self, text: str) -> Dict[str, Any]:
        """Count filler words, measure sentence length, return metadata."""
        cleaned = self.FILLER_REGEX.sub('', text)
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        filler_matches = self.FILLER_REGEX.findall(text)
        raw_words = text.split()
        cleaned_words = cleaned.split() if cleaned else []
        avg_sentence_len = 0
        sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
        if sentences:
            avg_sentence_len = sum(len(s.split()) for s in sentences) / len(sentences)
        return {
            'filler_count': len(filler_matches),
            'filler_density': round(len(filler_matches) / max(len(raw_words), 1) * 100, 1),
            'avg_sentence_length': round(avg_sentence_len, 1),
            'word_count': len(raw_words),
            'cleaned_word_count': len(cleaned_words),
        }

    def _inject_preprocessing_insights(self, result: Dict, processed: Dict) -> None:
        """Boost cognitive_load score based on actual filler density."""
        ind = result.get('deception_indicators', {})
        cl = ind.get('cognitive_load', {})
        # Base score from LLM, but boost if filler density is high
        filler_boost = min(40, int(processed['filler_density'] * 2))
        new_score = min(100, cl.get('score', 0) + filler_boost)
        cl['score'] = new_score
        cl['flagged'] = new_score > 60
        if new_score > 60 and 'cognitive_load' not in result.get('triggered_flags', []):
            result.setdefault('triggered_flags', []).append('cognitive_load')
        # Very long sentences also contribute
        if processed['avg_sentence_length'] > 25:
            cl['score'] = min(100, cl['score'] + 10)
            cl['flagged'] = cl['score'] > 60

    # ------------------------------------------------------------------
    #   Prompt Building
    # ------------------------------------------------------------------
    def _build_prompt(self, text: str, voice_stress: float, question: str,
                      processed: Dict, previous_segments: Optional[List[Dict]] = None) -> str:
        """Construct the system + user prompt with few-shot examples and optional cross-segment context."""

        # Build cross-segment contradiction context
        cross_context = ""
        if previous_segments and len(previous_segments) > 0:
            prev_lines = []
            for i, seg in enumerate(previous_segments[-3:]):  # Last 3 segments only
                prev_q = seg.get('question', {})
                q_text = prev_q.get('text', '') if isinstance(prev_q, dict) else ''
                a_text = seg.get('transcript_english', '') or seg.get('transcript_original', '')
                if a_text:
                    line = f"  Segment {i+1}: "
                    if q_text:
                        line += f"Q: \"{q_text}\" "
                    line += f"A: \"{a_text[:200]}\""
                    prev_lines.append(line)
            if prev_lines:
                cross_context = "Previous answers by this subject:\n" + "\n".join(prev_lines)

        # Pre-processing stats
        pre_stats = (
            f"Pre-processing stats: "
            f"filler_words_count={processed['filler_count']}, "
            f"filler_density={processed['filler_density']}%, "
            f"avg_sentence_length={processed['avg_sentence_length']} words, "
            f"total_words={processed['word_count']}"
        )

        sys_msg = (
            "You are a forensic linguistics expert analyzing a transcript for deception. "
            "Your task is to output a single JSON object with the following fields:\n"
            "- translated_urdu: Roman Urdu translation of the text (if already Roman Urdu, keep it as-is)\n"
            "- translated_english: English translation of the text\n"
            "- language_detected: one of 'english', 'roman_urdu', 'urdu'\n"
            "- deception_indicators: object with eight sub-objects (evasion, over_explanation, "
            "irrelevance, contradiction, vagueness, improbable_details, cognitive_load, distancing_language), each containing:\n"
            "    'score': integer 0-100, 'flagged': boolean (true if score > 60), "
            "'confidence': one of 'high', 'medium', 'low'\n"
            "- emotion_mismatch: object with 'score' (integer 0-100) and 'flagged' (boolean). "
            "Set score>60 only if voice_stress>70 but text claims calm/normal.\n"
            "- overall_deception_score: integer 0-100, average of all indicator scores plus a bonus from emotion mismatch (max 100)\n"
            "- triggered_flags: list of indicator names that were flagged\n"
            "- summary: A forensic linguistic analysis in BOTH English AND Roman Urdu. The Roman Urdu part MUST come after the English part. Explain *how* the person is speaking. For example: 'Subject is using distancing language and high cognitive load while over-explaining trivial details to build false credibility. Roman Urdu: Ye shaks doori ki zabaan istemal kar raha hai aur zyada explanatory details de raha hai jhoot ko sach dikhane ke liye.'\n"
            "- is_analyzable: boolean. False for greetings, single words, incomplete sentences, or pure filler. True otherwise.\n"
            "\nIndicator definitions WITH examples:\n"
            "\n1. Evasion (score 0-100): NOT answering the question directly. Changing topic, answering a different question, or giving a non-answer.\n"
            "   - Example (HIGH): Q: \"Did you take the money?\" A: \"I have been working here for 10 years without any problems.\" → evasion=80\n"
            "   - Example (LOW): Q: \"Did you take the money?\" A: \"No, I did not take the money.\" → evasion=0\n"
            "\n2. Over-explanation (score 0-100): Unnecessary details provided to build false credibility. Too much irrelevant specificity.\n"
            "   - Example (HIGH): \"I was at home watching Netflix, Stranger Things season 3 episode 4, at exactly 9:15 PM, and I had popcorn too.\" → over_explanation=75\n"
            "   - Example (LOW): \"I was at home watching TV.\" → over_explanation=5\n"
            "\n3. Irrelevance (score 0-100): Off-topic or semantic drift. Bringing up unrelated subjects.\n"
            "   - Example (HIGH): Q: \"Where were you last night?\" A: \"My cousin got a new job last week and they are paying really well.\" → irrelevance=85\n"
            "\n4. Contradiction (score 0-100): Self-contradiction WITHIN the current response. (Cross-segment contradictions are handled separately.)\n"
            "   - Example (HIGH): \"I was alone in my room. My friend was with me the whole time.\" → contradiction=90\n"
            "\n5. Vagueness (score 0-100): Hedge words like 'maybe', 'I think', 'probably', 'kind of', 'around', 'approximately', 'sort of', 'could be'.\n"
            "   - Example (HIGH): \"I think it was around midnight, maybe 11 or 12, probably near the parking lot somewhere.\" → vagueness=80\n"
            "   - Example (LOW): \"It was 11:30 PM in the main parking lot.\" → vagueness=0\n"
            "\n6. Improbable details (score 0-100): Too-specific timestamps, perfect memory of trivial things, unlikely precision.\n"
            "   - Example (HIGH): \"I remember it was exactly 9:15 PM and 37 seconds when I opened the refrigerator to get a glass of water.\" → improbable_details=85\n"
            "\n7. Cognitive Load (score 0-100): High use of filler words (umm, uhh, actually, like) and unusually long, rambling sentences as the subject struggles to invent or maintain a false story.\n"
            "   - Example (HIGH): \"Well, umm, actually, you know, I was, like, basically at the, umm, office until around, like, 9-ish maybe?\" → cognitive_load=80\n"
            "\n8. Distancing Language (score 0-100): Avoiding personal pronouns (I, me, my). Using impersonal language to detach from the lie.\n"
            "   - Example (HIGH): \"The person arrived at the location. That individual was seen entering the building.\" instead of \"I arrived at the location.\" → distancing_language=75\n"
            "   - Example (LOW): \"I arrived at the location and I entered the building.\" → distancing_language=0\n"
            "\nEmotion mismatch: only flag if voice_stress > 70 but text claims calm/normal.\n"
            "Be objective. Use 'confidence' level to indicate how sure you are about each indicator. "
            "Respond ONLY with the JSON object, no extra text."
        )

        user_parts = [
            f"Transcript: \"{text}\"",
            pre_stats,
            f"Voice stress score (0-100): {voice_stress}" if voice_stress else "",
            f"Question context: \"{question}\"" if question else "",
        ]
        if cross_context:
            user_parts.append(cross_context)

        user_msg = "\n".join(filter(None, user_parts))

        return f"System: {sys_msg}\nUser: {user_msg}"

    def _call_groq_with_retries(self, prompt: str, max_retries: int = 2) -> Optional[str]:
        """Call Groq API and return raw JSON string. Retries on failure."""
        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "user", "content": prompt},
                    ],
                    temperature=self.temperature,
                    max_tokens=2048,
                )
                content = response.choices[0].message.content.strip()
                # Remove markdown code fences if present
                if content.startswith("```"):
                    content = content.strip("`")
                    if content.startswith("json"):
                        content = content[4:]
                    content = content.strip()
                return content
            except Exception as e:
                print(f"Groq API attempt {attempt+1} failed: {e}")
                time.sleep(2 ** attempt)  # simple backoff
        print("All Groq API retries exhausted.")
        return None

    def _parse_response(self, json_str: str, original_text: str) -> Dict[str, Any]:
        """Parse the LLM JSON output and return a clean result dict."""
        try:
            data = json.loads(json_str)
        except json.JSONDecodeError:
            print("Failed to parse LLM response. Falling back.")
            return self._unanalyzable_result("Invalid JSON from API.")

        # Enforce required fields
        if "deception_indicators" not in data or "is_analyzable" not in data:
            return self._unanalyzable_result("Missing fields in API response.")

        # If not analyzable, zero out scores
        if not data.get("is_analyzable", False):
            return self._unanalyzable_result("Text not suitable for analysis.", data)

        # Normalize scores: ensure integers 0-100
        indicators = data["deception_indicators"]
        expected_keys = (
            "evasion", "over_explanation", "irrelevance", "contradiction",
            "vagueness", "improbable_details", "cognitive_load", "distancing_language"
        )
        for key in expected_keys:
            if key in indicators:
                indicators[key]["score"] = max(0, min(100, int(indicators[key].get("score", 0))))
                indicators[key]["flagged"] = indicators[key]["score"] > 60
                indicators[key].setdefault("confidence", "medium")
            else:
                indicators[key] = {"score": 0, "flagged": False, "confidence": "low"}

        # Emotion mismatch
        mismatch = data.get("emotion_mismatch", {})
        mismatch["score"] = max(0, min(100, int(mismatch.get("score", 0))))
        mismatch["flagged"] = mismatch["score"] > 60
        data["emotion_mismatch"] = mismatch

        # Overall score = average of indicators + extra from mismatch (simple bonus)
        indicator_scores = [indicators[k]["score"] for k in indicators]
        avg_score = sum(indicator_scores) / len(indicator_scores) if indicator_scores else 0
        # Add mismatch bonus: up to 20 extra points proportionally
        bonus = min(20, mismatch["score"] * 0.2)
        overall = min(100, round(avg_score + bonus))
        data["overall_deception_score"] = overall

        # Triggered flags
        triggered = [k for k, v in indicators.items() if v["flagged"]]
        if mismatch["flagged"]:
            triggered.append("emotion_mismatch")
        data["triggered_flags"] = triggered

        # Ensure summary and translations exist
        data.setdefault("translated_urdu", original_text)
        data.setdefault("translated_english", original_text)
        data.setdefault("language_detected", "unknown")
        data.setdefault("summary", f"Roman Urdu: {original_text[:100]}... | English: {original_text[:100]}...")

        return data

    def _unanalyzable_result(self, reason: str, partial: Optional[Dict] = None) -> Dict[str, Any]:
        """Return a default result when analysis is impossible."""
        base = {
            "translated_urdu": "",
            "translated_english": "",
            "language_detected": "unknown",
            "deception_indicators": {
                "evasion": {"score": 0, "flagged": False, "confidence": "low"},
                "over_explanation": {"score": 0, "flagged": False, "confidence": "low"},
                "irrelevance": {"score": 0, "flagged": False, "confidence": "low"},
                "contradiction": {"score": 0, "flagged": False, "confidence": "low"},
                "vagueness": {"score": 0, "flagged": False, "confidence": "low"},
                "improbable_details": {"score": 0, "flagged": False, "confidence": "low"},
                "cognitive_load": {"score": 0, "flagged": False, "confidence": "low"},
                "distancing_language": {"score": 0, "flagged": False, "confidence": "low"},
            },
            "emotion_mismatch": {"score": 0, "flagged": False},
            "overall_deception_score": 0,
            "triggered_flags": [],
            "summary": "Text not suitable for analysis.",
            "is_analyzable": False,
        }
        if partial:
            base.update({k: v for k, v in partial.items() if k in base})
        return base


# -------------------------------------------------------------------------
#   Example usage
# -------------------------------------------------------------------------
if __name__ == "__main__":
    analyzer = NLPDeceptionAnalyzer()  # requires GROQ_API_KEY env var

    # Example test
    sample_text = (
        "Main ghar par tha, Netflix dekh raha tha, Stranger Things season 3 episode 4, "
        "bilkul 9:15 baje, aur mere paas popcorn bhi tha"
    )
    question = "Tum kal raat kahan the?"
    result = analyzer.analyze(sample_text, voice_stress=20, question_context=question)

    print(json.dumps(result, indent=2, ensure_ascii=False))