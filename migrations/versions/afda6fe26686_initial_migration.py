"""Initial migration

Revision ID: afda6fe26686
Revises: 
Create Date: 2024-06-20 19:17:12.523831

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'afda6fe26686'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('equipment',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('model', sa.String(length=50), nullable=False),
    sa.Column('brand', sa.String(length=50), nullable=False),
    sa.Column('active', sa.Boolean(), nullable=True),
    sa.Column('condition', sa.String(length=20), nullable=False),
    sa.Column('building', sa.String(length=20), nullable=False),
    sa.Column('room', sa.String(length=20), nullable=False),
    sa.Column('esp_address', sa.String(length=128), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('ir_command',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('model', sa.String(length=50), nullable=False),
    sa.Column('raw_on', sa.String(length=2000), nullable=False),
    sa.Column('raw_off', sa.String(length=2000), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('model')
    )
    op.create_table('user',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('username', sa.String(length=50), nullable=False),
    sa.Column('password_hash', sa.String(length=256), nullable=False),
    sa.Column('role', sa.String(length=20), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('username')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user')
    op.drop_table('ir_command')
    op.drop_table('equipment')
    # ### end Alembic commands ###
