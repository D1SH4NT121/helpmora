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
    "food", "ration", "rations", "rashan", "nfsa", "aay", "pmgkay", "pm-gkay", "bhojan", "khana", "hungry", "hunger",
    "grain", "grains", "rice", "wheat", "meal", "meals", "grocer", "grocery", "pantry",
    # Housing / Shelter / Hostels
    "housing", "house", "shelter", "hostel", "sakhi niwas", "working women", "working women hostel", "rent", "rental",
    "evict", "eviction", "pmay", "sra", "slum", "jhuggi", "chawl", "homeless", "night shelter", "arhc",
    "accommodation", "room", "kiraya", "makaan", "ghar", "kamra", "basti", "stay", "stay tonight", "nowhere to stay",
    # Healthcare / Medical
    "health", "healthcare", "hospital", "doctor", "medicine", "medicines", "medication", "medical", "treatment",
    "surgery", "ayushman", "pmjay", "pm-jay", "esanjeevani", "ran", "disability", "disabled", "handicap", "divyang",
    "pregnant", "pregnancy", "mental health", "clinic", "dawai", "ilaj", "aspataal", "sick", "illness",
    # Finance / Livelihood / Pensions
    "pension", "subsidy", "subsidies", "income", "poor", "poverty", "mgnrega", "nrega", "wage", "wages", "labor",
    "labour", "kisan", "pm-kisan", "farmer", "farmers", "svanidhi", "street vendor", "jan dhan", "dbt", "nsap",
    "widow", "destitute", "bpl", "ews", "antyodaya", "unemployed", "employment", "job", "work", "rozgar", "rupees", "rupee",
    # Legal Aid & Citizen Rights
    "legal", "legal help", "legal aid", "free legal aid", "lawyer", "court", "justice", "nalsa", "dlsa", "slsa",
    "police", "fir", "complaint", "domestic violence", "human rights", "nhrc", "consumer court", "daakhil", "advocate",
    "vakil", "kanoon", "nyay", "tenant", "bail", "dispute", "harassment", "wage theft", "fraud",
    # Education & Family & Loans
    "school", "scholarship", "scholarships", "education", "study", "loan", "study loan", "education loan", "student loan",
    "college loan", "student", "students", "college", "university", "tuition", "fee", "fees", "admission", "coaching",
    "degree", "vidyalaxmi", "vidya lakshmi", "nsp", "padhai", "shiksha", "chhatravritti", "cgfsel", "higher education",
    "rte", "anganwadi", "children", "child", "kids", "single mother",
    # Identity, Citizenship & Documents
    "citizen", "citizenship", "indian citizen", "indian resident", "resident", "aadhaar", "aadhar", "voter id", "pan card",
    "caste certificate", "income certificate", "domicile", "scheme", "schemes", "program", "programs", "welfare",
    "assistance", "support", "qualify", "benefit", "benefits", "eligibility", "eligible", "portal", "help me",
    "need help", "apply", "how do i apply", "how to apply", "documents", "document", "no documents", "id card"
]

REVERT_WELCOME_REPLY = (
    "I have reverted your submission! You can now freely change your details step by step. "
    "Please tell me what you'd like to update (your income, household members, location, or welfare category), "
    "or navigate through the steps directly in the Guided Welfare Workflow tab."
)

CONVERSATIONAL = [
    "hi", "hello", "hey", "namaste", "namaskar", "good morning", "good afternoon", "good evening",
    "how are you", "help", "help me", "who are you", "what can you do", "what is helpmora",
    "thank you", "thanks", "dhanyawad", "shukriya", "bye", "goodbye", "yes", "no", "ok", "okay",
    "sure", "start", "clear", "reset", "revert", "undo", "back", "cancel", "change"
]

GREETING_PATTERNS = [
    r"^(?:hi+|hey+|hello+|namaste|namaskar|pranam|hola|yo)(?:\s+(?:there|helpmora|assistant|friend))?[\s!.,?]*$",
    r"^(?:(?:hi+|hey+|hello+|namaste)[\s,]+)?(?:how\s+are\s+you|who\s+are\s+you|what\s+(?:is\s+helpmora|can\s+you\s+do|do\s+you\s+do|are\s+you)|how\s+can\s+you\s+help(?:\s+me)?|what\s+is\s+this|tell\s+me\s+about\s+yourself|how\s+does\s+this\s+work)[\s!?.]*$",
    r"^(?:good\s+(?:morning|afternoon|evening|day)|greetings)[\s!.,?]*$",
]

REVERT_PATTERNS = [
    r"\b(?:revert|undo|go\s+back|step\s+back|change\s+(?:my\s+)?(?:idea|mind|details|income|submission)|cancel\s+(?:approval|submission)|modify\s+(?:submission|details|application))\b",
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
    r"\b(?:output of ideas|brainstorm ideas|give me ideas)\b",
]


def is_greeting(text: str) -> bool:
    """Check if message is a greeting or introductory inquiry."""
    s = str(text or "").strip().lower()
    if not s:
        return False
    return any(bool(re.search(pat, s)) for pat in GREETING_PATTERNS)


def is_revert_intent(text: str) -> bool:
    """Check if citizen wants to revert, step back, or change their idea."""
    s = str(text or "").strip().lower()
    if not s:
        return False
    return any(bool(re.search(pat, s)) for pat in REVERT_PATTERNS)


def is_out_of_context(text: str) -> bool:
    """Check if message is outside HELPmora's Indian welfare & legal-aid domain."""
    t = str(text or "").strip().lower()
    if not t:
        return False

    # 1. Greetings, revert requests & conversational inputs are in context
    if is_greeting(t) or is_revert_intent(t):
        return False

    clean_t = re.sub(r"[^\w\s]", "", t).strip()
    if clean_t in CONVERSATIONAL:
        return False

    # 2. Crisis cues and distress indicators must never be flagged as out-of-context
    if re.search(r"\b(?:suicide|kill myself|end my life|die|dead|better off without me|burden|no reason to live|trapped|unbearable|disappear|husband hits me|hits me|abuse|abusive|violence|safe place|nowhere to stay|homeless|shelter|danger|scared|afraid|controls|hurts?)\b", t):
        return False

    # 3. Multilingual script or non-ASCII characters (Chinese, Vietnamese, Cyrillic, Arabic, accented Latin, Devanagari, Tamil, etc.)
    if any(ord(c) > 127 for c in t):
        return False

    # 4. Intake follow-up answers (income numbers, family counts, age, Indian states/cities, citizenship)
    if re.search(r"(?:₹|rs\.?|inr|\$)\s*\d+|\b\d{1,7}\b", t):
        return False
    if re.search(r"\b(?:alone|single|myself|just me|live alone|\d+\s*(?:members?|people|kids|children)|family(?: of \d+)?|household(?: of \d+)?)\b", t):
        return False
    if re.search(r"\b(?:age\s*\d+|\d+\s*years?\s*old)\b", t):
        return False
    if re.search(r"\b(?:delhi|mumbai|bangalore|bengaluru|kolkata|chennai|hyderabad|pune|lucknow|patna|bhopal|jaipur|uttar pradesh|bihar|maharashtra|karnataka|rajasthan|gujarat|punjab|haryana|mp|up|texas|houston|dallas|illinois)\b", t):
        return False
    if re.search(r"\b(?:citizen|citizenship|indian|resident|aadhaar|aadhar|ration|rashan|documents?|no documents|refugee|immigrant)\b", t):
        return False

    # 5. Check for presence of any in-scope welfare / legal / citizen assistance term
    has_welfare = any(re.search(rf"\b{re.escape(w)}\b", t) for w in IN_SCOPE_TERMS)
    if has_welfare:
        return False

    # 6. Check explicit out-of-scope patterns (trivia, coding, math, recipes, entertainment, etc.)
    for pat in OUT_OF_SCOPE_REGEX:
        if re.search(pat, t):
            return True

    # 7. Check encyclopedic questions without welfare context (e.g., "what is photosynthesis")
    if re.search(r"^(?:what|who|where|when|why|how)\s+(?:is|are|was|were|do|does|did)\s+(?:the\s+)?[a-z0-9\s]+[?]?$", t):
        return True

    # 8. Check generic off-topic action requests
    if re.search(r"\b(?:birthday|party|cake|pizza|music|song|lyrics|joke|story|poem|poetry|essay|game|cricket|football|movie|actor|film)\b", t):
        return True

    return False

