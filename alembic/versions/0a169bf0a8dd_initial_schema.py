"""initial schema

Revision ID: 0a169bf0a8dd
Revises: 
Create Date: 2026-04-24 12:10:28.753615

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0a169bf0a8dd'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    
    #pgcrypto gives us gen_random_uuid(). Neon Ships it but it's not enabled by default.
    op.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto"')
    
    
    op.execute("""
        CREATE TABLE users (
            user_id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            email           VARCHAR(500) UNIQUE NOT NULL,
            api_key_hash    VARCHAR(300) NOT NULL,
            display_name    VARCHAR(100),
            created_at      TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
        )
        """)

    op.execute("CREATE INDEX idx_users_api_key ON users(api_key_hash)")

    op.execute("""
        CREATE TABLE data_sources (
            source_id       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id         UUID REFERENCES users(user_id) ON DELETE CASCADE,
            name            VARCHAR(600) NOT NULL,
            source_type     VARCHAR(20)  DEFAULT 'csv'
                CHECK (source_type = 'csv'),
            csv_file_path   VARCHAR(500) NOT NULL,
            csv_columns     JSONB,
            row_count       INTEGER,
            uploaded_at     TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
        )               
        """)
    
    op.execute("CREATE INDEX idx_sources_user ON data_sources(user_id)")

    op.execute("""
        CREATE TABLE semantic_definitions(
            definition_id       UUID PRIMARY    KEY DEFAULT gen_random_uuid(),
            metric_name         VARCHAR(200)    UNIQUE NOT NULL,
            display_name        VARCHAR(300)    NOT NULL,
            description         TEXT            NOT NULL,
            required_filters    JSONB DEFAULT '[]'::jsonb,
            time_dimension      VARCHAR(200),
            grain               VARCHAR(50),
            owner               VARCHAR(100),
            tags                JSONB           DEFAULT '[]'::jsonb,
            raw_yaml            TEXT,
            is_active           BOOLEAN         DEFAULT TRUE,
            created_at          TIMESTAMPTZ      DEFAULT CURRENT_TIMESTAMP
        )""")

    op.execute("""
        CREATE TABLE audit_log(
            log_id                  BIGSERIAL       PRIMARY KEY,
            user_id                 UUID    REFERENCES users(user_id),
            source_id               UUID    REFERENCES data_sources(source_id),
            question_text           TEXT    NOT NULL,
            generated_sql           TEXT,
            goverened_sql           TEXT,
            viz_spec                JSONB,
            governance_diff         TEXT,
            governance_result       VARCHAR(20)
                    CHECK (governance_result IN ('PASS', 'REWRITE', 'BLOCKED', 'ERROR')),
            governance_decisions    JSONB,
            matched_definitions     JSONB  DEFAULT '[]'::jsonb,
            execution_exit_code     INTEGER,
            execution_duration_ms   INTEGER,
            execution_timed_out     BOOLEAN DEFAULT FALSE,
            container_id            VARCHAR(64),
            latency_semantic_ms     INTEGER,
            latency_codegen_ms      INTEGER,
            latency_governance_ms   INTEGER,
            latency_execution_ms    INTEGER,
            tokens_latency_ms       INTEGER,
            tokens_input            INTEGER,
            tokens_output           INTEGER,
            created_at              TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
        )""")
    
    op.execute("CREATE INDEX idx_audit_user     ON audit_log(user_id)")
    
    op.execute("CREATE INDEX idx_audit_created  ON audit_log(created_at DESC)")
    
    op.execute("CREATE INDEX idx_audit_result   ON audit_log(governance_result)")
    
    
    
def downgrade() -> None:
    # Reverse order — children before parents because of FK constraints.
    op.execute("DROP TABLE IF EXISTS audit_log")
    op.execute("DROP TABLE IF EXISTS semantic_definitions")
    op.execute("DROP TABLE IF EXISTS data_sources")
    op.execute("DROP TABLE IF EXISTS users")