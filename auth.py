import streamlit as st
import bcrypt
import json
import os
import hashlib
import time
from pathlib import Path
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta
import secrets

class SecurityConfig:
    """Sicherheitskonfiguration"""
    # Passwort-Anforderungen
    MIN_PASSWORD_LENGTH = 12
    REQUIRE_UPPERCASE = True
    REQUIRE_LOWERCASE = True
    REQUIRE_DIGITS = True
    REQUIRE_SPECIAL_CHARS = True
    SPECIAL_CHARS = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    
    # Session-Sicherheit
    SESSION_TIMEOUT_HOURS = 8
    
    # Passwort-Änderungspflicht
    FORCE_PASSWORD_CHANGE_DAYS = 90
    FORCE_PASSWORD_CHANGE_ON_FIRST_LOGIN = True

class AuthManager:
    """Verwaltet die Authentifizierung der Anwendung mit erweiterten Sicherheitsfeatures"""
    
    def __init__(self):
        self.users_file = Path("data/users.json")
        self.security_log_file = Path("data/security.log")
        self.users_file.parent.mkdir(exist_ok=True)
        self._load_users()
        self._load_security_log()
    
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
    
    def _load_security_log(self):
        """Lädt das Sicherheitslog"""
        if self.security_log_file.exists():
            try:
                with open(self.security_log_file, 'r', encoding='utf-8') as f:
                    self.security_log = json.load(f)
            except Exception:
                self.security_log = {"login_attempts": {}, "password_changes": {}}
        else:
            self.security_log = {"login_attempts": {}, "password_changes": {}}
            self._save_security_log()
    
    def _save_security_log(self):
        """Speichert das Sicherheitslog"""
        try:
            with open(self.security_log_file, 'w', encoding='utf-8') as f:
                json.dump(self.security_log, f, indent=2, ensure_ascii=False)
        except Exception as e:
            st.error(f"Fehler beim Speichern des Sicherheitslogs: {e}")
    
    def _get_default_users(self) -> Dict:
        """Erstellt Standard-Benutzer mit erweiterten Sicherheitsinformationen"""
        # Festes Passwort für einfachere Nutzung
        default_password = "admin123"
        hashed_password = bcrypt.hashpw(default_password.encode('utf-8'), bcrypt.gensalt())
        
        return {
            "admin": {
                "username": "admin",
                "name": "Administrator",
                "password": hashed_password.decode('utf-8'),
                "role": "admin",
                "email": "admin@abb-streamlit.de",
                "created_at": datetime.now().isoformat(),
                "last_password_change": datetime.now().isoformat(),
                "password_expires_at": (datetime.now() + timedelta(days=SecurityConfig.FORCE_PASSWORD_CHANGE_DAYS)).isoformat(),
                "force_password_change": True,
                "last_login": None,
                "session_token": None
            }
        }
    
    def _generate_secure_password(self) -> str:
        """Generiert ein sicheres Standard-Passwort"""
        # Mindestens 16 Zeichen mit allen Anforderungen
        password = (
            secrets.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ") +  # Großbuchstabe
            secrets.choice("abcdefghijklmnopqrstuvwxyz") +  # Kleinbuchstabe
            secrets.choice("0123456789") +                   # Ziffer
            secrets.choice(SecurityConfig.SPECIAL_CHARS) +   # Sonderzeichen
            ''.join(secrets.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*") 
                   for _ in range(12))                      # Zusätzliche zufällige Zeichen
        )
        # Mischen der Zeichen
        password_list = list(password)
        secrets.SystemRandom().shuffle(password_list)
        return ''.join(password_list)
    
    def _validate_password_strength(self, password: str) -> Tuple[bool, str]:
        """Überprüft die Passwort-Stärke"""
        if len(password) < SecurityConfig.MIN_PASSWORD_LENGTH:
            return False, f"Passwort muss mindestens {SecurityConfig.MIN_PASSWORD_LENGTH} Zeichen lang sein"
        
        if SecurityConfig.REQUIRE_UPPERCASE and not any(c.isupper() for c in password):
            return False, "Passwort muss mindestens einen Großbuchstaben enthalten"
        
        if SecurityConfig.REQUIRE_LOWERCASE and not any(c.islower() for c in password):
            return False, "Passwort muss mindestens einen Kleinbuchstaben enthalten"
        
        if SecurityConfig.REQUIRE_DIGITS and not any(c.isdigit() for c in password):
            return False, "Passwort muss mindestens eine Ziffer enthalten"
        
        if SecurityConfig.REQUIRE_SPECIAL_CHARS and not any(c in SecurityConfig.SPECIAL_CHARS for c in password):
            return False, f"Passwort muss mindestens ein Sonderzeichen enthalten: {SecurityConfig.SPECIAL_CHARS}"
        
        # Überprüfung auf schwache Passwörter
        weak_passwords = ["password", "123456", "admin", "qwerty", "letmein", "welcome"]
        if password.lower() in weak_passwords:
            return False, "Dieses Passwort ist zu schwach und wird nicht akzeptiert"
        
        return True, "Passwort erfüllt alle Sicherheitsanforderungen"
    
    
    def _record_login_attempt(self, username: str, success: bool):
        """Zeichnet Login-Versuche auf"""
        if username not in self.users:
            return
        
        user = self.users[username]
        if success:
            user['last_login'] = datetime.now().isoformat()
            user['session_token'] = self._generate_session_token()
            self._save_users()
    
    def _generate_session_token(self) -> str:
        """Generiert einen sicheren Session-Token"""
        return secrets.token_urlsafe(32)
    
    def _check_password_expiry(self, username: str) -> Tuple[bool, Optional[str]]:
        """Überprüft, ob ein Passwort abgelaufen ist"""
        if username in self.users:
            user = self.users[username]
            
            # Erste Anmeldung - Passwort-Änderung erforderlich
            if user.get('force_password_change'):
                return True, "Sie müssen Ihr Passwort bei der ersten Anmeldung ändern"
            
            # Passwort abgelaufen
            if user.get('password_expires_at'):
                expiry_date = datetime.fromisoformat(user['password_expires_at'])
                if datetime.now() > expiry_date:
                    return True, f"Ihr Passwort ist seit {(datetime.now() - expiry_date).days} Tagen abgelaufen"
                
                # Warnung 7 Tage vor Ablauf
                warning_date = expiry_date - timedelta(days=7)
                if datetime.now() > warning_date:
                    days_left = (expiry_date - datetime.now()).days
                    return False, f"Warnung: Ihr Passwort läuft in {days_left} Tagen ab"
        
        return False, None
    
    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Überprüft ein Passwort gegen den Hash"""
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
        except Exception:
            return False
    
    def authenticate(self, username: str, password: str) -> Tuple[Optional[Dict], str]:
        """Authentifiziert einen Benutzer mit erweiterten Sicherheitsprüfungen"""
        # Überprüfung auf Benutzer-Existenz
        if username not in self.users:
            return None, "Ungültiger Benutzername oder Passwort"
        
        user = self.users[username]
        
        # Passwort überprüfen
        if self.verify_password(password, user['password']):
            # Erfolgreiche Anmeldung
            self._record_login_attempt(username, True)
            
            # Passwort-Änderung erforderlich?
            password_change_required, message = self._check_password_expiry(username)
            if password_change_required:
                user['force_password_change'] = True
                self._save_users()
                return user, f"Anmeldung erfolgreich, aber {message}"
            
            return user, "Anmeldung erfolgreich"
        else:
            # Fehlgeschlagene Anmeldung
            self._record_login_attempt(username, False)
            return None, "Ungültiger Benutzername oder Passwort"
    
    def add_user(self, username: str, name: str, password: str, role: str = "user", email: str = "") -> Tuple[bool, str]:
        """Fügt einen neuen Benutzer hinzu mit Passwort-Validierung"""
        if username in self.users:
            return False, "Benutzername existiert bereits"
        
        # Passwort-Stärke überprüfen
        is_valid, message = self._validate_password_strength(password)
        if not is_valid:
            return False, message
        
        # Passwort hashen
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        # Benutzer erstellen
        self.users[username] = {
            "username": username,
            "name": name,
            "password": hashed_password.decode('utf-8'),
            "role": role,
            "email": email,
            "created_at": datetime.now().isoformat(),
            "last_password_change": datetime.now().isoformat(),
            "password_expires_at": (datetime.now() + timedelta(days=SecurityConfig.FORCE_PASSWORD_CHANGE_DAYS)).isoformat(),
            "force_password_change": SecurityConfig.FORCE_PASSWORD_CHANGE_ON_FIRST_LOGIN,
            "last_login": None,
            "session_token": None
        }
        
        self._save_users()
        return True, "Benutzer erfolgreich erstellt"
    
    def change_password(self, username: str, old_password: str, new_password: str) -> Tuple[bool, str]:
        """Ändert das Passwort eines Benutzers mit Validierung"""
        if username not in self.users:
            return False, "Benutzer nicht gefunden"
        
        user = self.users[username]
        
        # Altes Passwort überprüfen
        if not self.verify_password(old_password, user['password']):
            return False, "Aktuelles Passwort ist falsch"
        
        # Neues Passwort darf nicht dem alten entsprechen
        if old_password == new_password:
            return False, "Neues Passwort muss sich vom aktuellen unterscheiden"
        
        # Passwort-Stärke überprüfen
        is_valid, message = self._validate_password_strength(new_password)
        if not is_valid:
            return False, message
        
        # Passwort hashen und speichern
        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
        user['password'] = hashed_password.decode('utf-8')
        user['last_password_change'] = datetime.now().isoformat()
        user['password_expires_at'] = (datetime.now() + timedelta(days=SecurityConfig.FORCE_PASSWORD_CHANGE_DAYS)).isoformat()
        user['force_password_change'] = False
        
        # Sicherheitslog aktualisieren
        if username not in self.security_log['password_changes']:
            self.security_log['password_changes'][username] = []
        
        self.security_log['password_changes'][username].append({
            'timestamp': datetime.now().isoformat(),
            'ip_address': 'unknown'  # Könnte später erweitert werden
        })
        
        self._save_users()
        self._save_security_log()
        
        return True, "Passwort erfolgreich geändert"
    
    def get_all_users(self) -> Dict:
        """Gibt alle Benutzer zurück (ohne sensible Daten)"""
        return {username: {k: v for k, v in user.items() 
                          if k not in ['password', 'session_token']} 
                for username, user in self.users.items()}
    
    def get_user_security_status(self, username: str) -> Dict:
        """Gibt den Sicherheitsstatus eines Benutzers zurück"""
        if username not in self.users:
            return {}
        
        user = self.users[username]
        return {
            'username': username,
            'force_password_change': user.get('force_password_change', False),
            'password_expires_at': user.get('password_expires_at'),
            'last_password_change': user.get('last_password_change'),
            'last_login': user.get('last_login')
        }

def check_authentication():
    """Überprüft, ob der Benutzer angemeldet ist und Session gültig ist"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    if 'user' not in st.session_state:
        st.session_state.user = None
    
    if 'login_time' not in st.session_state:
        st.session_state.login_time = None
    
    # Session-Timeout überprüfen
    if st.session_state.authenticated and st.session_state.login_time:
        login_time = datetime.fromisoformat(st.session_state.login_time)
        if datetime.now() - login_time > timedelta(hours=SecurityConfig.SESSION_TIMEOUT_HOURS):
            # Session abgelaufen
            logout()
            return False
    
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
                user, message = auth_manager.authenticate(username, password)
                if user:
                    st.session_state.authenticated = True
                    st.session_state.user = user
                    st.session_state.login_time = datetime.now().isoformat()
                    
                    if user.get('force_password_change'):
                        st.warning("⚠️ Sie müssen Ihr Passwort ändern, bevor Sie fortfahren können.")
                        st.session_state.show_password_change = True
                    else:
                        st.success(f"Willkommen, {user['name']}! Sie werden weitergeleitet...")
                    
                    st.rerun()
                else:
                    st.error(message)
            else:
                st.warning("Bitte füllen Sie alle Felder aus!")
    
    # Hilfetext
    st.markdown("---")
    st.info("**🔐 Standard-Anmeldedaten:** Benutzername: `admin`, Passwort: `admin123`")
    st.info("**🔒 Sicherheitsfeatures:** Passwort-Änderungspflicht, Session-Timeout")

def logout():
    """Meldet den Benutzer ab"""
    st.session_state.authenticated = False
    st.session_state.user = None
    st.session_state.login_time = None
    st.session_state.show_password_change = False
    st.rerun()

def show_user_info():
    """Zeigt Benutzerinformationen in der Sidebar an"""
    if st.session_state.user:
        st.markdown("---")
        st.markdown(f"**👤 Angemeldet als:** {st.session_state.user['name']}")
        st.markdown(f"**🔑 Rolle:** {st.session_state.user['role']}")
        
        # Sicherheitsstatus anzeigen
        if st.session_state.user.get('force_password_change'):
            st.error("⚠️ Passwort-Änderung erforderlich!")
        
        # Session-Info
        if st.session_state.login_time:
            login_time = datetime.fromisoformat(st.session_state.login_time)
            remaining_time = timedelta(hours=SecurityConfig.SESSION_TIMEOUT_HOURS) - (datetime.now() - login_time)
            if remaining_time.total_seconds() > 0:
                st.info(f"⏰ Session läuft in {remaining_time.seconds // 3600}h {(remaining_time.seconds % 3600) // 60}m ab")
        
        if st.button("🚪 Abmelden", use_container_width=True):
            logout()

def force_password_change_page(auth_manager: AuthManager):
    """Seite für erzwungene Passwort-Änderung"""
    st.markdown('<h1 class="main-header">🔐 Passwort ändern erforderlich</h1>', unsafe_allow_html=True)
    st.warning("⚠️ Sie müssen Ihr Passwort ändern, bevor Sie die Anwendung nutzen können.")
    
    with st.form("force_password_change_form"):
        current_password = st.text_input("Aktuelles Passwort", type="password", placeholder="Ihr aktuelles Passwort")
        new_password = st.text_input("Neues Passwort", type="password", placeholder="Neues sicheres Passwort")
        confirm_password = st.text_input("Neues Passwort bestätigen", type="password", placeholder="Passwort wiederholen")
        
        if st.form_submit_button("Passwort ändern", type="primary"):
            if not all([current_password, new_password, confirm_password]):
                st.error("Bitte füllen Sie alle Felder aus!")
            elif new_password != confirm_password:
                st.error("Die neuen Passwörter stimmen nicht überein!")
            else:
                success, message = auth_manager.change_password(
                    st.session_state.user['username'], 
                    current_password, 
                    new_password
                )
                if success:
                    st.success("✅ Passwort erfolgreich geändert! Sie werden weitergeleitet...")
                    st.session_state.show_password_change = False
                    st.rerun()
                else:
                    st.error(f"❌ {message}")
    
    # Passwort-Anforderungen anzeigen
    st.markdown("---")
    st.markdown("### 🔐 Passwort-Anforderungen")
    st.markdown(f"- Mindestens {SecurityConfig.MIN_PASSWORD_LENGTH} Zeichen")
    st.markdown("- Mindestens ein Großbuchstabe")
    st.markdown("- Mindestens ein Kleinbuchstabe")
    st.markdown("- Mindestens eine Ziffer")
    st.markdown(f"- Mindestens ein Sonderzeichen: {SecurityConfig.SPECIAL_CHARS}")
    st.markdown("- Darf nicht dem aktuellen Passwort entsprechen")
