import sqlite3
import config
from contextlib import contextmanager
from typing import Generator, Any, Dict, List, Optional
import os

# Datenbankverbindung
def get_connection():
    """Erstellt eine neue Datenbankverbindung"""
    return sqlite3.connect(config.DATABASE_URL.replace('sqlite:///', ''), check_same_thread=False)

@contextmanager
def get_db_session():
    """Context Manager für Datenbank-Sessions"""
    conn = get_connection()
    conn.row_factory = sqlite3.Row  # Ermöglicht Zugriff auf Spalten über Namen
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def get_db():
    """Gibt eine neue Datenbankverbindung zurück"""
    return get_connection()

def create_tables():
    """Erstellt alle Tabellen in der Datenbank"""
    with get_db_session() as conn:
        cursor = conn.cursor()
        
        # ABB-Tabelle
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS abb (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                laufnummer INTEGER UNIQUE,
                aktiv BOOLEAN DEFAULT 1,
                vorname TEXT NOT NULL,
                nachname TEXT NOT NULL,
                geschlecht TEXT CHECK(geschlecht IN ('m', 'w', 'd')),
                geburtsdatum DATE,
                schulabschluss TEXT,
                vorbildung TEXT,
                studienabbrecher BOOLEAN DEFAULT 0,
                beruf TEXT,
                zq TEXT,
                bereich TEXT CHECK(bereich IN ('IHK', 'HWK', 'sonstiges')),
                ausbildungsbeginn DATE,
                ausbildungsende DATE,
                schulungsdatum DATE,
                mobilnummer TEXT,
                email_beruf TEXT,
                email_privat TEXT,
                telefon_beruf TEXT,
                telefon_privat TEXT,
                direktkontakt BOOLEAN DEFAULT 0,
                betrieb TEXT,
                betriebadresse TEXT,
                landkreis_betrieb TEXT,
                asp_name TEXT,
                asp_telefon TEXT,
                asp_email TEXT,
                eindruck TEXT,
                hinweise TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Einsatz-Tabelle
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS einsatz (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                beschreibung TEXT,
                start_datum DATE,
                end_datum DATE,
                status TEXT DEFAULT 'geplant',
                prioritaet TEXT DEFAULT 'normal',
                schueleranzahl INTEGER DEFAULT 0,
                landkreis TEXT,
                stadt TEXT,
                schulart TEXT,
                online BOOLEAN DEFAULT 0,
                stubo BOOLEAN DEFAULT 0,
                klassenstufe TEXT,
                erstellt_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                aktualisiert_am TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # ABB-Einsatz-Zuordnungstabelle
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS abb_einsatz (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                abb_id INTEGER NOT NULL,
                einsatz_id INTEGER NOT NULL,
                zuordnungs_datum DATE DEFAULT CURRENT_DATE,
                notizen TEXT,
                FOREIGN KEY (abb_id) REFERENCES abb (id) ON DELETE CASCADE,
                FOREIGN KEY (einsatz_id) REFERENCES einsatz (id) ON DELETE CASCADE,
                UNIQUE(abb_id, einsatz_id)
            )
        ''')
        
        # Indizes für bessere Performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_abb_vorname ON abb(vorname)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_abb_nachname ON abb(nachname)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_abb_bereich ON abb(bereich)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_abb_aktiv ON abb(aktiv)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_einsatz_name ON einsatz(name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_abb_einsatz_abb ON abb_einsatz(abb_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_abb_einsatz_einsatz ON abb_einsatz(einsatz_id)')

def drop_tables():
    """Löscht alle Tabellen aus der Datenbank"""
    with get_db_session() as conn:
        cursor = conn.cursor()
        cursor.execute('DROP TABLE IF EXISTS abb_einsatz')
        cursor.execute('DROP TABLE IF EXISTS einsatz')
        cursor.execute('DROP TABLE IF EXISTS abb')

def execute_query(query: str, params: tuple = ()) -> List[Dict[str, Any]]:
    """Führt eine SQL-Abfrage aus und gibt das Ergebnis als Liste von Dictionaries zurück"""
    with get_db_session() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        columns = [description[0] for description in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

def execute_single_query(query: str, params: tuple = ()) -> Optional[Dict[str, Any]]:
    """Führt eine SQL-Abfrage aus und gibt das erste Ergebnis als Dictionary zurück"""
    with get_db_session() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        columns = [description[0] for description in cursor.description]
        row = cursor.fetchone()
        return dict(zip(columns, row)) if row else None

def execute_insert(query: str, params: tuple = ()) -> int:
    """Führt einen INSERT aus und gibt die ID des eingefügten Datensatzes zurück"""
    with get_db_session() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        return cursor.lastrowid

def execute_update(query: str, params: tuple = ()) -> int:
    """Führt einen UPDATE aus und gibt die Anzahl der betroffenen Zeilen zurück"""
    with get_db_session() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        return cursor.rowcount

def execute_delete(query: str, params: tuple = ()) -> int:
    """Führt einen DELETE aus und gibt die Anzahl der gelöschten Zeilen zurück"""
    with get_db_session() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        return cursor.rowcount
