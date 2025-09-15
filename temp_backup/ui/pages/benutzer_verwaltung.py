import streamlit as st
from auth import AuthManager, SecurityConfig

def benutzer_verwaltung_page():
    """Seite für die Benutzerverwaltung"""
    
    # Überprüfen, ob der Benutzer Admin-Rechte hat
    if not st.session_state.user or st.session_state.user.get('role') != 'admin':
        st.error("❌ Sie haben keine Berechtigung, auf diese Seite zuzugreifen!")
        st.info("Nur Administratoren können die Benutzerverwaltung nutzen.")
        return
    
    st.header("👥 Benutzerverwaltung")
    st.markdown("Verwalten Sie Benutzer und deren Berechtigungen mit erweiterten Sicherheitsfeatures.")
    
    # AuthManager initialisieren
    auth_manager = AuthManager()
    
    # Tabs für verschiedene Funktionen
    tab1, tab2, tab3, tab4 = st.tabs(["👤 Neuen Benutzer hinzufügen", "📋 Alle Benutzer anzeigen", "🔐 Passwort ändern", "🔒 Sicherheitsstatus"])
    
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
                else:
                    success, message = auth_manager.add_user(username, name, password, role, email)
                    if success:
                        st.success(f"✅ {message}")
                        st.balloons()
                    else:
                        st.error(f"❌ {message}")
    
    with tab2:
        st.subheader("Alle Benutzer")
        
        users = auth_manager.get_all_users()
        
        if users:
            # Benutzer in einer Tabelle anzeigen
            user_data = []
            for username, user_info in users.items():
                # Sicherheitsstatus bestimmen
                security_status = "🟢 Aktiv"
                if user_info.get('force_password_change'):
                    security_status = "⚠️ Passwort-Änderung erforderlich"
                elif user_info.get('locked_until'):
                    security_status = "🔒 Gesperrt"
                
                user_data.append({
                    "Benutzername": username,
                    "Name": user_info.get('name', ''),
                    "E-Mail": user_info.get('email', ''),
                    "Rolle": user_info.get('role', ''),
                    "Status": security_status,
                    "Erstellt": user_info.get('created_at', '')[:10] if user_info.get('created_at') else '',
                    "Letzter Login": user_info.get('last_login', '')[:10] if user_info.get('last_login') else ''
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
            
            current_password = st.text_input("Aktuelles Passwort *", type="password", placeholder="Aktuelles Passwort des Benutzers")
            new_password = st.text_input("Neues Passwort *", type="password", placeholder="Neues sicheres Passwort")
            new_password_confirm = st.text_input("Neues Passwort bestätigen *", type="password", placeholder="Passwort wiederholen")
            
            if st.form_submit_button("Passwort ändern", type="primary"):
                if not all([username, current_password, new_password, new_password_confirm]):
                    st.error("Bitte füllen Sie alle Felder aus!")
                elif new_password != new_password_confirm:
                    st.error("Die neuen Passwörter stimmen nicht überein!")
                else:
                    success, message = auth_manager.change_password(username, current_password, new_password)
                    if success:
                        st.success(f"✅ {message}")
                    else:
                        st.error(f"❌ {message}")
    
    with tab4:
        st.subheader("🔒 Sicherheitsstatus")
        
        users = auth_manager.get_all_users()
        if users:
            for username, user_info in users.items():
                with st.expander(f"Benutzer: {username} ({user_info.get('name', '')})"):
                    security_status = auth_manager.get_user_security_status(username)
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**Passwort-Status:**")
                        if security_status.get('force_password_change'):
                            st.error("⚠️ Passwort-Änderung erforderlich")
                        else:
                            st.success("✅ Passwort aktuell")
                        
                        if security_status.get('password_expires_at'):
                            expiry_date = security_status['password_expires_at'][:10]
                            st.info(f"**Läuft ab:** {expiry_date}")
                        
                        if security_status.get('last_password_change'):
                            last_change = security_status['last_password_change'][:10]
                            st.info(f"**Letzte Änderung:** {last_change}")
                    
                    with col2:
                        st.markdown("**Konto-Status:**")
                        login_attempts = security_status.get('login_attempts', 0)
                        if login_attempts > 0:
                            st.warning(f"**Fehlgeschlagene Logins:** {login_attempts}")
                        else:
                            st.success("✅ Keine fehlgeschlagenen Logins")
                        
                        if security_status.get('locked_until'):
                            st.error("🔒 Konto gesperrt")
                        
                        if security_status.get('last_login'):
                            last_login = security_status['last_login'][:10]
                            st.info(f"**Letzter Login:** {last_login}")
    
    # Wichtige Hinweise
    st.markdown("---")
    st.markdown("### 📋 Sicherheitshinweise")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info(f"""
        **🔐 Passwort-Richtlinien:**
        - Mindestens {SecurityConfig.MIN_PASSWORD_LENGTH} Zeichen
        - Mindestens ein Großbuchstabe
        - Mindestens ein Kleinbuchstabe
        - Mindestens eine Ziffer
        - Mindestens ein Sonderzeichen: {SecurityConfig.SPECIAL_CHARS}
        - Darf nicht dem aktuellen Passwort entsprechen
        - Automatische Ablaufzeit: {SecurityConfig.FORCE_PASSWORD_CHANGE_DAYS} Tage
        """)
    
    with col2:
        st.warning(f"""
        **⚠️ Sicherheitsfeatures:**
        - Session-Timeout: {SecurityConfig.SESSION_TIMEOUT_HOURS} Stunden
        - Max. Login-Versuche: {SecurityConfig.MAX_LOGIN_ATTEMPTS}
        - Konto-Sperre: {SecurityConfig.LOCKOUT_DURATION_MINUTES} Minuten
        - Passwort-Änderungspflicht bei erster Anmeldung
        - Brute-Force-Schutz
        - Sichere Passwort-Hashing mit bcrypt
        """)
