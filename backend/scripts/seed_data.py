"""Seed the database with demo users and cases.

Usage:  python scripts/seed_data.py
"""

import os
import sys
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.security import hash_password  # noqa: E402
from app.db.session import SessionLocal, init_db  # noqa: E402
from app.models.case import Case, CasePriority, CaseStatus, CrimeType  # noqa: E402
from app.models.notification import Notification  # noqa: E402
from app.models.user import User, UserRole  # noqa: E402

DEMO_USERS = [
    {
        "username": "admin",
        "email": "admin@crimegpt.gov.in",
        "full_name": "System Administrator",
        "role": UserRole.ADMIN,
        "password": "admin123",
    },
    {
        "username": "officer1",
        "email": "officer1@crimegpt.gov.in",
        "full_name": "Inspector Rakesh Patel",
        "role": UserRole.OFFICER,
        "password": "officer123",
    },
    {
        "username": "analyst1",
        "email": "analyst1@crimegpt.gov.in",
        "full_name": "Analyst Meera Shah",
        "role": UserRole.ANALYST,
        "password": "analyst123",
    },
]

DEMO_CASES = [
    {
        "title": "UPI fraud - victim lost INR 85,000 to fake customer care",
        "description": (
            "On 12/03/2025 the complainant received a call from 9876543210 claiming to be "
            "bank customer care. The caller shared a UPI collect request from fraudster@ybl and "
            "the victim lost Rs. 85,000. Transaction UTR 402312345678 was credited to account "
            "912345678901234."
        ),
        "crime_type": CrimeType.UPI_FRAUD,
        "priority": CasePriority.HIGH,
        "status": CaseStatus.IN_PROGRESS,
        "complainant_name": "Kiran Desai",
        "complainant_contact": "9876500011",
        "location": "Ahmedabad",
        "loss_amount": 85000,
    },
    {
        "title": "Phishing website impersonating a nationalised bank",
        "description": (
            "Complainant clicked https://secure-bank-verify.example.com received via SMS on "
            "05/02/2025 and entered net banking credentials. IP 45.67.89.10 was recorded in the "
            "bank logs. Loss of Rs. 1,20,000 reported."
        ),
        "crime_type": CrimeType.PHISHING,
        "priority": CasePriority.CRITICAL,
        "status": CaseStatus.OPEN,
        "complainant_name": "Shri Anil Mehta",
        "complainant_contact": "9825011122",
        "location": "Surat",
        "loss_amount": 120000,
    },
    {
        "title": "Ransomware attack on a logistics company server",
        "description": (
            "On 2025-01-20 the company's file server was encrypted and a ransom note demanded "
            "payment in bitcoin. Backups were partially available. Contact email "
            "lockbit.support@example.org."
        ),
        "crime_type": CrimeType.RANSOMWARE,
        "priority": CasePriority.CRITICAL,
        "status": CaseStatus.PENDING,
        "complainant_name": "Gujarat Logistics Pvt Ltd",
        "complainant_contact": "9898912345",
        "location": "Vadodara",
        "loss_amount": 500000,
    },
    {
        "title": "Fake Instagram profile used for extortion",
        "description": (
            "A fake Instagram profile using the victim's morphed photographs demanded money on "
            "18/04/2025. Threatening messages were received from 7778889990."
        ),
        "crime_type": CrimeType.SOCIAL_MEDIA_FRAUD,
        "priority": CasePriority.MEDIUM,
        "status": CaseStatus.OPEN,
        "complainant_name": "Ms. Priya Joshi",
        "complainant_contact": "9033344455",
        "location": "Rajkot",
        "loss_amount": 25000,
    },
    {
        "title": "SIM swap leading to unauthorised bank transfers",
        "description": (
            "Duplicate SIM was issued on 02/05/2025 without the victim's consent. OTPs were "
            "diverted and Rs. 2,40,000 was transferred from account 556677889900."
        ),
        "crime_type": CrimeType.SIM_SWAP,
        "priority": CasePriority.HIGH,
        "status": CaseStatus.CLOSED,
        "complainant_name": "Hardik Trivedi",
        "complainant_contact": "9724455667",
        "location": "Gandhinagar",
        "loss_amount": 240000,
    },
]


def seed() -> None:
    init_db()
    db = SessionLocal()
    try:
        users = {}
        for data in DEMO_USERS:
            user = db.query(User).filter(User.username == data["username"]).first()
            if user is None:
                user = User(
                    username=data["username"],
                    email=data["email"],
                    full_name=data["full_name"],
                    role=data["role"].value,
                    hashed_password=hash_password(data["password"]),
                )
                db.add(user)
                db.commit()
                db.refresh(user)
            users[data["username"]] = user

        officer = users["officer1"]
        year = datetime.now(timezone.utc).year
        for index, data in enumerate(DEMO_CASES, start=1):
            case_number = f"CG-{year}-{index:05d}"
            if db.query(Case).filter(Case.case_number == case_number).first():
                continue
            case = Case(
                case_number=case_number,
                title=data["title"],
                description=data["description"],
                crime_type=data["crime_type"].value,
                priority=data["priority"].value,
                status=data["status"].value,
                complainant_name=data["complainant_name"],
                complainant_contact=data["complainant_contact"],
                location=data["location"],
                loss_amount=data["loss_amount"],
                officer_id=officer.id,
                created_at=datetime.now(timezone.utc) - timedelta(days=index * 7),
            )
            db.add(case)
            db.commit()
            db.refresh(case)
            db.add(
                Notification(
                    user_id=officer.id,
                    case_id=case.id,
                    title=f"Case {case.case_number} assigned",
                    message=case.title,
                    severity="info" if case.priority != "critical" else "warning",
                )
            )
            db.commit()

        print("Seeded users: " + ", ".join(users))
        print(f"Total cases: {db.query(Case).count()}")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
