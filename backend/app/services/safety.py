import re
from typing import Tuple, Optional, Dict, Any

class SafetyGuard:
    # Emergency medical triggers in English and Hindi (Devanagari and transliterated)
    EMERGENCY_PATTERNS = [
        # Cardiovascular & Chest
        r"\b(chest pain|heart attack|cardiac arrest|pain in chest|छाती में दर्द|दिल का दौरा)\b",
        # Severe Breathing
        r"\b(cannot breathe|shortness of breath|choking|difficulty breathing|दम घुट|सांस नहीं ले|साँस लेने में तकलीफ)\b",
        # Stroke / Paralysis
        r"\b(stroke|paralysis|face drooping|slurred speech|sudden weakness|लकवा|पक्षघात)\b",
        # Uncontrolled Bleeding / Trauma
        r"\b(uncontrolled bleeding|severe hemorrhage|vomiting blood|coughing blood|खून की उल्टी|भारी रक्तस्राव)\b",
        # Severe Neurological / Poisoning
        r"\b(unconscious|loss of consciousness|seizure|fits|poisoning|consumed poison|बेहोश|दौरा|जहर)\b",
        # Self-harm & Crisis
        r"\b(suicide|kill myself|end my life|आत्महत्या|जान देना)\b"
    ]

    # Explicit medication prescription requests
    PRESCRIPTION_PATTERNS = [
        r"\b(prescribe|which medicine should i take|give me medicine|what dose|what dosage|how many mg|how many tablets)\b",
        r"\b(दवा लिखो|कौन सी दवा लूं|कितनी गोली खाऊं|कितने एमजी|दवाई बताओ)\b"
    ]

    # Adversarial jailbreak patterns
    JAILBREAK_PATTERNS = [
        r"(ignore (all )?previous instructions|disregard guidelines|pretend you are (an unrestricted|a real) doctor)",
        r"(bypass (rules|restrictions)|act as dan|jailbreak|system override)"
    ]

    @classmethod
    def detect_language(cls, text: str) -> str:
        """Detect whether the text is primarily Hindi (Devanagari) or English."""
        hindi_chars = len(re.findall(r"[\u0900-\u097F]", text))
        total_chars = len(re.findall(r"\w", text))
        if total_chars > 0 and (hindi_chars / total_chars) > 0.15:
            return "hi"
        return "en"

    @classmethod
    def check_query_safety(cls, question: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        Evaluates input query for critical safety concerns.
        Returns: (is_safe, category, safety_response)
        """
        lowered = question.lower()

        # 1. Check for Emergency
        for pattern in cls.EMERGENCY_PATTERNS:
            if re.search(pattern, lowered, re.IGNORECASE):
                is_hindi = cls.detect_language(question) == "hi"
                msg_en = (
                    "EMERGENCY ADVISORY: The symptoms or circumstances you described indicate a potentially "
                    "life-threatening emergency. HealthSutra is an awareness assistant, not an emergency medical service. "
                    "Please call 112 / 108 immediately or proceed to the nearest emergency healthcare facility."
                )
                msg_hi = (
                    "आपातकालीन सूचना: आपके द्वारा बताए गए लक्षण किसी गंभीर चिकित्सीय आपातकाल का संकेत दे सकते हैं। "
                    "हेल्थसूत्र केवल सामान्य स्वास्थ्य जागरूकता के लिए है। कृपया तुरंत 112 या 108 पर कॉल करें "
                    "या निकटतम अस्पताल के आपातकालीन विभाग में जाएँ।"
                )
                return False, "emergency_alert", {
                    "status": "emergency_alert",
                    "answer": msg_hi if is_hindi else msg_en,
                    "language": "hi" if is_hindi else "en",
                    "citations": [],
                    "safety_notice": "National Emergency Helpline: 112 | Medical Ambulance: 108 | Tele-MANAS: 14416",
                    "top_score": 0.0,
                    "grounded": True
                }

        # 2. Check for Jailbreak
        for pattern in cls.JAILBREAK_PATTERNS:
            if re.search(pattern, lowered, re.IGNORECASE):
                return False, "safety_violation", {
                    "status": "safety_violation",
                    "answer": "HealthSutra operates exclusively under strict verified public health guidelines and cannot alter its safety protocols.",
                    "language": "en",
                    "citations": [],
                    "safety_notice": "Adversarial instructions and role-play bypasses are prohibited.",
                    "top_score": 0.0,
                    "grounded": True
                }

        return True, "safe", None

    @classmethod
    def check_prescription_request(cls, question: str) -> bool:
        """Check if user is asking for specific drug prescription or dosage."""
        lowered = question.lower()
        for pattern in cls.PRESCRIPTION_PATTERNS:
            if re.search(pattern, lowered, re.IGNORECASE):
                return True
        return False
