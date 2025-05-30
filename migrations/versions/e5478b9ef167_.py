"""empty message

Revision ID: e5478b9ef167
Revises: 
Create Date: 2025-04-19 19:57:41.001167

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e5478b9ef167'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('recording',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('patient_id', sa.Integer(), nullable=False),
    sa.Column('recording_type', sa.String(length=100), nullable=False),
    sa.Column('hospitalization_day', sa.Integer(), nullable=False),
    sa.Column('weight', sa.Float(), nullable=False),
    sa.Column('systolic', sa.Float(), nullable=False),
    sa.Column('diastolic', sa.Float(), nullable=False),
    sa.Column('voice_sample', sa.LargeBinary(), nullable=False),
    sa.Column('nocturnal_cough_sample', sa.LargeBinary(), nullable=False),
    sa.Column('breathing_difficulty', sa.Integer(), nullable=False),
    sa.Column('chest_pain', sa.Integer(), nullable=False),
    sa.Column('fatigue_level', sa.Integer(), nullable=False),
    sa.Column('sleep_quality', sa.Integer(), nullable=False),
    sa.Column('additional_notes', sa.String(length=10000), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('recording')
    # ### end Alembic commands ###
