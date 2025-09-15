import os
from pathlib import Path
from dotenv import load_dotenv

# .env-Datei laden
load_dotenv()

# Basis-Verzeichnis
BASE_DIR = Path(__file__).parent

# Datenbank-Konfiguration
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR}/data/abb_streamlit.db")

# CSV-Konfiguration
CSV_DELIMITER = os.getenv("CSV_DELIMITER", ";")
CSV_ENCODING = os.getenv("CSV_ENCODING", "utf-8")

# Anwendungseinstellungen
DEBUG = os.getenv("DEBUG", "False").lower() == "true"  # Standardmäßig auf False für Produktion
PAGE_SIZE = int(os.getenv("PAGE_SIZE", "25"))
MAX_STUDENTS_PER_EINSATZ = int(os.getenv("MAX_STUDENTS_PER_EINSATZ", "25"))

# Sicherheitseinstellungen
SECURITY_ENABLED = os.getenv("SECURITY_ENABLED", "True").lower() == "true"
MIN_PASSWORD_LENGTH = int(os.getenv("MIN_PASSWORD_LENGTH", "12"))
SESSION_TIMEOUT_HOURS = int(os.getenv("SESSION_TIMEOUT_HOURS", "8"))
MAX_LOGIN_ATTEMPTS = int(os.getenv("MAX_LOGIN_ATTEMPTS", "5"))
LOCKOUT_DURATION_MINUTES = int(os.getenv("LOCKOUT_DURATION_MINUTES", "30"))
FORCE_PASSWORD_CHANGE_DAYS = int(os.getenv("FORCE_PASSWORD_CHANGE_DAYS", "90"))
REQUIRE_STRONG_PASSWORDS = os.getenv("REQUIRE_STRONG_PASSWORDS", "True").lower() == "true"

# Logging und Überwachung
ENABLE_SECURITY_LOGGING = os.getenv("ENABLE_SECURITY_LOGGING", "True").lower() == "true"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", f"{BASE_DIR}/logs/app.log")

# HTTPS und SSL (für Produktionsumgebung)
ENABLE_HTTPS = os.getenv("ENABLE_HTTPS", "False").lower() == "true"
SSL_CERT_FILE = os.getenv("SSL_CERT_FILE", "")
SSL_KEY_FILE = os.getenv("SSL_KEY_FILE", "")

# Pfade
DATA_DIR = Path(os.getenv("DATA_DIR", BASE_DIR / "data"))
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", BASE_DIR / "uploads"))
EXPORT_DIR = Path(os.getenv("EXPORT_DIR", BASE_DIR / "exports"))
LOGS_DIR = Path(os.getenv("LOGS_DIR", BASE_DIR / "logs"))

# Verzeichnisse erstellen, falls sie nicht existieren
DATA_DIR.mkdir(exist_ok=True)
UPLOAD_DIR.mkdir(exist_ok=True)
EXPORT_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# Sicherheitswarnungen
if DEBUG:
    print("⚠️  WARNUNG: Debug-Modus ist aktiviert. Deaktivieren Sie ihn in der Produktionsumgebung!")
    print("⚠️  Setzen Sie DEBUG=False in Ihrer .env-Datei")

if not SECURITY_ENABLED:
    print("🚨 WARNUNG: Sicherheitsfeatures sind deaktiviert!")
    print("🚨 Setzen Sie SECURITY_ENABLED=True in Ihrer .env-Datei")

# Produktionssicherheitsprüfungen
if not DEBUG and not ENABLE_HTTPS:
    print("⚠️  WARNUNG: HTTPS ist in der Produktionsumgebung deaktiviert!")
    print("⚠️  Aktivieren Sie HTTPS für sichere Verbindungen")
