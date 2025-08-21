import streamlit as st
import bcrypt
import json
import os
from pathlib import Path
from typing import Dict, Optional

class AuthManager:
    """Verwaltet die Authentifizierung der Anwendung"""
    
    def __init__(self):
        self.users_file = Path("data/users.json")
        self.users_file.parent.mkdir(exist_ok=True)
        self._load_users()
    
    def _load_users(self):
        """Lädt Benutzer aus der JSON-Datei"""
        if self.users_file.exists():
            try:
                with open(self.users_file, 'r', encoding='utf-8') as f:
                    self.users = json.load(f)
            except Exception as e:
                st.error(f"Fehler beim Laden der Benutzer: {e}")
                self.users = self._get_default_users()
        else:
            self.users = self._get_default_users()
            self._save_users()
    
    def _save_users(self):
        """Speichert Benutzer in der JSON-Datei"""
        try:
            with open(self.users_file, 'w', encoding='utf-8') as f:
                json.dump(self.users, f, indent=2, ensure_ascii=False)
        except Exception as e:
            st.error(f"Fehler beim Speichern der Benutzer: {e}")
    
    def _get_default_users(self) -> Dict:
        """Erstellt Standard-Benutzer"""
        default_password = "admin123"  # Standard-Passwort
        hashed_password = bcrypt.hashpw(default_password.encode('utf-8'), bcrypt.gensalt())
        
        return {
            "admin": {
                "username": "admin",
                "name": "Administrator",
                "password": hashed_password.decode('utf-8'),
                "role": "admin",
                "email": "admin@abb-streamlit.de"
            }
        }
    
    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Überprüft ein Passwort gegen den Hash"""
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
        except Exception:
            return False
    
    def authenticate(self, username: str, password: str) -> Optional[Dict]:
        """Authentifiziert einen Benutzer"""
        if username in self.users:
            user = self.users[username]
            if self.verify_password(password, user['password']):
                return user
        return None
    
    def add_user(self, username: str, name: str, password: str, role: str = "user", email: str = "") -> bool:
        """Fügt einen neuen Benutzer hinzu"""
        if username in self.users:
            return False
        
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        self.users[username] = {
            "username": username,
            "name": name,
            "password": hashed_password.decode('utf-8'),
            "role": role,
            "email": email
        }
        
        self._save_users()
        return True
    
    def change_password(self, username: str, new_password: str) -> bool:
        """Ändert das Passwort eines Benutzers"""
        if username in self.users:
            hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
            self.users[username]['password'] = hashed_password.decode('utf-8')
            self._save_users()
            return True
        return False
    
    def get_all_users(self) -> Dict:
        """Gibt alle Benutzer zurück (ohne Passwörter)"""
        return {username: {k: v for k, v in user.items() if k != 'password'} 
                for username, user in self.users.items()}

def check_authentication():
    """Überprüft, ob der Benutzer angemeldet ist"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    if 'user' not in st.session_state:
        st.session_state.user = None
    
    return st.session_state.authenticated

def login_page(auth_manager: AuthManager):
    """Zeigt die Login-Seite an"""
    st.markdown('<h1 class="main-header">🔐 Anmeldung</h1>', unsafe_allow_html=True)
    st.markdown('<h2 style="text-align: center; color: #666;">ABB Streamlit - Ausbildungsbotschafter Verwaltung</h2>', unsafe_allow_html=True)
    
    # Login-Formular
    with st.form("login_form"):
        username = st.text_input("Benutzername", placeholder="Ihr Benutzername")
        password = st.text_input("Passwort", type="password", placeholder="Ihr Passwort")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            submit_button = st.form_submit_button("Anmelden", type="primary", use_container_width=True)
        
        if submit_button:
            if username and password:
                user = auth_manager.authenticate(username, password)
                if user:
                    st.session_state.authenticated = True
                    st.session_state.user = user
                    st.success(f"Willkommen, {user['name']}! Sie werden weitergeleitet...")
                    st.rerun()
                else:
                    st.error("Ungültiger Benutzername oder Passwort!")
            else:
                st.warning("Bitte füllen Sie alle Felder aus!")
    
    # Hilfetext
    st.markdown("---")
    st.info("**Standard-Anmeldedaten:** Benutzername: `admin`, Passwort: `admin123`")
    st.warning("⚠️ **Wichtig:** Ändern Sie das Standard-Passwort nach der ersten Anmeldung!")

def logout():
    """Meldet den Benutzer ab"""
    st.session_state.authenticated = False
    st.session_state.user = None
    st.rerun()

def show_user_info():
    """Zeigt Benutzerinformationen in der Sidebar an"""
    if st.session_state.user:
        st.markdown("---")
        st.markdown(f"**👤 Angemeldet als:** {st.session_state.user['name']}")
        st.markdown(f"**🔑 Rolle:** {st.session_state.user['role']}")
        
        if st.button("🚪 Abmelden", use_container_width=True):
            logout()
