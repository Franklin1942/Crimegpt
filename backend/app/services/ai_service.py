"""AI analysis engine.

Uses OpenAI when ``OPENAI_API_KEY`` is configured and falls back to a
deterministic rule-based engine so the platform is fully usable offline.
"""

import json
import re
from typing import Any, Dict, List

import httpx

from ..core.config import settings
from . import legal_service

CRIME_KEYWORDS: Dict[str, List[str]] = {
    "phishing": ["phishing", "fake link", "fake website", "spoofed email", "credential"],
    "upi_fraud": ["upi", "gpay", "google pay", "phonepe", "paytm", "utr", "qr code"],
    "identity_theft": ["identity theft", "aadhaar", "pan card", "impersonat", "forged id"],
    "malware": ["malware", "virus", "trojan", "spyware", "keylogger"],
    "ransomware": ["ransomware", "encrypted my files", "ransom", "decryption key", "bitcoin ransom"],
    "social_media_fraud": ["facebook", "instagram", "whatsapp", "fake profile", "telegram"],
    "sim_swap": ["sim swap", "sim card", "duplicate sim", "porting", "otp not received"],
    "financial_fraud": ["bank", "credit card", "debit card", "loan", "investment", "trading"],
    "cyber_stalking": ["stalking", "harass", "threaten", "morphed", "obscene"],
    "data_breach": ["data breach", "leaked", "database dump", "exfiltrat", "personal data"],
}

ENTITY_PATTERNS: Dict[str, str] = {
    "emails": r"[\w\.\-+]+@[\w\-]+\.[\w\.\-]+",
    "mobile_numbers": r"(?:(?:\+91[\-\s]?)|0)?[6-9]\d{9}\b",
    "ip_addresses": r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
    "urls": r"https?://[^\s,;)]+",
    "bank_accounts": r"\b\d{9,18}\b",
    "upi_ids": r"\b[\w\.\-]{2,}@(?:okhdfcbank|oksbi|okaxis|okicici|ybl|paytm|upi|apl)\b",
    "amounts": r"(?:Rs\.?|INR|₹)\s?[\d,]+(?:\.\d{1,2})?",
}

DATE_PATTERN = r"\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}-\d{2}-\d{2})\b"


def classify_crime(text: str) -> Dict[str, Any]:
    lowered = text.lower()
    scores = {
        crime: sum(lowered.count(keyword) for keyword in keywords)
        for crime, keywords in CRIME_KEYWORDS.items()
    }
    best_crime, best_score = max(scores.items(), key=lambda item: item[1])
    if best_score == 0:
        return {"crime_type": "other", "confidence": 40, "scores": scores}
    confidence = min(95, 55 + best_score * 10)
    return {"crime_type": best_crime, "confidence": confidence, "scores": scores}


def extract_entities(text: str) -> Dict[str, List[str]]:
    entities: Dict[str, List[str]] = {}
    for name, pattern in ENTITY_PATTERNS.items():
        matches = re.findall(pattern, text, flags=re.IGNORECASE)
        entities[name] = sorted({match.strip() for match in matches})
    # A UPI id also matches the generic email pattern; keep them distinct.
    entities["emails"] = [
        email for email in entities["emails"] if email not in entities["upi_ids"]
    ]
    entities["names"] = sorted(set(re.findall(r"\b(?:Mr|Mrs|Ms|Shri|Smt)\.?\s+([A-Z][a-z]+(?:\s[A-Z][a-z]+)?)", text)))
    return entities


def build_timeline(text: str) -> List[Dict[str, str]]:
    timeline: List[Dict[str, str]] = []
    for sentence in re.split(r"(?<=[.!?])\s+", text):
        match = re.search(DATE_PATTERN, sentence)
        if match:
            timeline.append({"date": match.group(1), "event": sentence.strip()[:280]})
    return timeline


def build_recommendations(crime_type: str, entities: Dict[str, List[str]]) -> List[str]:
    recommendations = [
        f"Register the case under the recommended sections for {crime_type.replace('_', ' ')}.",
        "Preserve all electronic records with hash values and a Section 63 BSA certificate.",
    ]
    if entities.get("mobile_numbers"):
        recommendations.append(
            "Request CDR and subscriber details for: " + ", ".join(entities["mobile_numbers"][:5])
        )
    if entities.get("bank_accounts") or entities.get("upi_ids"):
        recommendations.append(
            "Issue a freeze request to the concerned bank/PSP and report on the NCRP portal within the golden hour."
        )
    if entities.get("ip_addresses"):
        recommendations.append(
            "Seek IP logs from the ISP for: " + ", ".join(entities["ip_addresses"][:5])
        )
    if entities.get("urls"):
        recommendations.append("Capture WHOIS/hosting details and request takedown of the reported URLs.")
    return recommendations


def summarize(text: str, crime_type: str, entities: Dict[str, List[str]]) -> str:
    first_sentences = " ".join(re.split(r"(?<=[.!?])\s+", text.strip())[:3])
    entity_count = sum(len(values) for values in entities.values())
    return (
        f"Classified as {crime_type.replace('_', ' ').title()}. "
        f"{entity_count} entities extracted. {first_sentences}"[:1200]
    )


def _rule_based_analysis(text: str) -> Dict[str, Any]:
    classification = classify_crime(text)
    crime_type = classification["crime_type"]
    entities = extract_entities(text)
    return {
        "crime_type": crime_type,
        "confidence": classification["confidence"],
        "summary": summarize(text, crime_type, entities),
        "entities": entities,
        "timeline": build_timeline(text),
        "recommendations": build_recommendations(crime_type, entities),
        "legal_sections": legal_service.recommend_sections(crime_type, text),
        "engine": "rule_based",
    }


def _openai_analysis(text: str) -> Dict[str, Any]:
    prompt = (
        "You are an investigation assistant for the Indian cyber crime police. "
        "Analyse the case document and reply with JSON containing the keys "
        "crime_type (one of: " + ", ".join(CRIME_KEYWORDS) + ", other), confidence (0-100), "
        "summary, entities (object of string arrays), timeline (array of {date, event}), "
        "recommendations (array of strings)."
    )
    response = httpx.post(
        "https://api.openai.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {settings.OPENAI_API_KEY}"},
        json={
            "model": settings.OPENAI_MODEL,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": prompt},
                {"role": "user", "content": text[:12000]},
            ],
        },
        timeout=60,
    )
    response.raise_for_status()
    payload = json.loads(response.json()["choices"][0]["message"]["content"])
    crime_type = payload.get("crime_type", "other")
    return {
        "crime_type": crime_type,
        "confidence": int(payload.get("confidence", 70)),
        "summary": payload.get("summary", ""),
        "entities": payload.get("entities", {}),
        "timeline": payload.get("timeline", []),
        "recommendations": payload.get("recommendations", []),
        "legal_sections": legal_service.recommend_sections(crime_type, text),
        "engine": "openai",
    }


def analyze_text(text: str) -> Dict[str, Any]:
    """Analyse case text, falling back to the rule-based engine on any AI failure."""
    if not text.strip():
        return {
            "crime_type": "other",
            "confidence": 0,
            "summary": "No readable text found in the document.",
            "entities": {},
            "timeline": [],
            "recommendations": ["Upload a readable document to run the analysis."],
            "legal_sections": [],
            "engine": "rule_based",
        }
    if settings.OPENAI_API_KEY:
        try:
            return _openai_analysis(text)
        except Exception:  # noqa: BLE001 - degrade gracefully to offline engine
            pass
    return _rule_based_analysis(text)
