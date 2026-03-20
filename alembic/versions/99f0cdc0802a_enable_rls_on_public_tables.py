"""enable rls on public tables

Revision ID: 99f0cdc0802a
Revises: 23bcaaab40d3
Create Date: 2026-03-18 22:49:12.488482

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "99f0cdc0802a"
down_revision: Union[str, Sequence[str], None] = "23bcaaab40d3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


EXCLUDED_TABLES = {
    "alembic_version",
    "forecast_ai_reports",
    "forecast_assets",
    "forecast_backtests",
    "forecast_diagnostics",
    "forecast_requests",
    "forecast_point_evaluations",
    "forecast_points",
    "forecast_point_outcomes",
    "histories",
    "users",
    "plans",
    "subscriptions",
}


def _get_public_tables(connection):
    query = sa.text(
        """
        select tablename
        from pg_tables
        where schemaname = 'public'
        order by tablename
    """
    )
    result = connection.execute(query)
    return [row[0] for row in result if row[0] not in EXCLUDED_TABLES]


def upgrade():
    connection = op.get_bind()
    tables = _get_public_tables(connection)

    for table_name in tables:
        op.execute(
            sa.text(f'ALTER TABLE public."{table_name}" ENABLE ROW LEVEL SECURITY;')
        )


def downgrade():
    connection = op.get_bind()
    tables = _get_public_tables(connection)

    for table_name in tables:
        op.execute(
            sa.text(f'ALTER TABLE public."{table_name}" DISABLE ROW LEVEL SECURITY;')
        )
