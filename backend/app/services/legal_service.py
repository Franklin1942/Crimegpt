"""Legal intelligence: maps crime types to BNS / IT Act sections."""

from typing import Any, Dict, List

BNS_SECTIONS: Dict[str, List[Dict[str, Any]]] = {
    "phishing": [
        {"act": "BNS", "section": "318(4)", "title": "Cheating and dishonestly inducing delivery of property"},
        {"act": "BNS", "section": "319(2)", "title": "Cheating by personation"},
        {"act": "IT Act", "section": "66C", "title": "Identity theft"},
        {"act": "IT Act", "section": "66D", "title": "Cheating by personation using computer resource"},
    ],
    "upi_fraud": [
        {"act": "BNS", "section": "318(4)", "title": "Cheating and dishonestly inducing delivery of property"},
        {"act": "IT Act", "section": "66D", "title": "Cheating by personation using computer resource"},
        {"act": "IT Act", "section": "43", "title": "Penalty for damage to computer, computer system"},
    ],
    "identity_theft": [
        {"act": "IT Act", "section": "66C", "title": "Identity theft"},
        {"act": "BNS", "section": "319(2)", "title": "Cheating by personation"},
    ],
    "malware": [
        {"act": "IT Act", "section": "43", "title": "Damage to computer, computer system"},
        {"act": "IT Act", "section": "66", "title": "Computer related offences"},
        {"act": "BNS", "section": "324", "title": "Mischief causing damage"},
    ],
    "ransomware": [
        {"act": "IT Act", "section": "66", "title": "Computer related offences"},
        {"act": "BNS", "section": "308", "title": "Extortion"},
        {"act": "IT Act", "section": "43(i)", "title": "Destroying / deleting information in a computer resource"},
    ],
    "social_media_fraud": [
        {"act": "IT Act", "section": "66D", "title": "Cheating by personation using computer resource"},
        {"act": "BNS", "section": "356", "title": "Defamation"},
    ],
    "sim_swap": [
        {"act": "IT Act", "section": "66C", "title": "Identity theft"},
        {"act": "BNS", "section": "318(4)", "title": "Cheating"},
    ],
    "financial_fraud": [
        {"act": "BNS", "section": "318(4)", "title": "Cheating and dishonestly inducing delivery of property"},
        {"act": "BNS", "section": "316(2)", "title": "Criminal breach of trust"},
        {"act": "IT Act", "section": "66D", "title": "Cheating by personation using computer resource"},
    ],
    "cyber_stalking": [
        {"act": "BNS", "section": "78", "title": "Stalking"},
        {"act": "IT Act", "section": "67", "title": "Publishing obscene material in electronic form"},
    ],
    "data_breach": [
        {"act": "IT Act", "section": "43A", "title": "Compensation for failure to protect data"},
        {"act": "IT Act", "section": "72", "title": "Breach of confidentiality and privacy"},
    ],
    "other": [
        {"act": "BNS", "section": "318", "title": "Cheating"},
        {"act": "IT Act", "section": "66", "title": "Computer related offences"},
    ],
}

EVIDENCE_CHECKLISTS: Dict[str, List[str]] = {
    "phishing": [
        "Original phishing email/SMS with full headers",
        "Screenshots of the fraudulent website",
        "WHOIS and hosting details of the domain",
        "Victim bank statement showing the debit",
        "Transaction IDs and beneficiary account details",
    ],
    "upi_fraud": [
        "UPI transaction IDs (UTR numbers)",
        "Bank statement of the victim account",
        "Beneficiary VPA / account KYC from the PSP",
        "Call detail record (CDR) of the fraudster number",
        "Screenshots of chat / call logs",
    ],
    "identity_theft": [
        "Copies of forged identity documents",
        "Account creation logs from the service provider",
        "IP logs of the impersonating account",
        "Victim's genuine identity proof",
    ],
    "malware": [
        "Forensic image of the infected system",
        "Malware sample and hash values",
        "Network traffic capture (PCAP)",
        "Antivirus / EDR logs",
    ],
    "ransomware": [
        "Ransom note file",
        "Encrypted file samples and extensions",
        "Crypto wallet address used for ransom",
        "Backup and system restore logs",
    ],
    "social_media_fraud": [
        "Profile URL and screenshots of the fake account",
        "Platform-provided subscriber and IP logs",
        "Chat transcripts with the accused",
        "Payment trail if money was transferred",
    ],
    "sim_swap": [
        "Telecom operator SIM change logs",
        "KYC documents submitted for the swap",
        "OTP delivery logs from the bank",
        "Victim's bank transaction statement",
    ],
    "financial_fraud": [
        "Complete bank statements of all involved accounts",
        "KYC of beneficiary accounts",
        "Money trail / layering chart",
        "Merchant settlement records",
    ],
    "cyber_stalking": [
        "Screenshots of messages / posts with timestamps",
        "Platform subscriber and IP logs",
        "Victim statement under BNSS",
        "Device forensic report if applicable",
    ],
    "data_breach": [
        "Server and application access logs",
        "Sample of the leaked dataset",
        "Security audit / VAPT report",
        "Data protection policy of the entity",
    ],
    "other": [
        "Written complaint of the victim",
        "Relevant digital evidence with hash values",
        "Section 63 BSA certificate for electronic records",
    ],
}


def recommend_sections(crime_type: str, description: str = "") -> List[Dict[str, Any]]:
    """Return legal sections for a crime type with confidence and reasoning."""
    sections = BNS_SECTIONS.get(crime_type, BNS_SECTIONS["other"])
    text = description.lower()
    results: List[Dict[str, Any]] = []
    for index, section in enumerate(sections):
        confidence = max(55, 95 - index * 10)
        if section["title"].split()[0].lower() in text:
            confidence = min(99, confidence + 5)
        results.append(
            {
                **section,
                "confidence": confidence,
                "reasoning": (
                    f"Commonly invoked for {crime_type.replace('_', ' ')} cases "
                    f"where {section['title'].lower()} is made out."
                ),
            }
        )
    return results


def evidence_checklist(crime_type: str) -> List[str]:
    return EVIDENCE_CHECKLISTS.get(crime_type, EVIDENCE_CHECKLISTS["other"])
