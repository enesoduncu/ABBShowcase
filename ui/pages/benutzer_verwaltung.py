import streamlit as st
from auth import AuthManager

def benutzer_verwaltung_page():
    """Seite für die Benutzerverwaltung"""
    
    # Überprüfen, ob der Benutzer Admin-Rechte hat
    if not st.session_state.user or st.session_state.user.get('role') != 'admin':
        st.error("❌ Sie haben keine Berechtigung, auf diese Seite zuzugreifen!")
        st.info("Nur Administratoren können die Benutzerverwaltung nutzen.")
        return
    
    st.header("👥 Benutzerverwaltung")
    st.markdown("Verwalten Sie Benutzer und deren Berechtigungen.")
    
    # AuthManager initialisieren
    auth_manager = AuthManager()
    
    # Tabs für verschiedene Funktionen
    tab1, tab2, tab3 = st.tabs(["👤 Neuen Benutzer hinzufügen", "📋 Alle Benutzer anzeigen", "🔐 Passwort ändern"])
    
    with tab1:
        st.subheader("Neuen Benutzer hinzufügen")
        
        with st.form("add_user_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                username = st.text_input("Benutzername *", placeholder="z.B. max.mustermann")
                name = st.text_input("Vollständiger Name *", placeholder="Max Mustermann")
                email = st.text_input("E-Mail", placeholder="max.mustermann@firma.de")
            
            with col2:
                password = st.text_input("Passwort *", type="password", placeholder="Sicheres Passwort")
                password_confirm = st.text_input("Passwort bestätigen *", type="password", placeholder="Passwort wiederholen")
                role = st.selectbox("Rolle *", ["user", "admin"], help="Admin hat alle Rechte, User hat eingeschränkte Rechte")
            
            # Validierung
            if st.form_submit_button("Benutzer hinzufügen", type="primary"):
                if not all([username, name, password, password_confirm]):
                    st.error("Bitte füllen Sie alle Pflichtfelder aus!")
                elif password != password_confirm:
                    st.error("Die Passwörter stimmen nicht überein!")
                elif len(password) < 6:
                    st.error("Das Passwort muss mindestens 6 Zeichen lang sein!")
                else:
                    if auth_manager.add_user(username, name, password, role, email):
                        st.success(f"✅ Benutzer '{username}' wurde erfolgreich hinzugefügt!")
                        st.balloons()
                    else:
                        st.error(f"❌ Benutzer '{username}' existiert bereits!")
    
    with tab2:
        st.subheader("Alle Benutzer")
        
        users = auth_manager.get_all_users()
        
        if users:
            # Benutzer in einer Tabelle anzeigen
            user_data = []
            for username, user_info in users.items():
                user_data.append({
                    "Benutzername": username,
                    "Name": user_info.get('name', ''),
                    "E-Mail": user_info.get('email', ''),
                    "Rolle": user_info.get('role', ''),
                    "Status": "🟢 Aktiv"
                })
            
            if user_data:
                st.dataframe(user_data, use_container_width=True)
            else:
                st.info("Keine Benutzer gefunden.")
        else:
            st.info("Keine Benutzer verfügbar.")
    
    with tab3:
        st.subheader("Passwort ändern")
        
        with st.form("change_password_form"):
            username = st.selectbox(
                "Benutzer auswählen",
                [user['username'] for user in auth_manager.get_all_users().values()],
                help="Wählen Sie den Benutzer aus, dessen Passwort Sie ändern möchten"
            )
            
            new_password = st.text_input("Neues Passwort *", type="password", placeholder="Neues sicheres Passwort")
            new_password_confirm = st.text_input("Neues Passwort bestätigen *", type="password", placeholder="Passwort wiederholen")
            
            if st.form_submit_button("Passwort ändern", type="primary"):
                if not all([username, new_password, new_password_confirm]):
                    st.error("Bitte füllen Sie alle Felder aus!")
                elif new_password != new_password_confirm:
                    st.error("Die Passwörter stimmen nicht überein!")
                elif len(new_password) < 6:
                    st.error("Das Passwort muss mindestens 6 Zeichen lang sein!")
                else:
                    if auth_manager.change_password(username, new_password):
                        st.success(f"✅ Passwort für Benutzer '{username}' wurde erfolgreich geändert!")
                    else:
                        st.error(f"❌ Fehler beim Ändern des Passworts für Benutzer '{username}'!")
    
    # Wichtige Hinweise
    st.markdown("---")
    st.markdown("### 📋 Wichtige Hinweise")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("""
        **🔐 Passwort-Richtlinien:**
        - Mindestens 6 Zeichen
        - Kombination aus Buchstaben, Zahlen und Sonderzeichen empfohlen
        - Regelmäßig ändern
        """)
    
    with col2:
        st.warning("""
        **⚠️ Sicherheitshinweise:**
        - Geben Sie niemals Passwörter weiter
        - Verwenden Sie sichere Passwörter
        - Melden Sie sich nach der Arbeit ab
        """)
