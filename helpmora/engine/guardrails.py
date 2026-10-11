"""Domain Context Guardrails for HELPmora.

Ensures the agent answers strictly within the domain of Indian Social Welfare,
Government Assistance Schemes, and Free Legal Aid Navigation.
"""

import re
from typing import Tuple

OUT_OF_CONTEXT_REPLY = (
    "I don't have knowledge of those things. I am HELPmora, specialized exclusively in "
    "Indian social welfare schemes, government assistance programs, and free legal aid navigation. "
    "Please ask me about welfare programs, subsidies, pensions, housing, healthcare, rations, or legal support in India."
)

GREETING_WELCOME_REPLY = (
    "Hello and welcome! I am HELPmora, your digital assistant for Indian social welfare schemes and free legal aid.\n\n"
    "Here is how I can help you:\n"
    "• Food & Rations: Find NFSA ration cards, Antyodaya Anna Yojana, and grain subsidies.\n"
    "• Housing & Shelter: Check eligibility for Pradhan Mantri Awas Yojana (PMAY) and shelter homes.\n"
    "• Healthcare: Navigate free hospital treatment under Ayushman Bharat (PM-JAY).\n"
    "• Pensions & Income: Explore NSAP old age/widow pensions, PM-KISAN farmer support, and MGNREGA work.\n"
    "• Free Legal Aid: Connect with NALSA/DLSA legal aid lawyers, consumer redressal, and human rights aid.\n\n"
    "Tell me about your situation or what support you are looking for, and I will find the right programs for you!"
)

IN_SCOPE_TERMS = [
    # Food / Nutrition
    "food", "ration", "rations", "rashan", "nfsa", "bhojan", "khana", "hungry", "hunger", "grain", "rice", "wheat",
    # Housing / Shelter
    "housing", "house", "shelter", "rent", "rental", "evict", "eviction", "pmay", "sra", "slum", "jhuggi", "chawl",
    "homeless", "night shelter", "arhc", "accommodation", "room", "kiraya", "makaan", "ghar",
    # Healthcare / Medical
    "health", "healthcare", "hospital", "doctor", "medicine", "medical", "treatment", "surgery", "ayushman", "pmjay",
    "disability", "disabled", "handicap", "divyang", "pregnant", "pregnancy", "mental health", "clinic",
    # Finance / Livelihood / Pensions
    "pension", "subsidy", "subsidies", "income", "poor", "poverty", "mgnrega", "nrega", "wage", "wages", "labor",
    "labour", "kisan", "pm-kisan", "farmer", "svanidhi", "street vendor", "jan dhan", "dbt", "nsap", "widow",
    "destitute", "bpl", "ews", "antyodaya", "unemployed", "employment", "job", "work",
    # Legal Aid & Citizen Rights
    "legal", "lawyer", "court", "justice", "nalsa", "dlsa", "slsa", "police", "fir", "complaint", "domestic violence",
    "human rights", "nhrc", "consumer court", "daakhil", "advocate", "tenant", "bail", "dispute", "harassment",
    # Education & Family
    "school", "scholarship", "education", "rte", "anganwadi", "children", "child", "kids", "single mother",
    # Identity & Documents
    "aadhaar", "aadhar", "voter id", "pan card", "caste certificate", "income certificate", "domicile", "scheme",
    "schemes", "program", "programs", "welfare", "assistance", "support", "qualify", "benefit", "benefits",
    "eligibility", "portal", "help me", "need help", "apply"
]

CONVERSATIONAL = [
    "hi", "hello", "hey", "namaste", "namaskar", "good morning", "good afternoon", "good evening",
    "how are you", "help", "help me", "who are you", "what can you do", "what is helpmora",
    "thank you", "thanks", "dhanyawad", "shukriya", "bye", "goodbye", "yes", "no", "ok", "okay",
    "sure", "start", "clear", "reset"
]

GREETING_PATTERNS = [
    r"^(?:hi+|hey+|hello+|namaste|namaskar|pranam|hola|yo)(?:\s+(?:there|helpmora|assistant|friend))?[\s!.,?]*$",
    r"^(?:(?:hi+|hey+|hello+|namaste)[\s,]+)?(?:who\s+are\s+you|what\s+(?:is\s+helpmora|can\s+you\s+do|do\s+you\s+do|are\s+you)|how\s+can\s+you\s+help(?:\s+me)?|what\s+is\s+this|tell\s+me\s+about\s+yourself|how\s+does\s+this\s+work)[\s!?.]*$",
    r"^(?:good\s+(?:morning|afternoon|evening|day)|greetings)[\s!.,?]*$",
]

OUT_OF_SCOPE_REGEX = [
    r"\b(?:what is|who is|where is|tell me about)\s+(?:the\s+)?capital\b",
    r"\b(?:capital of|currency of|population of|president of|prime minister of)\b",
    r"\b(?:who (?:invented|discovered|wrote|directed|won|is the ceo of))\b",
    r"\b(?:recipe for|how to cook|how to make)\s+(?:biryani|cake|pizza|pasta|tea|coffee)\b",
    r"\b(?:write (?:a|an)\s+)?(?:poem|poetry|song|lyrics|story|joke|essay|code|script|program|python function|function)\b",
    r"\b(?:python|javascript|java|c\+\+|html|css|sql|function|algorithm)\b",
    r"\b(?:calculate|solve|what is \d+[\+\-\*\/]\d+)\b",
    r"\b(?:movie|cricket|football|world cup|olympics|actor|actress|celebrity)\b",
    r"\b(?:weather in|temperature in|forecast)\b",
    r"\b(?:tallest building|highest mountain|longest river|fastest car)\b",
]


def is_greeting(text: str) -> bool:
    """Check if message is a greeting or introductory inquiry."""
    s = str(text or "").strip().lower()
    if not s:
        return False
    return any(bool(re.search(pat, s)) for pat in GREETING_PATTERNS)


def is_out_of_context(text: str) -> bool:
    """Check if message is outside HELPmora's Indian welfare & legal-aid domain."""
    t = str(text or "").strip().lower()
    if not t:
        return False

    # 1. Greetings & conversational inputs are in context
    if is_greeting(t):
        return False

    clean_t = re.sub(r"[^\w\s]", "", t).strip()
    if clean_t in CONVERSATIONAL:
        return False

    # 2. Check explicit out-of-scope patterns (trivia, coding, math, recipes, etc.)
    for pat in OUT_OF_SCOPE_REGEX:
        if re.search(pat, t):
            has_welfare = any(re.search(rf"\b{re.escape(w)}\b", t) for w in IN_SCOPE_TERMS)
            if not has_welfare:
                return True

    # 3. Check general fact questions without any welfare or distress terms
    if re.search(r"\b(?:what is|who is|where is|how does|why is|tell me about)\b", t):
        has_welfare = any(re.search(rf"\b{re.escape(w)}\b", t) for w in IN_SCOPE_TERMS)
        if not has_welfare:
            return True

    return False
