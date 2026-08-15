-- CrimeGPT PostgreSQL schema
-- Mirrors the SQLAlchemy models in backend/app/models.

CREATE TABLE IF NOT EXISTS users (
    id              SERIAL PRIMARY KEY,
    username        VARCHAR(64) UNIQUE NOT NULL,
    email           VARCHAR(255) UNIQUE NOT NULL,
    full_name       VARCHAR(255) NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    role            VARCHAR(32) NOT NULL DEFAULT 'investigating_officer',
    department      VARCHAR(255) NOT NULL DEFAULT 'Cyber Crime Branch',
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS cases (
    id                  SERIAL PRIMARY KEY,
    case_number         VARCHAR(32) UNIQUE NOT NULL,
    title               VARCHAR(255) NOT NULL,
    description         TEXT NOT NULL DEFAULT '',
    crime_type          VARCHAR(64) NOT NULL DEFAULT 'other',
    status              VARCHAR(32) NOT NULL DEFAULT 'open',
    priority            VARCHAR(32) NOT NULL DEFAULT 'medium',
    complainant_name    VARCHAR(255) NOT NULL DEFAULT '',
    complainant_contact VARCHAR(64) NOT NULL DEFAULT '',
    location            VARCHAR(255) NOT NULL DEFAULT '',
    loss_amount         INTEGER NOT NULL DEFAULT 0,
    officer_id          INTEGER REFERENCES users (id),
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_cases_status ON cases (status);
CREATE INDEX IF NOT EXISTS idx_cases_crime_type ON cases (crime_type);

CREATE TABLE IF NOT EXISTS documents (
    id             SERIAL PRIMARY KEY,
    case_id        INTEGER NOT NULL REFERENCES cases (id) ON DELETE CASCADE,
    filename       VARCHAR(255) NOT NULL,
    content_type   VARCHAR(128) NOT NULL DEFAULT 'application/octet-stream',
    size_bytes     INTEGER NOT NULL DEFAULT 0,
    storage_path   VARCHAR(512) NOT NULL DEFAULT '',
    extracted_text TEXT NOT NULL DEFAULT '',
    uploaded_by    INTEGER REFERENCES users (id),
    created_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_documents_case_id ON documents (case_id);

CREATE TABLE IF NOT EXISTS document_analyses (
    id              SERIAL PRIMARY KEY,
    document_id     INTEGER NOT NULL REFERENCES documents (id) ON DELETE CASCADE,
    case_id         INTEGER NOT NULL REFERENCES cases (id) ON DELETE CASCADE,
    crime_type      VARCHAR(64) NOT NULL DEFAULT 'other',
    confidence      INTEGER NOT NULL DEFAULT 0,
    summary         TEXT NOT NULL DEFAULT '',
    entities        JSONB NOT NULL DEFAULT '{}'::JSONB,
    timeline        JSONB NOT NULL DEFAULT '[]'::JSONB,
    recommendations JSONB NOT NULL DEFAULT '[]'::JSONB,
    legal_sections  JSONB NOT NULL DEFAULT '[]'::JSONB,
    engine          VARCHAR(32) NOT NULL DEFAULT 'rule_based',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS chat_sessions (
    id         SERIAL PRIMARY KEY,
    user_id    INTEGER NOT NULL REFERENCES users (id),
    case_id    INTEGER REFERENCES cases (id) ON DELETE CASCADE,
    title      VARCHAR(255) NOT NULL DEFAULT 'New conversation',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS chat_messages (
    id         SERIAL PRIMARY KEY,
    session_id INTEGER NOT NULL REFERENCES chat_sessions (id) ON DELETE CASCADE,
    role       VARCHAR(16) NOT NULL DEFAULT 'user',
    content    TEXT NOT NULL DEFAULT '',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS notifications (
    id         SERIAL PRIMARY KEY,
    user_id    INTEGER NOT NULL REFERENCES users (id),
    case_id    INTEGER REFERENCES cases (id) ON DELETE CASCADE,
    title      VARCHAR(255) NOT NULL,
    message    TEXT NOT NULL DEFAULT '',
    severity   VARCHAR(16) NOT NULL DEFAULT 'info',
    is_read    BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS audit_logs (
    id            SERIAL PRIMARY KEY,
    user_id       INTEGER REFERENCES users (id),
    action        VARCHAR(64) NOT NULL,
    resource_type VARCHAR(64) NOT NULL DEFAULT '',
    resource_id   VARCHAR(64) NOT NULL DEFAULT '',
    details       TEXT NOT NULL DEFAULT '',
    ip_address    VARCHAR(64) NOT NULL DEFAULT '',
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON audit_logs (created_at DESC);
