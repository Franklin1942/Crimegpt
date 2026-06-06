# Crimegpt
CrimeGPT is a technology solution that helps law enforcement agencies manage cases using artificial intelligence and documentation.  
# CrimeGPT - AI-Powered Crime Documentation & Legal Intelligence Platform

CrimeGPT is an AI-powered platform designed for law enforcement agencies to automate crime documentation, cybercrime investigation assistance, legal intelligence, evidence analysis, and report generation.

## 🚀 Features

### Core Modules
- **Authentication & Authorization**: JWT-based authentication with Role-Based Access Control (RBAC)
- **Dashboard**: Real-time analytics, statistics cards, activity timeline, and case distribution charts
- **Case Management**: Full CRUD operations for cases with document uploads and evidence tracking
- **AI Analysis Engine**: Automated document analysis with entity extraction, timeline generation, and investigation recommendations
- **Legal Intelligence**: AI-powered legal section recommendations (BNS & IT Act)
- **Investigator Copilot**: ChatGPT-style interface for case assistance and investigation guidance
- **Evidence Intelligence**: Evidence checklist generation based on crime type
- **Charge Sheet Generator**: Automated charge sheet generation with PDF export
- **Document Processing**: Support for PDF, DOCX, TXT, and images with OCR capabilities
- **Search Module**: Global search across cases, documents, and entities
- **Notification System**: Real-time alerts and notifications
- **Audit Logging**: Complete audit trail for compliance

### User Roles
- **Administrator**: Full system access with user management capabilities
- **Investigating Officer**: Can create cases, upload evidence, run AI analysis, generate reports
- **Cyber Analyst**: Can review AI findings, analyze evidence, generate intelligence reports

## 🛠 Technology Stack

### Frontend
- **Framework**: Next.js 15 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **UI Components**: Custom components with Lucide Icons
- **Charts**: Recharts
- **State Management**: React Context + Hooks

### Backend
- **Framework**: FastAPI (Python 3.12)
- **Authentication**: JWT + Role-Based Access Control
- **Database**: PostgreSQL 15
- **ORM**: SQLAlchemy 2.0
- **AI/ML**: OpenAI GPT-4, LangChain
- **Document Processing**: PyPDF2, python-docx, pytesseract (OCR)
- **PDF Generation**: ReportLab

### DevOps
- **Containerization**: Docker, Docker Compose
- **Version Control**: Git

## 📋 Prerequisites

- Python 3.12+
- Node.js 20+
- PostgreSQL 15+
- Docker & Docker Compose (optional)
- OpenAI API Key (for AI features)

## 🚀 Quick Start

### Using Docker (Recommended)

1. **Clone the repository**
```bash
git clone <repository-url>
cd KANAD
```

2. **Configure environment variables**
```bash
# Copy backend environment file
cp backend/.env.example backend/.env

# Edit backend/.env and add your OpenAI API key
# OPENAI_API_KEY=your-openai-api-key-here
```

3. **Start all services**
```bash
docker-compose up -d
```

4. **Access the application**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/api/docs

5. **Seed sample data**
```bash
docker-compose exec backend python scripts/seed_data.py
```

### Manual Setup

#### Backend Setup

1. **Navigate to backend directory**
```bash
cd backend
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Initialize database**
```bash
# Create PostgreSQL database 'crimegpt'
psql -U postgres -c "CREATE DATABASE crimegpt;"

# Run schema
psql -U postgres -d crimegpt -f ../database/schema.sql
```

6. **Seed sample data**
```bash
python scripts/seed_data.py
```

7. **Start backend server**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Setup

1. **Navigate to frontend directory**
```bash
cd frontend
```

2. **Install dependencies**
```bash
npm install
```

3. **Configure environment**
```bash
cp .env.example .env.local
# Edit .env.local with your API URL
```

4. **Start development server**
```bash
npm run dev
```

5. **Access the application**
- Open http://localhost:3000 in your browser

## 🔐 Default Credentials

After seeding sample data, you can login with:

| Role | Username | Password |
|------|----------|----------|
| Administrator | admin | admin123 |
| Investigating Officer | officer1 | officer123 |
| Cyber Analyst | analyst1 | analyst123 |

## 📁 Project Structure

```
KANAD/
├── backend/
│   ├── app/
│   │   ├── api/           # API routes
│   │   ├── core/          # Configuration, security, dependencies
│   │   ├── models/        # SQLAlchemy models
│   │   ├── schemas/       # Pydantic schemas
│   │   ├── services/      # Business logic (AI, Legal, Chat, Report)
│   │   ├── db/            # Database configuration
│   │   └── main.py        # FastAPI application
│   ├── scripts/           # Utility scripts (seed data)
│   ├── requirements.txt    # Python dependencies
│   ├── Dockerfile         # Backend Docker configuration
│   └── .env.example       # Environment variables template
├── frontend/
│   ├── src/
│   │   ├── app/           # Next.js app directory
│   │   ├── components/    # React components
│   │   ├── lib/           # Utility functions
│   │   ├── hooks/         # Custom React hooks
│   │   ├── types/         # TypeScript types
│   │   └── contexts/      # React contexts
│   ├── package.json       # Node dependencies
│   ├── Dockerfile         # Frontend Docker configuration
│   └── .env.example       # Environment variables template
├── database/
│   └── schema.sql         # PostgreSQL database schema
├── docker-compose.yml     # Docker Compose configuration
├── ARCHITECTURE.md        # System architecture documentation
└── README.md              # This file
```

## 🔧 API Documentation

Once the backend is running, access the interactive API documentation at:
- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

### Main API Endpoints

- **Authentication**: `/api/auth/*`
- **Users**: `/api/users/*`
- **Cases**: `/api/cases/*`
- **Documents**: `/api/documents/*`
- **AI Analysis**: `/api/ai/*`
- **Legal Intelligence**: `/api/legal/*`
- **Investigator Copilot**: `/api/chat/*`
- **Reports**: `/api/reports/*`
- **Analytics**: `/api/analytics/*`
- **Notifications**: `/api/notifications/*`
- **Audit Logs**: `/api/audit/*`

## 🤖 AI Features

### Crime Classification
The AI engine automatically classifies crimes into categories:
- Phishing
- UPI Fraud
- Identity Theft
- Malware
- Ransomware
- Social Media Fraud
- SIM Swap
- Financial Fraud
- Cyber Stalking
- Data Breach

### Entity Extraction
Automatically extracts key entities from documents:
- Names
- Mobile Numbers
- Emails
- IP Addresses
- Bank Accounts
- URLs
- Locations

### Timeline Generation
Generates chronological event sequences from case descriptions.

### Legal Recommendations
AI-powered recommendations for:
- BNS (Bharatiya Nyaya Sanhita) sections
- IT Act sections
- With confidence scores and reasoning

## 📊 Analytics Dashboard

The dashboard provides:
- Total cases, open cases, closed cases, pending cases
- High priority and critical cases
- Crime type distribution
- Severity analysis
- Monthly trends
- Officer performance metrics

## 🔐 Security Features

- JWT-based authentication
- Password hashing with bcrypt
- Role-Based Access Control (RBAC)
- SQL injection prevention (ORM)
- XSS protection
- CSRF protection
- File upload validation
- Audit logging
- Secure environment variables

## 🌐 Multilingual Support

The platform supports:
- English
- Hindi
- Gujarati

## 📝 Documentation

- [Architecture Documentation](./ARCHITECTURE.md)
- [API Documentation](http://localhost:8000/api/docs) (when running)
- [Setup Guide](#quick-start)
- [Deployment Guide](#deployment)

## 🚢 Deployment

### Production Deployment

1. **Update environment variables** with production values
2. **Use strong secrets** for JWT and database
3. **Configure HTTPS** for production
4. **Set up proper backups** for database
5. **Configure monitoring** and logging
6. **Use production-grade database** (managed PostgreSQL)
7. **Scale horizontally** using load balancers

### Docker Production

```bash
# Build production images
docker-compose -f docker-compose.yml build

# Run with production configuration
docker-compose -f docker-compose.yml up -d
```

## 🤝 Contributing

This is a hackathon project. For contributions:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is created for the Gujarat Police Cyber Crime Branch hackathon.

## 👥 Team

CrimeGPT Development Team

## 🙏 Acknowledgments

- OpenAI for GPT-4 API
- LangChain for AI framework
- FastAPI for the backend framework
- Next.js for the frontend framework
- Gujarat Police Cyber Crime Branch

## 📞 Support

For support and queries, contact the development team.

---

**Built with ❤️ for Gujarat Police Cyber Crime Branch**
