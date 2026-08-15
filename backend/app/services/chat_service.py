"""Investigator Copilot: OpenAI-backed with an offline playbook fallback."""

from typing import Any, Dict, List, Optional

import httpx

from ..core.config import settings
from . import legal_service

SYSTEM_PROMPT = (
    "You are CrimeGPT, an investigation copilot for Indian cyber crime officers. "
    "Give concise, procedural guidance referencing BNS/IT Act sections and BNSS procedure. "
    "Never fabricate case facts and always remind the officer to verify legally."
)

PLAYBOOKS: Dict[str, str] = {
    "freeze": (
        "To freeze fraudulent funds: report on the NCRP / 1930 helpline immediately, raise a "
        "lien request with the beneficiary bank's nodal officer, and follow up with a written "
        "request under Section 106 BNSS quoting the UTR numbers."
    ),
    "cdr": (
        "For CDR/subscriber details, send a written request to the telecom nodal officer under "
        "Section 94 BNSS, signed by an officer not below the rank of SP, specifying the exact "
        "number and date range."
    ),
    "seizure": (
        "Seize digital devices with two independent witnesses, hash the media (SHA-256) before "
        "imaging, prepare the seizure memo, and attach the Section 63 BSA certificate."
    ),
    "chargesheet": (
        "The charge sheet must cover: FIR details, investigation steps, seizure memos, forensic "
        "reports, statements recorded under Sections 180/183 BNSS, and the sections invoked."
    ),
}


def _offline_reply(message: str, case_context: Optional[Dict[str, Any]] = None) -> str:
    lowered = message.lower()
    parts: List[str] = []

    if case_context:
        parts.append(
            f"Case {case_context.get('case_number')} — {case_context.get('title')} "
            f"({str(case_context.get('crime_type', '')).replace('_', ' ')}, "
            f"status: {case_context.get('status')})."
        )

    for keyword, playbook in PLAYBOOKS.items():
        if keyword in lowered:
            parts.append(playbook)

    if any(word in lowered for word in ("section", "law", "act", "punish", "legal")):
        crime_type = (case_context or {}).get("crime_type", "other")
        sections = legal_service.recommend_sections(str(crime_type), message)
        parts.append(
            "Applicable sections: "
            + "; ".join(f"{s['act']} {s['section']} - {s['title']}" for s in sections)
        )

    if any(word in lowered for word in ("evidence", "collect", "checklist")):
        crime_type = (case_context or {}).get("crime_type", "other")
        parts.append(
            "Evidence checklist: " + "; ".join(legal_service.evidence_checklist(str(crime_type)))
        )

    if len(parts) <= (1 if case_context else 0):
        parts.append(
            "I can help with legal sections, evidence checklists, fund-freeze steps, CDR requests, "
            "seizure procedure and charge sheet drafting. Ask about any of these, or configure "
            "OPENAI_API_KEY for free-form answers."
        )
    return "\n\n".join(parts)


def _openai_reply(messages: List[Dict[str, str]]) -> str:
    response = httpx.post(
        "https://api.openai.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {settings.OPENAI_API_KEY}"},
        json={
            "model": settings.OPENAI_MODEL,
            "messages": [{"role": "system", "content": SYSTEM_PROMPT}] + messages,
        },
        timeout=60,
    )
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]


def generate_reply(
    message: str,
    history: Optional[List[Dict[str, str]]] = None,
    case_context: Optional[Dict[str, Any]] = None,
) -> Dict[str, str]:
    if settings.OPENAI_API_KEY:
        try:
            context_messages: List[Dict[str, str]] = list(history or [])
            if case_context:
                context_messages.insert(
                    0, {"role": "system", "content": f"Case context: {case_context}"}
                )
            context_messages.append({"role": "user", "content": message})
            return {"reply": _openai_reply(context_messages), "engine": "openai"}
        except Exception:  # noqa: BLE001 - degrade to offline playbooks
            pass
    return {"reply": _offline_reply(message, case_context), "engine": "rule_based"}
