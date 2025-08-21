# ABB Streamlit - Ausbildungsbotschafter Verwaltung

Eine Streamlit-basierte Web-Applikation zur Verwaltung von Ausbildungsbotschaftern (ABB), Schuleinsätzen/Terminen sowie der Teilnehmer-Verknüpfung.

## Features

- **🔐 Authentifizierung**: Sichere Anmeldung mit Benutzerverwaltung
- **ABB-Verwaltung**: Vollständige CRUD-Operationen für Ausbildungsbotschafter
- **Einsatz-Verwaltung**: Schuleinsätze mit automatischer 25er-Gruppen-Aufteilung
- **Zuordnungen**: Verknüpfung von ABB mit Einsätzen
- **Dashboard**: Kennzahlen und Visualisierungen
- **Import/Export**: CSV-Import und -Export für alle Tabellen
- **Berichte**: Verschiedene Auswertungen und Exportmöglichkeiten
- **Benutzerverwaltung**: Benutzer anlegen und verwalten (nur für Admins)

## Installation

1. **Repository klonen oder herunterladen**
2. **Python 3.11+ installieren**
3. **Abhängigkeiten installieren:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Datenbank initialisieren (optional - wird automatisch erstellt):**
   ```bash
   python seed_data.py
   ```
5. **App starten:**
   ```bash
   streamlit run app.py
   ```

## Schnellstart

```bash
# Abhängigkeiten installieren
pip install -r requirements.txt

# Beispieldaten laden (optional)
python seed_data.py

# Anwendung starten
streamlit run app.py
```

## 🔐 Authentifizierung

Die Anwendung verfügt über ein sicheres Authentifizierungssystem:

### Standard-Anmeldedaten
- **Benutzername**: `admin`
- **Passwort**: `admin123`

### Wichtige Sicherheitshinweise
⚠️ **Ändern Sie das Standard-Passwort nach der ersten Anmeldung!**

### Benutzerrollen
- **Admin**: Vollzugriff auf alle Funktionen inklusive Benutzerverwaltung
- **User**: Zugriff auf alle Anwendungsfunktionen (außer Benutzerverwaltung)

### Neue Benutzer hinzufügen
1. Melden Sie sich als Administrator an
2. Navigieren Sie zu "👥 Benutzerverwaltung"
3. Fügen Sie neue Benutzer hinzu oder ändern Sie Passwörter

## Projektstruktur

```
ABBStreamlit/
├── app.py                 # Hauptanwendung
├── auth.py               # Authentifizierung
├── requirements.txt       # Python-Abhängigkeiten
├── .env                  # Umgebungsvariablen
├── alembic.ini          # Alembic-Konfiguration
├── data/                 # Datenbankdateien
├── models/               # SQLAlchemy-Models
├── services/             # Geschäftslogik
├── ui/                   # UI-Komponenten
│   └── pages/           # Streamlit-Seiten
│       ├── abb_verwaltung.py
│       ├── einsatz_verwaltung.py
│       ├── zuordnungen.py
│       ├── berichte.py
│       ├── einstellungen.py
│       └── benutzer_verwaltung.py
├── schemas/              # Pydantic-Schemas
├── utils/                # Hilfsfunktionen
└── tests/                # Tests
```

## Datenmodell

### Ausbildungsbotschafter (ABB)
- Persönliche Daten, Kontaktinformationen
- Berufliche Informationen und Ausbildung
- Bereich (IHK, HWK, sonstiges)

### Einsätze
- Schuleinsätze mit maximal 25 Schülern pro Eintrag
- Automatische Aufteilung bei größeren Gruppen
- Schul- und Termininformationen

### Zuordnungen
- Many-to-Many-Beziehung zwischen ABB und Einsätzen
- Rollen und Kommentare möglich

## Geschäftsregeln

- **Max 25 Regel**: Einsätze werden automatisch in Gruppen von maximal 25 Schülern aufgeteilt
- **Dubletten-Schutz**: Optionaler Check für ABB-Duplikate
- **Validierung**: Umfassende Eingabevalidierung mit Pydantic

## Verwendung

1. **🔐 Anmeldung**: Sichere Anmeldung mit Benutzername und Passwort
2. **Dashboard**: Übersicht über Kennzahlen und Statistiken
3. **ABB verwalten**: Ausbildungsbotschafter anlegen, bearbeiten und verwalten
4. **Einsätze verwalten**: Schuleinsätze planen und organisieren
5. **Zuordnungen**: ABB zu Einsätzen zuordnen
6. **Berichte**: Verschiedene Auswertungen und Exporte
7. **Einstellungen**: Konfiguration und Backup-Funktionen
8. **Benutzerverwaltung**: Benutzer anlegen und verwalten (nur für Admins)

## Technische Details

- **Backend**: SQLite mit SQLAlchemy ORM
- **Frontend**: Streamlit
- **Authentifizierung**: bcrypt für sichere Passwort-Hashing
- **Validierung**: Pydantic-Schemas
- **Migrationen**: Alembic
- **Tests**: Unit-Tests für Services
- **Smoke-Tests ausführen:**
  ```bash
  python test_smoke.py
  ```

## Support

Bei Fragen oder Problemen wenden Sie sich an das Entwicklungsteam.
