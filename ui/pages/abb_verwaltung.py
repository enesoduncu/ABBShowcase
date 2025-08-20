import streamlit as st
import pandas as pd
from datetime import date, datetime
from typing import Optional

from database import get_db
from services.abb_service import ABBService
from services.csv_service import CSVService
from schemas.abb import ABBCreate, ABBUpdate, ABBFilter
from schemas.common import PaginationParams

def abb_verwaltung_page():
    """ABB-Verwaltungsseite"""
    
    st.title("👥 ABB verwalten")
    st.markdown("Verwalten Sie Ausbildungsbotschafter (ABB)")
    
    # Session State initialisieren
    if 'abb_page' not in st.session_state:
        st.session_state.abb_page = 1
    if 'abb_filters' not in st.session_state:
        st.session_state.abb_filters = {}
    
    # ABB-Service initialisieren
    abb_service = ABBService()
    
    # Sidebar für Filter
    with st.sidebar:
        st.header("🔍 Filter")
        
        # Status-Filter
        status_filter = st.selectbox(
            "Status",
            ["Alle", "Aktiv", "Inaktiv"],
            index=0
        )
        
        # Kategorie-Filter
        kategorien = abb_service.get_kategorien()
        kategorie_filter = st.selectbox(
            "Kategorie",
            ["Alle"] + kategorien,
            index=0
        )
        
        # Suche
        suche = st.text_input("Suche (Name, Beschreibung)")
        
        # Filter anwenden
        if st.button("Filter anwenden"):
            st.session_state.abb_filters = {
                'aktiv': None if status_filter == "Alle" else status_filter == "Aktiv",
                'bereich': None if kategorie_filter == "Alle" else kategorie_filter,
                'suche': suche if suche else None
            }
            st.session_state.abb_page = 1
            st.rerun()
        
        # Filter zurücksetzen
        if st.button("Filter zurücksetzen"):
            st.session_state.abb_filters = {}
            st.session_state.abb_page = 1
            st.rerun()
    
    # Hauptbereich
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.subheader("📋 ABB-Liste")
    
    with col2:
        if st.button("➕ Neuen ABB anlegen", type="primary"):
            st.session_state.show_abb_form = True
    
    # ABB-Formular
    if st.session_state.get('show_abb_form', False):
        with st.expander("Neuen ABB anlegen", expanded=True):
            if abb_form():
                st.session_state.show_abb_form = False
                st.rerun()
    
    # ABB-Liste anzeigen
    show_abb_list(abb_service)
    
    # CSV-Import/Export
    st.subheader("📁 Import/Export")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**CSV-Import**")
        uploaded_file = st.file_uploader(
            "CSV-Datei hochladen",
            type=['csv'],
            help="Wählen Sie eine CSV-Datei mit ABB-Daten aus"
        )
        
        if uploaded_file is not None:
            if st.button("Import starten"):
                import_abb_csv(uploaded_file, abb_service)
    
    with col2:
        st.markdown("**CSV-Export**")
        if st.button("Alle ABB exportieren"):
            export_abb_csv(abb_service)

def abb_form() -> bool:
    """ABB-Formular für das Anlegen/Bearbeiten"""
    
    st.markdown("### ABB-Daten eingeben")
    
    with st.form("abb_form"):
        # Persönliche Daten
        st.markdown("#### Persönliche Daten")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            laufnummer = st.number_input("Laufnummer", min_value=1, step=1)
            vorname = st.text_input("Vorname *", max_chars=100)
            nachname = st.text_input("Nachname *", max_chars=100)
            geschlecht = st.selectbox("Geschlecht", ["", "m", "w", "d"], format_func=lambda x: {"": "", "m": "Männlich", "w": "Weiblich", "d": "Divers"}.get(x, x))
            geburtsdatum = st.date_input("Geburtsdatum")
        
        with col2:
            schulabschluss = st.text_input("Schulabschluss", max_chars=100)
            vorbildung = st.text_input("Vorbildung", max_chars=200)
            studienabbrecher = st.checkbox("Studienabbrecher", value=False)
            beruf = st.text_input("Beruf", max_chars=100)
            zq = st.text_input("ZQ", max_chars=100)
        
        with col3:
            bereich = st.selectbox("Bereich *", ["IHK", "HWK", "sonstiges"])
            ausbildungsbeginn = st.date_input("Ausbildungsbeginn")
            ausbildungsende = st.date_input("Ausbildungsende")
            schulungsdatum = st.date_input("Schulungsdatum")
        
        # Kontaktdaten
        st.markdown("#### Kontaktdaten")
        col1, col2 = st.columns(2)
        
        with col1:
            mobilnummer = st.text_input("Mobilnummer", max_chars=20)
            email_beruf = st.text_input("Email Beruf", max_chars=100)
            email_privat = st.text_input("Email Privat", max_chars=100)
            telefon_beruf = st.text_input("Telefon Beruf", max_chars=20)
            telefon_privat = st.text_input("Telefon Privat", max_chars=20)
        
        with col2:
            direktkontakt = st.checkbox("Direktkontakt erlaubt", value=False)
            betrieb = st.text_input("Betrieb", max_chars=200)
            betriebadresse = st.text_area("Betriebadresse", max_chars=500)
            landkreis_betrieb = st.text_input("Landkreis Betrieb", max_chars=100)
        
        # ASP-Daten
        st.markdown("#### ASP-Daten")
        col1, col2 = st.columns(2)
        
        with col1:
            asp_name = st.text_input("ASP Name", max_chars=100)
            asp_telefon = st.text_input("ASP Telefon", max_chars=20)
            asp_email = st.text_input("ASP Email", max_chars=100)
        
        with col2:
            eindruck = st.text_area("Eindruck", max_chars=1000, help="Persönlicher Eindruck vom ABB")
            hinweise = st.text_area("Hinweise", max_chars=1000, help="Zusätzliche Hinweise")
        
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
            if validate_abb_form(vorname, nachname, bereich):
                try:
                    abb_data = ABBCreate(
                        laufnummer=laufnummer if laufnummer else None,
                        aktiv=True,
                        vorname=vorname,
                        nachname=nachname,
                        geschlecht=geschlecht if geschlecht else None,
                        geburtsdatum=geburtsdatum,
                        schulabschluss=schulabschluss,
                        vorbildung=vorbildung,
                        studienabbrecher=studienabbrecher,
                        beruf=beruf,
                        zq=zq,
                        bereich=bereich,
                        ausbildungsbeginn=ausbildungsbeginn,
                        ausbildungsende=ausbildungsende,
                        schulungsdatum=schulungsdatum,
                        mobilnummer=mobilnummer,
                        email_beruf=email_beruf,
                        email_privat=email_privat,
                        telefon_beruf=telefon_beruf,
                        telefon_privat=telefon_privat,
                        direktkontakt=direktkontakt,
                        betrieb=betrieb,
                        betriebadresse=betriebadresse,
                        landkreis_betrieb=landkreis_betrieb,
                        asp_name=asp_name,
                        asp_telefon=asp_telefon,
                        asp_email=asp_email,
                        eindruck=eindruck,
                        hinweise=hinweise
                    )
                    
                    abb_service = ABBService()
                    abb_service.create(abb_data)
                    
                    st.success("ABB erfolgreich angelegt!")
                    return True
                    
                except Exception as e:
                    st.error(f"Fehler beim Anlegen des ABB: {str(e)}")
                    return False
    
    return False

def validate_abb_form(vorname: str, nachname: str, bereich: str) -> bool:
    """Validiert das ABB-Formular"""
    
    if not vorname or not nachname or not bereich:
        st.error("❌ Bitte füllen Sie alle Pflichtfelder aus.")
        return False
    
    return True

def show_abb_list(abb_service: ABBService):
    """Zeigt die ABB-Liste an"""
    
    # Pagination
    page_size = 25
    page = st.session_state.abb_page
    
    # Filter anwenden
    filters = ABBFilter(**st.session_state.abb_filters)
    pagination = PaginationParams(page=page, size=page_size)
    
    try:
        abbs, total = abb_service.get_filtered(filters, pagination)
        
        if not abbs:
            st.info("Keine ABB gefunden.")
            return
        
        # Daten für DataFrame vorbereiten
        data = []
        for abb in abbs:
            data.append({
                'ID': abb.get('id', ''),
                'Laufnummer': abb.get('laufnummer', ''),
                'Aktiv': 'Ja' if abb.get('aktiv') else 'Nein',
                'Vorname': abb.get('vorname', ''),
                'Nachname': abb.get('nachname', ''),
                'Geschlecht': abb.get('geschlecht', ''),
                'Geburtsdatum': abb.get('geburtsdatum', ''),
                'Schulabschluss': abb.get('schulabschluss', ''),
                'Vorbildung': abb.get('vorbildung', ''),
                'Studienabbrecher': 'Ja' if abb.get('studienabbrecher') else 'Nein',
                'Beruf': abb.get('beruf', ''),
                'ZQ': abb.get('zq', ''),
                'Bereich': abb.get('bereich', ''),
                'Ausbildungsbeginn': abb.get('ausbildungsbeginn', ''),
                'Ausbildungsende': abb.get('ausbildungsende', ''),
                'Schulungsdatum': abb.get('schulungsdatum', ''),
                'Mobilnummer': abb.get('mobilnummer', ''),
                'Email Beruf': abb.get('email_beruf', ''),
                'Email Privat': abb.get('email_privat', ''),
                'Telefon Beruf': abb.get('telefon_beruf', ''),
                'Telefon Privat': abb.get('telefon_privat', ''),
                'Direktkontakt': 'Ja' if abb.get('direktkontakt') else 'Nein',
                'Betrieb': abb.get('betrieb', ''),
                'Betriebadresse': abb.get('betriebadresse', ''),
                'Landkreis Betrieb': abb.get('landkreis_betrieb', ''),
                'ASP Name': abb.get('asp_name', ''),
                'ASP Telefon': abb.get('asp_telefon', ''),
                'ASP Email': abb.get('asp_email', ''),
                'Eindruck': abb.get('eindruck', ''),
                'Hinweise': abb.get('hinweise', ''),
                'Erstellt am': abb.get('created_at', ''),
                'Aktualisiert am': abb.get('updated_at', '')
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
                st.session_state.abb_page = 1
                st.rerun()
        
        with col2:
            if st.button("◀️ Vorherige", disabled=page == 1):
                st.session_state.abb_page = page - 1
                st.rerun()
        
        with col3:
            st.markdown(f"**Seite {page} von {total_pages}**")
        
        with col4:
            if st.button("▶️ Nächste", disabled=page >= total_pages):
                st.session_state.abb_page = page + 1
                st.rerun()
        
        with col5:
            if st.button("⏭️ Letzte", disabled=page >= total_pages):
                st.session_state.abb_page = total_pages
                st.rerun()
        
        st.markdown(f"**Gesamt: {total} ABB**")
        
    except Exception as e:
        st.error(f"Fehler beim Laden der ABB-Liste: {str(e)}")

def import_abb_csv(uploaded_file, abb_service: ABBService):
    """Importiert ABB-Daten aus CSV"""
    
    try:
        file_content = uploaded_file.read()
        csv_service = CSVService()
        result = csv_service.import_abb_from_csv(file_content)
        
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

def export_abb_csv(abb_service: ABBService):
    """Exportiert ABB-Daten als CSV"""
    
    try:
        abbs, _ = abb_service.get_all()
        csv_service = CSVService()
        csv_data = csv_service.export_abb_to_csv(abbs)
        
        st.download_button(
            label="📥 CSV herunterladen",
            data=csv_data,
            file_name=f"abb_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
        
        st.success("✅ CSV-Export bereit!")
        
    except Exception as e:
        st.error(f"❌ Fehler beim CSV-Export: {str(e)}")

if __name__ == "__main__":
    abb_verwaltung_page()
