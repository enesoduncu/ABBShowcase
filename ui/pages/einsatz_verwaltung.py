import streamlit as st
import pandas as pd
from datetime import date, datetime
from typing import Optional

from database import get_db
from services.einsatz_service import EinsatzService
from services.csv_service import CSVService
from schemas.einsatz import EinsatzCreate, EinsatzUpdate, EinsatzFilter
from schemas.common import PaginationParams

def einsatz_verwaltung_page():
    """Einsatz-Verwaltungsseite"""
    
    st.title("📅 Einsätze verwalten")
    st.markdown("Verwalten Sie Schuleinsätze und Termine")
    
    # Session State initialisieren
    if 'einsatz_page' not in st.session_state:
        st.session_state.einsatz_page = 1
    if 'einsatz_filters' not in st.session_state:
        st.session_state.einsatz_filters = {}
    
    # Einsatz-Service initialisieren
    einsatz_service = EinsatzService()
    
    # Sidebar für Filter
    with st.sidebar:
        st.header("🔍 Filter")
        
        # Datumsbereich
        st.markdown("**Datumsspanne**")
        datum_von = st.date_input("Von", value=date.today())
        datum_bis = st.date_input("Bis", value=date.today())
        
        # Status
        status_options = einsatz_service.get_status()
        status_filter = st.selectbox(
            "Status",
            ["Alle"] + status_options,
            index=0
        )
        
        # Priorität
        prioritaeten = einsatz_service.get_prioritaeten()
        prioritaet_filter = st.selectbox(
            "Priorität",
            ["Alle"] + prioritaeten,
            index=0
        )
        
        # Suche
        suche = st.text_input("Suche (Name, Beschreibung)")
        
        # Filter anwenden
        if st.button("Filter anwenden"):
            st.session_state.einsatz_filters = {
                'start_datum_von': datum_von,
                'start_datum_bis': datum_bis,
                'status': None if status_filter == "Alle" else status_filter,
                'prioritaet': None if prioritaet_filter == "Alle" else prioritaet_filter,
                'name': None if not suche else suche
            }
            st.session_state.einsatz_page = 1
            st.rerun()
        
        # Filter zurücksetzen
        if st.button("Filter zurücksetzen"):
            st.session_state.einsatz_filters = {}
            st.session_state.einsatz_page = 1
            st.rerun()
    
    # Hauptbereich
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.subheader("📋 Einsatz-Liste")
    
    with col2:
        if st.button("➕ Neuen Einsatz anlegen", type="primary"):
            st.session_state.show_einsatz_form = True
    
    # Einsatz-Formular
    if st.session_state.get('show_einsatz_form', False):
        with st.expander("Neuen Einsatz anlegen", expanded=True):
            if einsatz_form(einsatz_service):
                st.session_state.show_einsatz_form = False
                st.rerun()
    
    # Einsatz-Liste anzeigen
    show_einsatz_list(einsatz_service)
    
    # CSV-Import/Export
    st.subheader("📁 Import/Export")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**CSV-Import**")
        uploaded_file = st.file_uploader(
            "CSV-Datei hochladen",
            type=['csv'],
            help="Wählen Sie eine CSV-Datei mit Einsatz-Daten aus"
        )
        
        if uploaded_file is not None:
            if st.button("Import starten"):
                import_einsatz_csv(uploaded_file, einsatz_service)
    
    with col2:
        st.markdown("**CSV-Export**")
        if st.button("Alle Einsätze exportieren"):
            export_einsatz_csv(einsatz_service)

def einsatz_form(einsatz_service: EinsatzService) -> bool:
    """Einsatz-Formular für das Anlegen/Bearbeiten"""
    
    st.markdown("### Einsatz-Daten eingeben")
    
    with st.form("einsatz_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            einsatzdatum = st.date_input("Einsatzdatum *", min_value=date.today())
            schulname = st.text_input("Schulname *", max_chars=200)
            schulart = st.text_input("Schulart *", max_chars=100)
            partner = st.text_input("Partner", max_chars=200)
            stadt = st.text_input("Stadt *", max_chars=100)
            landkreis = st.text_input("Landkreis *", max_chars=100)
        
        with col2:
            stubo = st.checkbox("Studien- und Berufsorientierung (STUBO)")
            online = st.checkbox("Online-Veranstaltung")
            klassenstufe = st.text_input("Klassenstufe *", max_chars=50)
            schueleranzahl = st.number_input(
                "Schüleranzahl *", 
                min_value=1, 
                max_value=100, 
                value=25,
                help="Maximal 25 Schüler pro Einsatz. Bei mehr Schülern wird automatisch aufgeteilt."
            )
        
        # Automatische Aufteilung
        if schueleranzahl > 25:
            st.warning(f"⚠️ **Wichtiger Hinweis:** {schueleranzahl} Schüler übersteigen das Maximum von 25 pro Einsatz.")
            
            anzahl_einsaetze = (schueleranzahl + 24) // 25  # Aufrunden
            st.info(f"📊 **Automatische Aufteilung:** Der Einsatz wird in {anzahl_einsaetze} separate Einsätze aufgeteilt:")
            
            # Aufteilung anzeigen
            rest = schueleranzahl
            for i in range(anzahl_einsaetze):
                schueler_im_einsatz = min(25, rest)
                st.markdown(f"• **Einsatz {i+1}:** {schueler_im_einsatz} Schüler")
                rest -= schueler_im_einsatz
        
        # Buttons
        col1, col2, col3 = st.columns(3)
        
        with col1:
            submitted = st.form_submit_button("💾 Speichern", type="primary")
        with col2:
            if st.form_submit_button("❌ Abbrechen"):
                return True
        with col3:
            if st.form_submit_button("🔄 Zurücksetzen"):
                st.rerun()
        
        if submitted:
            if validate_einsatz_form(schulname, schulart, stadt, landkreis, klassenstufe):
                try:
                    # Einsatz-Daten erstellen
                    einsatz_data = EinsatzCreate(
                        name=schulname,
                        beschreibung=f"Schulart: {schulart}, Stadt: {stadt}, Landkreis: {landkreis}, Partner: {partner}, STUBO: {stubo}, Online: {online}, Klassenstufe: {klassenstufe}, Schüleranzahl: {schueleranzahl}",
                        start_datum=einsatzdatum,
                        status="geplant",
                        prioritaet="normal"
                    )
                    
                    # Bei mehr als 25 Schülern automatisch aufteilen
                    if schueleranzahl > 25:
                        einsaetze = einsatz_service.split_einsatz_by_25(einsatz_data, schueleranzahl)
                        created_einsaetze = einsatz_service.create_multiple(einsaetze)
                        
                        st.success(f"✅ Einsatz erfolgreich in {len(created_einsaetze)} separate Einsätze aufgeteilt!")
                        st.info(f"📊 **Details:** {schueleranzahl} Schüler wurden auf {len(created_einsaetze)} Einsätze verteilt.")
                        
                        # Details der erstellten Einsätze anzeigen
                        for i, einsatz in enumerate(created_einsaetze):
                            st.markdown(f"• **Einsatz {i+1}:** {einsatz.get('name', '')} - {einsatz.get('start_datum', '')} - {schueleranzahl} Schüler")
                    else:
                        # Normaler Fall: Einzelner Einsatz
                        einsatz_service.create(einsatz_data)
                        st.success("✅ Einsatz erfolgreich angelegt!")
                    
                    return True
                    
                except Exception as e:
                    st.error(f"❌ Fehler beim Anlegen des Einsatzes: {str(e)}")
    
    return False

def validate_einsatz_form(schulname: str, schulart: str, stadt: str, landkreis: str, klassenstufe: str) -> bool:
    """Validiert das Einsatz-Formular"""
    
    if not schulname or not schulart or not stadt or not landkreis or not klassenstufe:
        st.error("❌ Bitte füllen Sie alle Pflichtfelder aus.")
        return False
    
    return True

def show_einsatz_list(einsatz_service: EinsatzService):
    """Zeigt die Einsatz-Liste an"""
    
    # Pagination
    page_size = 25
    page = st.session_state.einsatz_page
    
    # Filter anwenden
    filters = EinsatzFilter(**st.session_state.einsatz_filters)
    pagination = PaginationParams(page=page, size=page_size)
    
    try:
        einsaetze, total = einsatz_service.get_filtered(filters, pagination)
        
        if not einsaetze:
            st.info("Keine Einsätze gefunden.")
            return
        
        # Daten für DataFrame vorbereiten
        data = []
        for einsatz in einsaetze:
            data.append({
                'ID': einsatz.get('id', ''),
                'Name': einsatz.get('name', ''),
                'Beschreibung': einsatz.get('beschreibung', ''),
                'Start Datum': einsatz.get('start_datum', ''),
                'End Datum': einsatz.get('end_datum', ''),
                'Status': einsatz.get('status', ''),
                'Priorität': einsatz.get('prioritaet', ''),
                'Schüleranzahl': einsatz.get('schueleranzahl', ''),
                'Landkreis': einsatz.get('landkreis', ''),
                'Stadt': einsatz.get('stadt', ''),
                'Schulart': einsatz.get('schulart', ''),
                'Online': 'Ja' if einsatz.get('online') else 'Nein',
                'STUBO': 'Ja' if einsatz.get('stubo') else 'Nein',
                'Klassenstufe': einsatz.get('klassenstufe', ''),
                'Erstellt am': einsatz.get('created_at', ''),
                'Aktualisiert am': einsatz.get('updated_at', '')
            })
        
        df = pd.DataFrame(data)
        
        # DataFrame anzeigen
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )
        
        # Pagination
        total_pages = (total + page_size - 1) // page_size
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            if st.button("⏮️ Erste", disabled=page == 1):
                st.session_state.einsatz_page = 1
                st.rerun()
        
        with col2:
            if st.button("◀️ Vorherige", disabled=page == 1):
                st.session_state.einsatz_page = page - 1
                st.rerun()
        
        with col3:
            st.markdown(f"**Seite {page} von {total_pages}**")
        
        with col4:
            if st.button("▶️ Nächste", disabled=page >= total_pages):
                st.session_state.einsatz_page = page + 1
                st.rerun()
        
        with col5:
            if st.button("⏭️ Letzte", disabled=page >= total_pages):
                st.session_state.einsatz_page = total_pages
                st.rerun()
        
        st.markdown(f"**Gesamt: {total} Einsätze**")
        
    except Exception as e:
        st.error(f"❌ Fehler beim Laden der Einsatz-Liste: {str(e)}")

def import_einsatz_csv(uploaded_file, einsatz_service: EinsatzService):
    """Importiert Einsatz-Daten aus CSV"""
    
    try:
        file_content = uploaded_file.read()
        csv_service = CSVService()
        result = csv_service.import_einsatz_from_csv(file_content)
        
        if result.success:
            st.success(f"✅ CSV-Import erfolgreich! {result.imported_rows} von {result.total_rows} Zeilen importiert.")
        else:
            st.error(f"❌ CSV-Import fehlgeschlagen! {result.error_count} Fehler gefunden.")
            
            # Fehler anzeigen
            if result.errors:
                st.markdown("**Fehlerdetails:**")
                for error in result.errors[:10]:  # Maximal 10 Fehler anzeigen
                    st.error(f"Zeile {error['row']}, Feld '{error['field']}': {error['error']}")
        
        # Warnungen anzeigen
        if result.warnings:
            st.warning("**Warnungen:**")
            for warning in result.warnings[:5]:  # Maximal 5 Warnungen anzeigen
                st.warning(warning)
                
    except Exception as e:
        st.error(f"❌ Fehler beim CSV-Import: {str(e)}")

def export_einsatz_csv(einsatz_service: EinsatzService):
    """Exportiert Einsatz-Daten als CSV"""
    
    try:
        einsaetze, _ = einsatz_service.get_all()
        csv_service = CSVService()
        csv_data = csv_service.export_einsatz_to_csv(einsaetze)
        
        st.download_button(
            label="📥 CSV herunterladen",
            data=csv_data,
            file_name=f"einsatz_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
        
        st.success("✅ CSV-Export bereit!")
        
    except Exception as e:
        st.error(f"❌ Fehler beim CSV-Export: {str(e)}")

if __name__ == "__main__":
    einsatz_verwaltung_page()
