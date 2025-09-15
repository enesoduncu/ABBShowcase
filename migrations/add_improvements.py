"""
Migration: Verbesserungen für ABB und Einsatz-Verwaltung
- Neue Enums für Schulabschluss und Studium-Status
- Schularten-Enum für Einsätze
- Korrektur von 'stubo' zu 'studienbotschafter'
- 'eindruck' zu 'notizen' geändert
- Neue Felder hinzugefügt
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

def upgrade():
    """Upgrade-Funktion"""
    
    # ABB-Tabelle erweitern
    with op.batch_alter_table('abb', schema=None) as batch_op:
        # Neue Spalten hinzufügen
        batch_op.add_column(sa.Column('studium_status', sa.String(50), nullable=True))
        batch_op.add_column(sa.Column('studium_fach', sa.String(200), nullable=True))
        
        # 'eindruck' zu 'notizen' umbenennen
        batch_op.alter_column('eindruck', new_column_name='notizen')
        
        # 'schulabschluss' zu Enum ändern (zunächst als String)
        batch_op.alter_column('schulabschluss', type_=sa.String(50))
    
    # Einsatz-Tabelle erweitern
    with op.batch_alter_table('einsatz', schema=None) as batch_op:
        # 'stubo' zu 'studienbotschafter' umbenennen
        batch_op.alter_column('stubo', new_column_name='studienbotschafter')
        
        # 'schulart' zu Enum ändern (zunächst als String)
        batch_op.alter_column('schulart', type_=sa.String(50))

def downgrade():
    """Downgrade-Funktion"""
    
    # ABB-Tabelle zurücksetzen
    with op.batch_alter_table('abb', schema=None) as batch_op:
        # Neue Spalten entfernen
        batch_op.drop_column('studium_fach')
        batch_op.drop_column('studium_status')
        
        # 'notizen' zu 'eindruck' umbenennen
        batch_op.alter_column('notizen', new_column_name='eindruck')
    
    # Einsatz-Tabelle zurücksetzen
    with op.batch_alter_table('einsatz', schema=None) as batch_op:
        # 'studienbotschafter' zu 'stubo' umbenennen
        batch_op.alter_column('studienbotschafter', new_column_name='stubo')
