import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from datetime import date, datetime, timedelta
from typing import Optional, List

# get_db wird nicht mehr benötigt
from services.abb_service import ABBService
from services.einsatz_service import EinsatzService
from services.link_service import LinkService
from services.csv_service import CSVService

def berichte_page():
    """Berichtsseite mit verschiedenen Auswertungen"""
    
    st.title("📊 Berichte & Auswertungen")
    st.markdown("Verschiedene Auswertungen und Exportmöglichkeiten")
    
    # Services initialisieren
    abb_service = ABBService()
    einsatz_service = EinsatzService()
    link_service = LinkService()
    
    # Tabs für verschiedene Berichte
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Dashboard", "🏫 Schuleinsätze", "👥 ABB-Statistiken", "🔗 Zuordnungen"])
    
    with tab1:
        dashboard_bericht(abb_service, einsatz_service, link_service)
    
    with tab2:
        einsatz_bericht(einsatz_service, link_service)
    
    with tab3:
        abb_bericht(abb_service, link_service)
    
    with tab4:
        zuordnungs_bericht(link_service, abb_service, einsatz_service)

def dashboard_bericht(abb_service: ABBService, einsatz_service: EinsatzService, link_service: LinkService):
    """Dashboard-Bericht mit KPI und Diagrammen"""
    
    st.subheader("📈 Dashboard-Übersicht")
    
    # KPI-Kacheln
    col1, col2, col3, col4 = st.columns(4)
    
    try:
        # ABB-Statistiken
        abb_stats = abb_service.get_statistics()
        
        with col1:
            st.metric(
                "Aktive ABB",
                abb_stats.get('aktiv_gesamt', 0),
                help="Anzahl der aktiven Ausbildungsbotschafter"
            )
        
        with col2:
            st.metric(
                "Direktkontakt",
                abb_stats.get('direktkontakt', 0),
                help="ABB mit erlaubtem Direktkontakt"
            )
        
        # Einsatz-Statistiken
        einsatz_stats = einsatz_service.get_statistics()
        
        with col3:
            st.metric(
                "Einsätze YTD",
                einsatz_stats.get('einsaetze_ytd', 0),
                help="Einsätze im aktuellen Jahr"
            )
        
        with col4:
            st.metric(
                "Durchschnitt Schüler",
                f"{einsatz_stats.get('durchschnitt_schueler', 0):.1f}",
                help="Durchschnittliche Schüleranzahl pro Einsatz"
            )
        
        # Diagramme
        st.markdown("### 📊 Visualisierungen")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Einsätze pro Landkreis**")
            
            if einsatz_stats.get('nach_landkreis'):
                landkreis_data = einsatz_stats['nach_landkreis']
                
                # Plotly-Balkendiagramm
                fig = px.bar(
                    x=list(landkreis_data.keys()),
                    y=list(landkreis_data.values()),
                    title="Einsätze nach Landkreis",
                    labels={'x': 'Landkreis', 'y': 'Anzahl Einsätze'}
                )
                fig.update_layout(showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Keine Daten für Landkreis-Statistiken verfügbar")
        
        with col2:
            st.markdown("**Online vs. Präsenz**")
            
            if einsatz_stats.get('online_vs_praesenz'):
                online_data = einsatz_stats['online_vs_praesenz']
                
                # Plotly-Kreisdiagramm
                fig = px.pie(
                    values=list(online_data.values()),
                    names=list(online_data.keys()),
                    title="Verteilung Online/Präsenz"
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Keine Daten für Online/Präsenz-Statistiken verfügbar")
        
        # ABB nach Bereich
        st.markdown("**ABB nach Bereich**")
        
        if abb_stats.get('nach_bereich'):
            bereich_data = abb_stats['nach_bereich']
            
            fig = px.bar(
                x=list(bereich_data.keys()),
                y=list(bereich_data.values()),
                title="ABB nach Bereich",
                labels={'x': 'Bereich', 'y': 'Anzahl ABB'}
            )
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        
        # Top-Schulen
        st.markdown("**Top-Schulen (Top 10)**")
        
        if einsatz_stats.get('top_schulen'):
            schul_data = einsatz_stats['top_schulen']
            
            # Top 10 Schulen
            top_schulen = dict(sorted(schul_data.items(), key=lambda x: x[1], reverse=True)[:10])
            
            fig = px.bar(
                x=list(top_schulen.values()),
                y=list(top_schulen.keys()),
                orientation='h',
                title="Top-Schulen nach Anzahl Einsätze",
                labels={'x': 'Anzahl Einsätze', 'y': 'Schule'}
            )
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"❌ Fehler beim Laden der Dashboard-Daten: {str(e)}")

def einsatz_bericht(einsatz_service: EinsatzService, link_service: LinkService):
    """Bericht über Schuleinsätze"""
    
    st.subheader("🏫 Schuleinsätze - Auswertungen")
    
    # Filter
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Zeitraum**")
        datum_von = st.date_input("Von", value=date.today() - timedelta(days=30))
        datum_bis = st.date_input("Bis", value=date.today())
    
    with col2:
        st.markdown("**Landkreis**")
        landkreise = einsatz_service.get_landkreise()
        selected_landkreis = st.selectbox("Landkreis auswählen", ["Alle"] + landkreise)
    
    # Bericht generieren
    if st.button("📊 Bericht generieren", type="primary"):
        try:
            # Filter anwenden
            filters = {}
            if datum_von:
                filters['start_datum_von'] = datum_von
            if datum_bis:
                filters['start_datum_bis'] = datum_bis
            if selected_landkreis != "Alle":
                filters['beschreibung'] = selected_landkreis
            
            # Einsätze laden
            einsaetze, total = einsatz_service.get_filtered(filters)
            
            if not einsaetze:
                st.info("Keine Einsätze im gewählten Zeitraum gefunden.")
                return
            
            # Statistiken berechnen
            st.markdown("### 📈 Zusammenfassung")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Gesamt Einsätze", total)
            
            with col2:
                online_count = sum(1 for e in einsaetze if e.get('online'))
                st.metric("Online", online_count)
            
            with col3:
                praesenz_count = sum(1 for e in einsaetze if not e.get('online'))
                st.metric("Präsenz", praesenz_count)
            
            with col4:
                stubo_count = sum(1 for e in einsaetze if e.get('stubo'))
                st.metric("Mit STUBO", stubo_count)
            
            # Detaillierte Tabelle
            st.markdown("### 📋 Detaillierte Übersicht")
            
            data = []
            for einsatz in einsaetze:
                # ABB-Statistiken für diesen Einsatz
                einsatz_stats = link_service.get_einsatz_statistics(einsatz.id)
                
                data.append({
                    'ID': einsatz.get('id', ''),
                    'Datum': einsatz.get('start_datum', ''),
                    'Schule': einsatz.get('name', ''),
                    'Schulart': einsatz.get('beschreibung', '').split(',')[0] if einsatz.get('beschreibung') else '',
                    'Stadt': einsatz.get('beschreibung', '').split(',')[2] if einsatz.get('beschreibung') and len(einsatz.get('beschreibung', '').split(',')) > 2 else '',
                    'Landkreis': einsatz.get('beschreibung', '').split(',')[3] if einsatz.get('beschreibung') and len(einsatz.get('beschreibung', '').split(',')) > 3 else '',
                    'Format': '💻 Online' if einsatz.get('online') else '🏫 Präsenz',
                    'STUBO': '✅' if einsatz.get('stubo') else '❌',
                    'Klassenstufe': einsatz.get('beschreibung', '').split(',')[7] if einsatz.get('beschreibung') and len(einsatz.get('beschreibung', '').split(',')) > 7 else '',
                    'Schüler': einsatz.get('beschreibung', '').split(',')[8] if einsatz.get('beschreibung') and len(einsatz.get('beschreibung', '').split(',')) > 8 else '',
                    'ABB zugeordnet': einsatz_stats.get('abb_anzahl', 0)
                })
            
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            # Export
            st.markdown("### 📥 Export")
            
            if st.button("📊 Als CSV exportieren"):
                csv_service = CSVService()
                csv_data = csv_service.export_einsatz_to_csv(einsaetze)
                
                st.download_button(
                    label="📥 CSV herunterladen",
                    data=csv_data,
                    file_name=f"einsatz_bericht_{datum_von.strftime('%Y%m%d')}_{datum_bis.strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
                
                st.success("✅ CSV-Export bereit!")
            
        except Exception as e:
            st.error(f"❌ Fehler beim Generieren des Berichts: {str(e)}")

def abb_bericht(abb_service: ABBService, link_service: LinkService):
    """Bericht über ABB-Statistiken"""
    
    st.subheader("👥 ABB-Statistiken")
    
    # Filter
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Bereich**")
        bereiche = abb_service.get_berufe() if hasattr(abb_service, 'get_berufe') else []
        selected_bereich = st.selectbox("Bereich auswählen", ["Alle"] + bereiche)
    
    with col2:
        st.markdown("**Status**")
        status_filter = st.selectbox("Status", ["Alle", "Aktiv", "Inaktiv"])
    
    # Bericht generieren
    if st.button("📊 ABB-Bericht generieren", type="primary"):
        try:
            # Filter anwenden
            filters = {}
            if selected_bereich != "Alle":
                filters['bereich'] = selected_bereich
            if status_filter != "Alle":
                filters['aktiv'] = status_filter == "Aktiv"
            
            # ABB laden
            abbs, total = abb_service.get_filtered(filters)
            
            if not abbs:
                st.info("Keine ABB mit den gewählten Filtern gefunden.")
                return
            
            # Statistiken berechnen
            st.markdown("### 📈 ABB-Übersicht")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Gesamt ABB", total)
            
            with col2:
                aktiv_count = sum(1 for a in abbs if a.aktiv)
                st.metric("Aktiv", aktiv_count)
            
            with col3:
                inaktiv_count = sum(1 for a in abbs if not a.aktiv)
                st.metric("Inaktiv", inaktiv_count)
            
            with col4:
                direktkontakt_count = sum(1 for a in abbs if a.direktkontakt)
                st.metric("Direktkontakt", direktkontakt_count)
            
            # Detaillierte Tabelle
            st.markdown("### 📋 ABB-Details")
            
            data = []
            for abb in abbs:
                # Einsatz-Statistiken für diesen ABB
                abb_stats = link_service.get_abb_statistics(abb.id)
                
                data.append({
                    'ID': abb.get('id', ''),
                    'Name': f"{abb.get('vorname', '')} {abb.get('nachname', '')}",
                    'Beruf': abb.get('beruf', ''),
                    'Bereich': abb.get('bereich', ''),
                    'Status': '🟢 Aktiv' if abb.get('aktiv') else '🔴 Inaktiv',
                    'Direktkontakt': '✅' if abb.get('direktkontakt') else '❌',
                    'Landkreis': abb.get('landkreis_betrieb') or '-',
                    'Ausbildungsbeginn': abb.get('ausbildungsbeginn', ''),
                    'Einsätze': abb_stats.get('einsatz_anzahl', 0)
                })
            
            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            # Export
            st.markdown("### 📥 Export")
            
            if st.button("📊 ABB als CSV exportieren"):
                csv_service = CSVService()
                csv_data = csv_service.export_abb_to_csv(abbs)
                
                st.download_button(
                    label="📥 CSV herunterladen",
                    data=csv_data,
                    file_name=f"abb_bericht_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
                
                st.success("✅ CSV-Export bereit!")
            
        except Exception as e:
            st.error(f"❌ Fehler beim Generieren des ABB-Berichts: {str(e)}")

def zuordnungs_bericht(link_service: LinkService, abb_service: ABBService, einsatz_service: EinsatzService):
    """Bericht über Zuordnungen"""
    
    st.subheader("🔗 Zuordnungs-Statistiken")
    
    try:
        # Alle Zuordnungen laden
        links, total = link_service.get_all_links()
        
        if not links:
            st.info("Keine Zuordnungen vorhanden.")
            return
        
        # Statistiken
        st.markdown("### 📊 Übersicht")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Gesamt Zuordnungen", total)
        
        with col2:
            # ABB mit den meisten Einsätzen
            abb_einsatz_count = {}
            for link in links:
                abb_id = link.get('abb_id')
                if abb_id not in abb_einsatz_count:
                    abb_einsatz_count[abb_id] = 0
                abb_einsatz_count[abb_id] += 1
            
            if abb_einsatz_count:
                max_einsaetze = max(abb_einsatz_count.values())
                st.metric("Max. Einsätze pro ABB", max_einsaetze)
            else:
                st.metric("Max. Einsätze pro ABB", 0)
        
        with col3:
            # Einsätze mit den meisten ABB
            einsatz_abb_count = {}
            for link in links:
                einsatz_id = link.get('einsatz_id')
                if einsatz_id not in einsatz_abb_count:
                    einsatz_abb_count[einsatz_id] = 0
                einsatz_abb_count[einsatz_id] += 1
            
            if einsatz_abb_count:
                max_abb = max(einsatz_abb_count.values())
                st.metric("Max. ABB pro Einsatz", max_abb)
            else:
                st.metric("Max. ABB pro Einsatz", 0)
        
        # Top ABB nach Einsätzen
        st.markdown("### 👥 Top ABB nach Einsätzen")
        
        if abb_einsatz_count:
            # Top 10 ABB
            top_abb = sorted(abb_einsatz_count.items(), key=lambda x: x[1], reverse=True)[:10]
            
            top_abb_data = []
            for abb_id, count in top_abb:
                abb = abb_service.get_by_id(abb_id)
                if abb:
                    top_abb_data.append({
                        'Name': f"{abb.get('vorname', '')} {abb.get('nachname', '')}",
                        'Beruf': abb.get('beruf', ''),
                        'Bereich': abb.get('bereich', ''),
                        'Einsätze': count
                    })
            
            if top_abb_data:
                top_df = pd.DataFrame(top_abb_data)
                st.dataframe(top_df, use_container_width=True, hide_index=True)
                
                # Diagramm
                fig = px.bar(
                    top_df,
                    x='Einsätze',
                    y='Name',
                    orientation='h',
                    title="Top 10 ABB nach Anzahl Einsätze"
                )
                st.plotly_chart(fig, use_container_width=True)
        
        # Top Einsätze nach ABB
        st.markdown("### 🏫 Top Einsätze nach ABB")
        
        if einsatz_abb_count:
            # Top 10 Einsätze
            top_einsaetze = sorted(einsatz_abb_count.items(), key=lambda x: x[1], reverse=True)[:10]
            
            top_einsatz_data = []
            for einsatz_id, count in top_einsaetze:
                einsatz = einsatz_service.get_by_id(einsatz_id)
                if einsatz:
                    top_einsatz_data.append({
                        'Schule': einsatz.get('name', ''),
                        'Datum': einsatz.get('start_datum', ''),
                        'Stadt': einsatz.get('beschreibung', '').split(',')[2] if einsatz.get('beschreibung') and len(einsatz.get('beschreibung', '').split(',')) > 2 else '',
                        'ABB': count
                    })
            
            if top_einsatz_data:
                top_einsatz_df = pd.DataFrame(top_einsatz_data)
                st.dataframe(top_einsatz_df, use_container_width=True, hide_index=True)
                
                # Diagramm
                fig = px.bar(
                    top_einsatz_df,
                    x='ABB',
                    y='Schule',
                    orientation='h',
                    title="Top 10 Einsätze nach Anzahl ABB"
                )
                st.plotly_chart(fig, use_container_width=True)
        
        # Export
        st.markdown("### 📥 Export")
        
        if st.button("📊 Alle Zuordnungen als CSV exportieren"):
            csv_service = CSVService()
            csv_data = csv_service.export_abb_einsatz_to_csv(links)
            
            st.download_button(
                label="📥 CSV herunterladen",
                data=csv_data,
                file_name=f"zuordnungen_bericht_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
            
            st.success("✅ CSV-Export bereit!")
        
    except Exception as e:
        st.error(f"❌ Fehler beim Laden der Zuordnungs-Statistiken: {str(e)}")

if __name__ == "__main__":
    berichte_page()
