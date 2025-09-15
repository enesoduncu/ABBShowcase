import streamlit as st
import pandas as pd
from datetime import date, datetime
from typing import Optional, List

from database import get_db
from services.link_service import LinkService
from services.abb_service import ABBService
from services.einsatz_service import EinsatzService
from services.csv_service import CSVService
from schemas.abb_einsatz import ABBEinsatzCreate, ABBEinsatzUpdate

def zuordnungen_page():
    """Zuordnungsseite für ABB-Einsatz-Verknüpfungen"""
    
    st.title("🔗 Zuordnungen verwalten")
    st.markdown("Verknüpfen Sie ABB mit Einsätzen")
    
    # Session State initialisieren
    if 'zuordnung_tab' not in st.session_state:
        st.session_state.zuordnung_tab = "einsatz_based"
    
    # Services initialisieren
    link_service = LinkService()
    abb_service = ABBService()
    einsatz_service = EinsatzService()
    
    # Tabs für verschiedene Ansichten
    tab1, tab2, tab3 = st.tabs(["📋 Pro Einsatz", "👥 Pro ABB", "📊 Übersicht"])
    
    with tab1:
        einsatz_based_zuordnungen(link_service, einsatz_service, abb_service)
    
    with tab2:
        abb_based_zuordnungen(link_service, abb_service, einsatz_service)
    
    with tab3:
        zuordnungs_uebersicht(link_service, abb_service, einsatz_service)

def einsatz_based_zuordnungen(link_service: LinkService, einsatz_service: EinsatzService, abb_service: ABBService):
    """Zuordnungen pro Einsatz verwalten"""
    
    st.subheader("📋 ABB zu Einsätzen zuordnen")
    
    # Einsatz auswählen
    einsaetze, _ = einsatz_service.get_all()
    
    if not einsaetze:
        st.info("Keine Einsätze vorhanden. Bitte legen Sie zuerst Einsätze an.")
        return
    
    einsatz_options = {f"{e.get('name', 'Unbekannt')} - {e.get('start_datum', '')}": e.get('id') for e in einsaetze}
    selected_einsatz_name = st.selectbox("Einsatz auswählen", list(einsatz_options.keys()), key="einsatz_based_einsatz_select")
    
    if selected_einsatz_name:
        selected_einsatz_id = einsatz_options[selected_einsatz_name]
        selected_einsatz = einsatz_service.get_by_id(selected_einsatz_id)
        
        if selected_einsatz:
            st.markdown(f"**Ausgewählter Einsatz:** {selected_einsatz.get('name', 'Unbekannt')} - {selected_einsatz.get('start_datum', '')}")
            st.markdown(f"**Beschreibung:** {selected_einsatz.get('beschreibung', 'Keine Beschreibung')}")
            
            # Bereits zugeordnete ABB anzeigen
            st.markdown("### Bereits zugeordnete ABB")
            assigned_links = link_service.get_links_by_einsatz(selected_einsatz_id)
            
            if assigned_links:
                assigned_data = []
                for link in assigned_links:
                    abb = abb_service.get_by_id(link.get('abb_id'))
                    if abb:
                                                 assigned_data.append({
                             'ID': link.get('id', ''),
                             'Name': f"{abb.get('vorname', '')} {abb.get('nachname', '')}",
                             'Beruf': abb.get('beruf', ''),
                             'Bereich': abb.get('bereich', ''),
                             'Notizen': link.get('notizen', '')
                         })
                
                assigned_df = pd.DataFrame(assigned_data)
                st.dataframe(assigned_df, use_container_width=True, hide_index=True)
                
                # ABB entfernen
                st.markdown("### ABB entfernen")
                remove_abb_id = st.selectbox(
                    "ABB zum Entfernen auswählen",
                    [link.get('abb_id') for link in assigned_links],
                    format_func=lambda x: f"{abb_service.get_by_id(x).get('vorname', '')} {abb_service.get_by_id(x).get('nachname', '')}" if abb_service.get_by_id(x) else f"ABB ID {x}",
                    key="einsatz_based_abb_remove_select"
                )
                
                if st.button("❌ ABB entfernen"):
                    if link_service.remove_abb_from_einsatz(remove_abb_id, selected_einsatz_id):
                        st.success("✅ ABB erfolgreich entfernt!")
                        st.rerun()
                    else:
                        st.error("❌ Fehler beim Entfernen des ABB")
            else:
                st.info("Noch keine ABB zugeordnet.")
            
            # Neue ABB zuordnen
            st.markdown("### Neue ABB zuordnen")
            
            # Verfügbare ABB anzeigen
            available_abbs = link_service.get_available_abbs_for_einsatz(selected_einsatz_id)
            
            if available_abbs:
                abb_options = {f"{abb.get('vorname', '')} {abb.get('nachname', '')} (ID: {abb.get('id', '?')})": abb.get('id') for abb in available_abbs}
                selected_abb_name = st.selectbox("ABB auswählen", list(abb_options.keys()))
                
                if selected_abb_name:
                    selected_abb_id = abb_options[selected_abb_name]
                    
                    # Zuordnungsdetails
                    kommentar = st.text_area("Notizen (optional)", max_chars=500)
                    
                    if st.button("✅ ABB zuordnen", type="primary"):
                        try:
                            link_service.assign_abb_to_einsatz(
                                selected_abb_id, 
                                selected_einsatz_id, 
                                None,  # rolle wird nicht mehr verwendet
                                kommentar if kommentar else None
                            )
                            st.success("✅ ABB erfolgreich zugeordnet!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Fehler beim Zuordnen: {str(e)}")
            else:
                st.info("Alle verfügbaren ABB sind bereits diesem Einsatz zugeordnet.")
            
            # Bulk-Zuordnung
            st.markdown("### Mehrere ABB gleichzeitig zuordnen")
            
            if available_abbs:
                selected_abb_ids = st.multiselect(
                    "Mehrere ABB auswählen",
                    options=[abb.get('id') for abb in available_abbs],
                    format_func=lambda x: f"{abb_service.get_by_id(x).get('vorname', '')} {abb_service.get_by_id(x).get('nachname', '')}" if abb_service.get_by_id(x) else f"ABB ID {x}"
                )
                
                bulk_rolle = st.text_input("Rolle für alle (optional)", max_chars=100)
                
                if st.button("✅ Mehrere ABB zuordnen", type="primary"):
                    if selected_abb_ids:
                        try:
                            created_links = link_service.bulk_assign_abbs_to_einsatz(
                                selected_abb_ids, 
                                selected_einsatz_id, 
                                bulk_rolle if bulk_rolle else None
                            )
                            st.success(f"✅ {len(created_links)} ABB erfolgreich zugeordnet!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Fehler bei der Bulk-Zuordnung: {str(e)}")
                    else:
                        st.warning("Bitte wählen Sie mindestens einen ABB aus.")

def abb_based_zuordnungen(link_service: LinkService, abb_service: ABBService, einsatz_service: EinsatzService):
    """Zuordnungen pro ABB verwalten"""
    
    st.subheader("👥 Einsätze zu ABB zuordnen")
    
    # ABB auswählen
    abbs, _ = abb_service.get_all()
    
    if not abbs:
        st.info("Keine ABB vorhanden. Bitte legen Sie zuerst ABB an.")
        return
    
    # ABB-Name aus den Dictionary-Daten extrahieren
    abb_options = {f"{abb.get('vorname', '')} {abb.get('nachname', '')} (ID: {abb.get('id', '?')})": abb.get('id') for abb in abbs}
    selected_abb_name = st.selectbox("ABB auswählen", list(abb_options.keys()), key="abb_based_abb_select")
    
    if selected_abb_name:
        selected_abb_id = abb_options[selected_abb_name]
        selected_abb = abb_service.get_by_id(selected_abb_id)
        
        if selected_abb:
            st.markdown(f"**Ausgewählter ABB:** {selected_abb.get('vorname', '')} {selected_abb.get('nachname', '')}")
            st.markdown(f"**Beruf:** {selected_abb.get('beruf', 'Keine Angabe')}")
            st.markdown(f"**Bereich:** {selected_abb.get('bereich', 'Unbekannt')}")
            st.markdown(f"**Status:** {'🟢 Aktiv' if selected_abb.get('aktiv') else '🔴 Inaktiv'}")
            
            # Bereits zugeordnete Einsätze anzeigen
            st.markdown("### Bereits zugeordnete Einsätze")
            assigned_links = link_service.get_links_by_abb(selected_abb_id)
            
            if assigned_links:
                assigned_data = []
                for link in assigned_links:
                    einsatz = einsatz_service.get_by_id(link.get('einsatz_id'))
                    if einsatz:
                        assigned_data.append({
                            'ID': link.get('id', ''),
                            'Name': einsatz.get('name', ''),
                            'Beschreibung': einsatz.get('beschreibung', ''),
                            'Start Datum': einsatz.get('start_datum', ''),
                            'Status': einsatz.get('status', ''),
                            'Notizen': link.get('notizen', '')
                        })
                
                assigned_df = pd.DataFrame(assigned_data)
                st.dataframe(assigned_df, use_container_width=True, hide_index=True)
                
                # Einsatz entfernen
                st.markdown("### Einsatz entfernen")
                remove_einsatz_id = st.selectbox(
                    "Einsatz zum Entfernen auswählen",
                    [link.get('einsatz_id') for link in assigned_links],
                    format_func=lambda x: f"{einsatz_service.get_by_id(x).get('name', 'Unbekannt')} - {einsatz_service.get_by_id(x).get('start_datum', '')}" if einsatz_service.get_by_id(x) else f"Einsatz ID {x}",
                    key="abb_based_einsatz_remove_select"
                )
                
                if st.button("❌ Einsatz entfernen"):
                    if link_service.remove_abb_from_einsatz(selected_abb_id, remove_einsatz_id):
                        st.success("✅ Einsatz erfolgreich entfernt!")
                        st.rerun()
                    else:
                        st.error("❌ Fehler beim Entfernen des Einsatzes")
            else:
                st.info("Noch keine Einsätze zugeordnet.")
            
            # Neue Einsätze zuordnen
            st.markdown("### Neue Einsätze zuordnen")
            
            # Verfügbare Einsätze anzeigen
            available_einsaetze = link_service.get_available_einsaetze_for_abb(selected_abb_id)
            
            if available_einsaetze:
                einsatz_options = {f"{e.get('name', 'Unbekannt')} - {e.get('start_datum', '')}": e.get('id') for e in available_einsaetze}
                selected_einsatz_name = st.selectbox("Einsatz auswählen", list(einsatz_options.keys()), key="abb_based_einsatz_select")
                
                if selected_einsatz_name:
                    selected_einsatz_id = einsatz_options[selected_einsatz_name]
                    
                    # Zuordnungsdetails
                    kommentar = st.text_area("Notizen (optional)", max_chars=500)
                    
                    if st.button("✅ Einsatz zuordnen", type="primary"):
                        try:
                            link_service.assign_abb_to_einsatz(
                                selected_abb_id, 
                                selected_einsatz_id, 
                                None,  # rolle wird nicht mehr verwendet
                                kommentar if kommentar else None
                            )
                            st.success("✅ Einsatz erfolgreich zugeordnet!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Fehler beim Zuordnen: {str(e)}")
            else:
                st.info("Alle verfügbaren Einsätze sind bereits diesem ABB zugeordnet.")

def zuordnungs_uebersicht(link_service: LinkService, abb_service: ABBService, einsatz_service: EinsatzService):
    """Übersicht aller Zuordnungen"""
    
    st.subheader("📊 Zuordnungsübersicht")
    
    # Statistiken
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_abbs, _ = abb_service.get_all()
        st.metric("Gesamt ABB", len(total_abbs))
    
    with col2:
        total_einsaetze, _ = einsatz_service.get_all()
        st.metric("Gesamt Einsätze", len(total_einsaetze))
    
    with col3:
        total_links, _ = link_service.get_all_links()
        st.metric("Gesamt Zuordnungen", len(total_links))
    
    # Alle Zuordnungen anzeigen
    st.markdown("### Alle Zuordnungen")
    
    try:
        links, total = link_service.get_all_links()
        
        if not links:
            st.info("Keine Zuordnungen vorhanden.")
            return
        
        # Daten für DataFrame vorbereiten
        data = []
        for link in links:
            abb = abb_service.get_by_id(link.get('abb_id'))
            einsatz = einsatz_service.get_by_id(link.get('einsatz_id'))
            
            if abb and einsatz:
                data.append({
                    'ID': link.get('id', ''),
                    'ABB': f"{abb.get('vorname', '')} {abb.get('nachname', '')}",
                    'Beruf': abb.get('beruf', ''),
                    'Bereich': abb.get('bereich', ''),
                    'Einsatz': f"{einsatz.get('name', '')} - {einsatz.get('start_datum', '')}",
                    'Name': einsatz.get('name', ''),
                    'Datum': einsatz.get('start_datum', '') if einsatz.get('start_datum') else '-',
                    'Notizen': link.get('notizen', '')
                })
        
        df = pd.DataFrame(data)
        
        # DataFrame anzeigen
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )
        
        st.markdown(f"**Gesamt: {total} Zuordnungen**")
        
    except Exception as e:
        st.error(f"❌ Fehler beim Laden der Zuordnungen: {str(e)}")
    
    # CSV-Export
    st.markdown("### Export")
    
    if st.button("📥 Alle Zuordnungen als CSV exportieren"):
        try:
            links, _ = link_service.get_all_links()
            csv_service = CSVService()
            csv_data = csv_service.export_abb_einsatz_to_csv(links)
            
            st.download_button(
                label="📥 CSV herunterladen",
                data=csv_data,
                file_name=f"zuordnungen_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
            
            st.success("✅ CSV-Export bereit!")
            
        except Exception as e:
            st.error(f"❌ Fehler beim CSV-Export: {str(e)}")

if __name__ == "__main__":
    zuordnungen_page()
