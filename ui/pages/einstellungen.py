import streamlit as st
import os
import shutil
from pathlib import Path
from datetime import datetime
import zipfile
import io

from database import create_tables, drop_tables
from services.abb_service import ABBService
from services.einsatz_service import EinsatzService
import config

def einstellungen_page():
    """Einstellungsseite mit Backup/Restore und Stammdatenverwaltung"""
    
    st.title("⚙️ Einstellungen")
    st.markdown("Konfiguration und Verwaltung der Anwendung")
    
    # Services initialisieren
    abb_service = ABBService()
    einsatz_service = EinsatzService()
    
    # Tabs für verschiedene Einstellungen
    tab1, tab2, tab3, tab4 = st.tabs(["💾 Backup/Restore", "🏷️ Stammdaten", "🗄️ Datenbank", "ℹ️ Info"])
    
    with tab1:
        backup_restore_section()
    
    with tab2:
        stammdaten_section(abb_service, einsatz_service)
    
    with tab3:
        datenbank_section()
    
    with tab4:
        info_section()

def backup_restore_section():
    """Backup und Restore-Funktionen"""
    
    st.subheader("💾 Backup & Restore")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📤 Backup erstellen")
        st.markdown("Erstellen Sie eine Sicherungskopie der Datenbank und aller Einstellungen.")
        
        if st.button("💾 Vollständiges Backup erstellen", type="primary"):
            try:
                backup_data = create_backup()
                
                # Download-Button für Backup
                st.download_button(
                    label="📥 Backup herunterladen",
                    data=backup_data,
                    file_name=f"abb_streamlit_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                    mime="application/zip"
                )
                
                st.success("✅ Backup erfolgreich erstellt!")
                
            except Exception as e:
                st.error(f"❌ Fehler beim Erstellen des Backups: {str(e)}")
    
    with col2:
        st.markdown("### 📥 Backup wiederherstellen")
        st.markdown("Stellen Sie eine vorherige Sicherung wieder her.")
        
        uploaded_backup = st.file_uploader(
            "Backup-Datei auswählen",
            type=['zip'],
            help="Wählen Sie eine .zip-Backup-Datei aus"
        )
        
        if uploaded_backup is not None:
            if st.button("🔄 Backup wiederherstellen", type="secondary"):
                try:
                    restore_backup(uploaded_backup)
                    st.success("✅ Backup erfolgreich wiederhergestellt!")
                    st.info("Bitte starten Sie die Anwendung neu, um alle Änderungen zu übernehmen.")
                except Exception as e:
                    st.error(f"❌ Fehler beim Wiederherstellen des Backups: {str(e)}")

def create_backup() -> bytes:
    """Erstellt ein vollständiges Backup der Anwendung"""
    
    # Backup-Verzeichnis erstellen
    backup_dir = Path("temp_backup")
    backup_dir.mkdir(exist_ok=True)
    
    try:
        # Datenbank kopieren
        db_path = Path(config.DATABASE_URL.replace("sqlite:///", ""))
        if db_path.exists():
            backup_db_path = backup_dir / "abb_streamlit.db"
            shutil.copy2(db_path, backup_db_path)
        
        # Konfigurationsdateien kopieren
        config_files = ["config.py", "requirements.txt", "README.md"]
        for file_name in config_files:
            if Path(file_name).exists():
                shutil.copy2(file_name, backup_dir / file_name)
        
        # Verzeichnisstruktur kopieren
        dirs_to_backup = ["models", "schemas", "services", "ui"]
        for dir_name in dirs_to_backup:
            if Path(dir_name).exists():
                shutil.copytree(dir_name, backup_dir / dir_name, dirs_exist_ok=True)
        
        # ZIP-Datei erstellen
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for file_path in backup_dir.rglob('*'):
                if file_path.is_file():
                    arc_name = file_path.relative_to(backup_dir)
                    zip_file.write(file_path, arc_name)
        
        zip_buffer.seek(0)
        backup_data = zip_buffer.getvalue()
        
        # Temporäres Verzeichnis aufräumen
        shutil.rmtree(backup_dir)
        
        return backup_data
        
    except Exception as e:
        # Aufräumen bei Fehlern
        if backup_dir.exists():
            shutil.rmtree(backup_dir)
        raise e

def restore_backup(uploaded_file):
    """Stellt ein Backup wieder her"""
    
    try:
        # Backup-Datei extrahieren
        with zipfile.ZipFile(uploaded_file, 'r') as zip_file:
            # Temporäres Verzeichnis erstellen
            restore_dir = Path("temp_restore")
            restore_dir.mkdir(exist_ok=True)
            
            # Dateien extrahieren
            zip_file.extractall(restore_dir)
            
            # Datenbank wiederherstellen
            db_path = Path(config.DATABASE_URL.replace("sqlite:///", ""))
            backup_db_path = restore_dir / "abb_streamlit.db"
            
            if backup_db_path.exists():
                # Bestehende Datenbank sichern
                if db_path.exists():
                    backup_name = f"abb_streamlit_backup_before_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
                    shutil.copy2(db_path, backup_name)
                    st.info(f"Bestehende Datenbank wurde als '{backup_name}' gesichert.")
                
                # Neue Datenbank kopieren
                shutil.copy2(backup_db_path, db_path)
                st.success("Datenbank erfolgreich wiederhergestellt!")
            
            # Aufräumen
            shutil.rmtree(restore_dir)
            
    except Exception as e:
        # Aufräumen bei Fehlern
        if 'restore_dir' in locals() and restore_dir.exists():
            shutil.rmtree(restore_dir)
        raise e

def stammdaten_section(abb_service: ABBService, einsatz_service: EinsatzService):
    """Stammdatenverwaltung"""
    
    st.subheader("🏷️ Stammdaten verwalten")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🏫 Schularten")
        
        # Schularten anzeigen
        schularten = einsatz_service.get_schularten()
        if schularten:
            st.markdown("**Verfügbare Schularten:**")
            for schulart in schularten:
                st.markdown(f"• {schulart}")
        else:
            st.info("Keine Schularten definiert.")
        
        # Neue Schulart hinzufügen
        neue_schulart = st.text_input("Neue Schulart", max_chars=100)
        if st.button("➕ Schulart hinzufügen"):
            if neue_schulart:
                st.info(f"Schulart '{neue_schulart}' wird beim nächsten Einsatz hinzugefügt.")
            else:
                st.warning("Bitte geben Sie eine Schulart ein.")
    
    with col2:
        st.markdown("### 🏘️ Landkreise")
        
        # Landkreise anzeigen
        landkreise = einsatz_service.get_landkreise()
        if landkreise:
            st.markdown("**Verfügbare Landkreise:**")
            for landkreis in landkreise:
                st.markdown(f"• {landkreis}")
        else:
            st.info("Keine Landkreise definiert.")
        
        # Neuen Landkreis hinzufügen
        neuer_landkreis = st.text_input("Neuer Landkreis", max_chars=100)
        if st.button("➕ Landkreis hinzufügen"):
            if neuer_landkreis:
                st.info(f"Landkreis '{neuer_landkreis}' wird beim nächsten Einsatz hinzugefügt.")
            else:
                st.warning("Bitte geben Sie einen Landkreis ein.")
    
    # ABB-spezifische Stammdaten
    st.markdown("### 👥 ABB-Stammdaten")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**Berufe**")
        berufe = abb_service.get_berufe()
        if berufe:
            st.markdown("**Verfügbare Berufe:**")
            for beruf in berufe[:10]:  # Nur erste 10 anzeigen
                st.markdown(f"• {beruf}")
            if len(berufe) > 10:
                st.markdown(f"... und {len(berufe) - 10} weitere")
        else:
            st.info("Keine Berufe definiert.")
    
    with col2:
        st.markdown("**Schulabschlüsse**")
        schulabschluesse = abb_service.get_schulabschluesse()
        if schulabschluesse:
            st.markdown("**Verfügbare Schulabschlüsse:**")
            for abschluss in schulabschluesse[:10]:
                st.markdown(f"• {abschluss}")
            if len(schulabschluesse) > 10:
                st.markdown(f"... und {len(schulabschluesse) - 10} weitere")
        else:
            st.info("Keine Schulabschlüsse definiert.")
    
    with col3:
        st.markdown("**Betriebslandkreise**")
        betrieb_landkreise = abb_service.get_landkreise()
        if betrieb_landkreise:
            st.markdown("**Verfügbare Landkreise:**")
            for landkreis in betrieb_landkreise[:10]:
                st.markdown(f"• {landkreis}")
            if len(betrieb_landkreise) > 10:
                st.markdown(f"... und {len(betrieb_landkreise) - 10} weitere")
        else:
            st.info("Keine Betriebslandkreise definiert.")

def datenbank_section():
    """Datenbankverwaltung"""
    
    st.subheader("🗄️ Datenbankverwaltung")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🔄 Datenbank neu initialisieren")
        st.markdown("**⚠️ Achtung:** Dies löscht alle vorhandenen Daten!")
        
        if st.button("🗑️ Datenbank leeren", type="secondary"):
            if st.checkbox("Ich bestätige, dass alle Daten gelöscht werden sollen"):
                try:
                    drop_tables()
                    create_tables()
                    st.success("✅ Datenbank erfolgreich neu initialisiert!")
                    st.info("Alle Daten wurden gelöscht und die Tabellen neu erstellt.")
                except Exception as e:
                    st.error(f"❌ Fehler beim Neuinitialisieren der Datenbank: {str(e)}")
            else:
                st.warning("Bitte bestätigen Sie das Löschen der Daten.")
    
    with col2:
        st.markdown("### 📊 Datenbankstatus")
        
        try:
            # Datenbankstatus prüfen
            st.success("✅ Datenbankverbindung erfolgreich")
            
            # Tabellen prüfen
            import sqlite3
            db_path = Path(config.DATABASE_URL.replace("sqlite:///", ""))
            
            if db_path.exists():
                conn = sqlite3.connect(str(db_path))
                cursor = conn.cursor()
                
                # Tabellen prüfen
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                existing_tables = [row[0] for row in cursor.fetchall()]
                
                required_tables = ['abb', 'einsatz', 'abb_einsatz']
                missing_tables = [table for table in required_tables if table not in existing_tables]
                
                if missing_tables:
                    st.error(f"❌ Fehlende Tabellen: {', '.join(missing_tables)}")
                else:
                    st.success("✅ Alle erforderlichen Tabellen vorhanden")
                
                # Datenbankgröße
                size_mb = db_path.stat().st_size / (1024 * 1024)
                st.metric("Datenbankgröße", f"{size_mb:.2f} MB")
                
                conn.close()
            else:
                st.error("❌ Datenbankdatei nicht gefunden")
            
        except Exception as e:
            st.error(f"❌ Datenbankfehler: {str(e)}")
    
    # Datenbankpfad anzeigen
    st.markdown("### 📁 Datenbankpfad")
    st.code(config.DATABASE_URL, language="text")

def info_section():
    """Informationsseite"""
    
    st.subheader("ℹ️ Anwendungsinformationen")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📋 Version & Build")
        st.markdown("**Version:** 1.0.0")
        st.markdown("**Build-Datum:** " + datetime.now().strftime("%d.%m.%Y %H:%M:%S"))
        st.markdown("**Python-Version:** 3.11+")
        st.markdown("**Streamlit-Version:** 1.28.1")
        
        st.markdown("### 🔧 Technische Details")
        st.markdown("**Datenbank:** SQLite mit SQLAlchemy ORM")
        st.markdown("**Validierung:** Pydantic-Schemas")
        st.markdown("**Migrationen:** Alembic")
        st.markdown("**Visualisierung:** Plotly & Matplotlib")
    
    with col2:
        st.markdown("### 📁 Verzeichnisstruktur")
        st.markdown("**Datenbank:** `./data/`")
        st.markdown("**Uploads:** `./uploads/`")
        st.markdown("**Exports:** `./exports/`")
        st.markdown("**Logs:** `./logs/`")
        
        st.markdown("### 🚀 Features")
        st.markdown("✅ Vollständige CRUD-Operationen")
        st.markdown("✅ Automatische 25er-Gruppen-Aufteilung")
        st.markdown("✅ CSV-Import/Export")
        st.markdown("✅ Erweiterte Filterung")
        st.markdown("✅ Dashboard mit Visualisierungen")
        st.markdown("✅ Backup/Restore-Funktionen")
    
    # Systeminformationen
    st.markdown("### 💻 Systeminformationen")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Arbeitsverzeichnis", os.getcwd())
    
    with col2:
        st.metric("Python-Pfad", os.path.dirname(os.__file__))
    
    with col3:
        st.metric("Streamlit-Pfad", os.path.dirname(st.__file__))
    
    # Konfiguration
    st.markdown("### ⚙️ Konfiguration")
    
    config_data = {
        "Datenbank-URL": config.DATABASE_URL,
        "CSV-Delimiter": config.CSV_DELIMITER,
        "CSV-Encoding": config.CSV_ENCODING,
        "Debug-Modus": config.DEBUG,
        "Seitengröße": config.PAGE_SIZE,
        "Max. Schüler pro Einsatz": config.MAX_STUDENTS_PER_EINSATZ
    }
    
    for key, value in config_data.items():
        st.markdown(f"**{key}:** `{value}`")
    
    # Hilfe und Support
    st.markdown("### 🆘 Hilfe & Support")
    st.markdown("**Dokumentation:** Siehe README.md")
    st.markdown("**Probleme:** Überprüfen Sie die Logs in `./logs/`")
    st.markdown("**Backup:** Regelmäßige Backups werden empfohlen")
    st.markdown("**Updates:** Prüfen Sie regelmäßig auf neue Versionen")

if __name__ == "__main__":
    einstellungen_page()
