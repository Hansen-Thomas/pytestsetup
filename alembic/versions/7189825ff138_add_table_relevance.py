"""Add table relevance

Revision ID: 7189825ff138
Revises: d087462e039d
Create Date: 2025-01-01 22:37:21.940360

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "7189825ff138"
down_revision: Union[str, None] = "d087462e039d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "Relevance",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("description"),
    )
    op.add_column("Card", sa.Column("id_relevance", sa.Integer(), nullable=True))
    op.create_foreign_key(None, "Card", "Relevance", ["id_relevance"], ["id"])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, "Card", type_="foreignkey")
    op.drop_column("Card", "id_relevance")
    op.drop_table("Relevance")
    # ### end Alembic commands ###