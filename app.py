import streamlit as st
import database
from database import create_tables
import config
import pandas as pd
from datetime import datetime

# Authentifizierung importieren
from auth import AuthManager, check_authentication, login_page, show_user_info, force_password_change_page

# Services importieren
from services.abb_service import ABBService
from services.einsatz_service import EinsatzService
from services.link_service import LinkService

# Seiten importieren
from ui.pages.abb_verwaltung import abb_verwaltung_page
from ui.pages.einsatz_verwaltung import einsatz_verwaltung_page
from ui.pages.zuordnungen import zuordnungen_page
from ui.pages.berichte import berichte_page
from ui.pages.einstellungen import einstellungen_page
from ui.pages.benutzer_verwaltung import benutzer_verwaltung_page

# Seitenkonfiguration
st.set_page_config(
    page_title="ABB Streamlit - Ausbildungsbotschafter Verwaltung",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS für besseres Styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .stButton > button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

def main():
    """Hauptfunktion der Anwendung"""
    
    # Authentifizierung initialisieren
    auth_manager = AuthManager()
    
    # Überprüfen, ob der Benutzer angemeldet ist
    if not check_authentication():
        login_page(auth_manager)
        return
    
    # Überprüfen, ob Passwort-Änderung erforderlich ist
    if st.session_state.user and st.session_state.user.get('force_password_change'):
        force_password_change_page(auth_manager)
        return
    
    # Datenbank initialisieren
    try:
        create_tables()
    except Exception as e:
        st.error(f"❌ Fehler bei der Datenbankinitialisierung: {str(e)}")
        return
    
    # Sidebar für Navigation
    with st.sidebar:
        st.markdown('<h1 class="main-header">🎓 ABB Streamlit</h1>', unsafe_allow_html=True)
        st.markdown("---")
        
        # Benutzerinformationen anzeigen
        show_user_info()
        
        # Navigation
        navigation_options = ["🏠 Dashboard", "👥 ABB verwalten", "📅 Einsätze verwalten", "🔗 Zuordnungen", "📊 Berichte", "⚙️ Einstellungen"]
        
        # Benutzerverwaltung nur für Admins anzeigen
        if st.session_state.user and st.session_state.user.get('role') == 'admin':
            navigation_options.append("👥 Benutzerverwaltung")
        
        page = st.selectbox(
            "Navigation",
            navigation_options
        )
    
    # Seiteninhalt basierend auf Auswahl
    if page == "🏠 Dashboard":
        dashboard_page()
    elif page == "👥 ABB verwalten":
        abb_verwaltung_page()
    elif page == "📅 Einsätze verwalten":
        einsatz_verwaltung_page()
    elif page == "🔗 Zuordnungen":
        zuordnungen_page()
    elif page == "📊 Berichte":
        berichte_page()
    elif page == "⚙️ Einstellungen":
        einstellungen_page()
    elif page == "👥 Benutzerverwaltung":
        benutzer_verwaltung_page()

def dashboard_page():
    """Dashboard-Seite"""
    
    # Header
    st.markdown('<h1 class="main-header">🎓 ABB Streamlit</h1>', unsafe_allow_html=True)
    st.markdown('<h2 style="text-align: center; color: #666;">Ausbildungsbotschafter Verwaltung</h2>', unsafe_allow_html=True)
    
    # Services initialisieren
    abb_service = ABBService()
    einsatz_service = EinsatzService()
    link_service = LinkService()
    
    # Dashboard
    st.header("📊 Dashboard")
    
    try:
        # KPI-Kacheln
        col1, col2, col3, col4 = st.columns(4)
        
        # ABB-Statistiken
        abb_stats = abb_service.get_statistics()
        
        with col1:
            st.metric(
                "Aktive ABB",
                abb_stats.get('aktiv_gesamt', 0),
                help="Anzahl der aktiven Ausbildungsbotschafter"
            )
        
        with col2:
            # Direktkontakt-Statistik
            direktkontakt_count = sum(1 for abb in abb_service.get_all()[0] if abb.get('direktkontakt'))
            st.metric(
                "Direktkontakt",
                direktkontakt_count,
                help="ABB mit erlaubtem Direktkontakt"
            )
        
        # Einsatz-Statistiken
        einsatz_stats = einsatz_service.get_statistics()
        
        with col3:
            # Einsätze im aktuellen Jahr
            current_year = datetime.now().year
            einsaetze_ytd = sum(1 for einsatz in einsatz_service.get_all()[0] 
                               if einsatz.get('start_datum') and str(einsatz.get('start_datum')).startswith(str(current_year)))
            st.metric(
                "Einsätze YTD",
                einsaetze_ytd,
                help="Einsätze im aktuellen Jahr"
            )
        
        with col4:
            # Durchschnittliche Schüleranzahl
            einsaetze = einsatz_service.get_all()[0]
            if einsaetze:
                total_schueler = sum(einsatz.get('schueleranzahl', 0) for einsatz in einsaetze)
                avg_schueler = total_schueler / len(einsaetze) if einsaetze else 0
            else:
                avg_schueler = 0
            st.metric(
                "Durchschnitt Schüler",
                f"{avg_schueler:.1f}",
                help="Durchschnittliche Schüleranzahl pro Einsatz"
            )
        
        # Diagramme
        st.subheader("📊 Visualisierungen")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Einsätze pro Landkreis**")
            
            if einsatz_stats.get('nach_landkreis'):
                landkreis_data = einsatz_stats['nach_landkreis']
                st.bar_chart(landkreis_data)
            else:
                st.info("Keine Daten für Landkreis-Statistiken verfügbar")
        
        with col2:
            st.markdown("**Online vs. Präsenz**")
            
            online_count = sum(1 for einsatz in einsaetze if einsatz.get('online'))
            praesenz_count = len(einsaetze) - online_count
            
            if einsaetze:
                online_data = {'Online': online_count, 'Präsenz': praesenz_count}
                st.bar_chart(online_data)
            else:
                st.info("Keine Daten für Online/Präsenz-Statistiken verfügbar")
        
        # ABB nach Bereich
        st.subheader("👥 ABB nach Bereich")
        if abb_stats.get('nach_bereich'):
            bereich_data = abb_stats['nach_bereich']
            st.bar_chart(bereich_data)
        else:
            st.info("Keine ABB-Daten verfügbar")
        
        # Top-Schulen
        st.subheader("🏫 Top-Schulen (Top 10)")
        if einsaetze:
            schulen_count = {}
            for einsatz in einsaetze:
                schulname = einsatz.get('name', 'Unbekannt')
                schulen_count[schulname] = schulen_count.get(schulname, 0) + 1
            
            top_schulen = sorted(schulen_count.items(), key=lambda x: x[1], reverse=True)[:10]
            if top_schulen:
                schulen_df = pd.DataFrame(top_schulen, columns=['Schule', 'Anzahl Einsätze'])
                st.dataframe(schulen_df, use_container_width=True)
            else:
                st.info("Keine Schuldaten verfügbar")
        else:
            st.info("Keine Einsätze verfügbar")
        
    except Exception as e:
        st.error(f"Fehler beim Laden der Dashboard-Daten: {str(e)}")
    
    # Schnellaktionen
    st.subheader("⚡ Schnellaktionen")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("➕ Neuen ABB anlegen", type="primary"):
            st.session_state.page = "👥 ABB verwalten"
            st.rerun()
    
    with col2:
        if st.button("📅 Neuen Einsatz anlegen", type="primary"):
            st.session_state.page = "📅 Einsätze verwalten"
            st.rerun()
    
    with col3:
        if st.button("🔗 ABB zuordnen", type="primary"):
            st.session_state.page = "🔗 Zuordnungen"
            st.rerun()
    
    # Footer
    st.markdown("---")
    st.markdown("**ABB Streamlit** - Eine moderne Verwaltungsanwendung für Ausbildungsbotschafter")
    st.markdown(f"Version: 1.0.0 | Datenbank: {config.DATABASE_URL}")

if __name__ == "__main__":
    main()
