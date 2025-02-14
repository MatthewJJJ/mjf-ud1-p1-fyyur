"""empty message

Revision ID: 6bcc0ce312ba
Revises: f4767c943707
Create Date: 2022-07-06 16:52:45.963256

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6bcc0ce312ba'
down_revision = 'f4767c943707'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('artists', sa.Column('description', sa.String(), nullable=True))
    op.add_column('artists', sa.Column('looking_for_venue', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('artists', 'looking_for_venue')
    op.drop_column('artists', 'description')
    # ### end Alembic commands ###
