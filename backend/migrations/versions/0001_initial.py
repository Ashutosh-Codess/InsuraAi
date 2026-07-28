"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-07-24

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto"')

    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("role", sa.String(20), nullable=False, server_default="customer"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "customers",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False, unique=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("age", sa.Integer()),
        sa.Column("gender", sa.String(20)),
        sa.Column("location", sa.String(255)),
        sa.Column("occupation", sa.String(255)),
        sa.Column("income", sa.Numeric(14, 2)),
        sa.Column("employment", sa.String(100)),
        sa.Column("marital_status", sa.String(30)),
        sa.Column("dependents", sa.Integer(), server_default="0"),
        sa.Column("risk_score", sa.Numeric(5, 2)),
        sa.Column("risk_category", sa.String(20)),
    )

    op.create_table(
        "policies",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("customer_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("customers.id"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("type", sa.String(50), nullable=False),
        sa.Column("provider", sa.String(255)),
        sa.Column("coverage_details", sa.Text()),
        sa.Column("coverage_amount", sa.Numeric(14, 2), nullable=False),
        sa.Column("premium_amount", sa.Numeric(14, 2), nullable=False),
        sa.Column("deductible", sa.Numeric(14, 2), server_default="0"),
        sa.Column("duration_months", sa.Integer(), nullable=False),
        sa.Column("eligibility", postgresql.JSONB(), server_default=sa.text("'{}'::jsonb")),
        sa.Column("exclusions", postgresql.JSONB(), server_default=sa.text("'{}'::jsonb")),
        sa.Column("terms_and_conditions", sa.Text()),
        sa.Column("renewal_conditions", sa.Text()),
        sa.Column("start_date", sa.Date(), server_default=sa.func.current_date()),
        sa.Column("status", sa.String(20), server_default="active"),
    )

    op.create_table(
        "claims",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("customer_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("customers.id"), nullable=False),
        sa.Column("policy_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("policies.id"), nullable=False),
        sa.Column("type", sa.String(50), nullable=False),
        sa.Column("claim_date", sa.Date(), server_default=sa.func.current_date()),
        sa.Column("incident_date", sa.Date()),
        sa.Column("incident_description", sa.Text()),
        sa.Column("claimed_amount", sa.Numeric(14, 2), nullable=False),
        sa.Column("approved_amount", sa.Numeric(14, 2)),
        sa.Column("status", sa.String(30), server_default="submitted"),
        sa.Column("final_decision", sa.Text()),
        sa.Column("processing_history", postgresql.JSONB(), server_default=sa.text("'[]'::jsonb")),
        sa.Column("fraud_score", sa.Numeric(5, 2)),
        sa.Column("fraud_label", sa.String(20)),
        sa.Column("investigation_notes", sa.Text()),
        sa.Column("submitted_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade():
    op.drop_table("claims")
    op.drop_table("policies")
    op.drop_table("customers")
    op.drop_table("users")
