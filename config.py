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
DEBUG = os.getenv("DEBUG", "True").lower() == "true"
PAGE_SIZE = int(os.getenv("PAGE_SIZE", "25"))
MAX_STUDENTS_PER_EINSATZ = int(os.getenv("MAX_STUDENTS_PER_EINSATZ", "25"))

# Pfade
DATA_DIR = Path(os.getenv("DATA_DIR", BASE_DIR / "data"))
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", BASE_DIR / "uploads"))
EXPORT_DIR = Path(os.getenv("EXPORT_DIR", BASE_DIR / "exports"))

# Verzeichnisse erstellen, falls sie nicht existieren
DATA_DIR.mkdir(exist_ok=True)
UPLOAD_DIR.mkdir(exist_ok=True)
EXPORT_DIR.mkdir(exist_ok=True)
