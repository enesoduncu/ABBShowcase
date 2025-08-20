#!/usr/bin/env python3
"""
Seed-Daten für ABB Streamlit
Erstellt 20 realistische Beispieldatensätze für jede Tabelle
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from database import get_db, create_tables
from models.abb import ABB, BereichEnum, GeschlechtEnum
from models.einsatz import Einsatz
from models.abb_einsatz import ABBEinsatz
from datetime import date, datetime, timedelta
import random

def create_seed_data():
    """Erstellt Beispieldaten für alle Tabellen"""
    
    print("🌱 Erstelle Seed-Daten für ABB Streamlit...")
    
    # Datenbankverbindung
    db = get_db()
    
    # Tabellen erstellen
    create_tables()
    
    # Beispieldaten für ABB
    print("👥 Erstelle ABB-Beispieldaten...")
    abbs = create_abb_seed_data(db)
    
    # Beispieldaten für Einsätze
    print("📅 Erstelle Einsatz-Beispieldaten...")
    einsaetze = create_einsatz_seed_data(db)
    
    # Beispieldaten für Zuordnungen
    print("🔗 Erstelle Zuordnungs-Beispieldaten...")
    create_zuordnungs_seed_data(db, abbs, einsaetze)
    
    print("✅ Seed-Daten erfolgreich erstellt!")
    print(f"   - {len(abbs)} ABB angelegt")
    print(f"   - {len(einsaetze)} Einsätze angelegt")
    print("   - Zuordnungen erstellt")

def create_abb_seed_data(db) -> list:
    """Erstellt ABB-Beispieldaten"""
    
    # Beispieldaten
    abb_data = [
        # IHK-Bereich
        {
            'vorname': 'Max', 'nachname': 'Mustermann', 'geschlecht': GeschlechtEnum.M,
            'geburtsdatum': date(1995, 3, 15), 'beruf': 'Industriekaufmann', 'bereich': BereichEnum.IHK,
            'ausbildungsbeginn': date(2015, 8, 1), 'ausbildungsende': date(2018, 7, 31),
            'schulungsdatum': date(2020, 5, 10), 'betrieb': 'Musterfirma GmbH', 'landkreis_betrieb': 'Stuttgart',
            'direktkontakt': True, 'aktiv': True
        },
        {
            'vorname': 'Anna', 'nachname': 'Schmidt', 'geschlecht': GeschlechtEnum.W,
            'geburtsdatum': date(1992, 7, 22), 'beruf': 'Kauffrau für Büromanagement', 'bereich': BereichEnum.IHK,
            'ausbildungsbeginn': date(2012, 9, 1), 'ausbildungsende': date(2015, 8, 31),
            'schulungsdatum': date(2019, 3, 15), 'betrieb': 'Büroservice AG', 'landkreis_betrieb': 'Esslingen',
            'direktkontakt': False, 'aktiv': True
        },
        {
            'vorname': 'Tom', 'nachname': 'Weber', 'geschlecht': GeschlechtEnum.M,
            'geburtsdatum': date(1998, 11, 8), 'beruf': 'Fachinformatiker', 'bereich': BereichEnum.IHK,
            'ausbildungsbeginn': date(2018, 8, 1), 'ausbildungsende': date(2021, 7, 31),
            'schulungsdatum': date(2022, 1, 20), 'betrieb': 'TechCorp GmbH', 'landkreis_betrieb': 'Ludwigsburg',
            'direktkontakt': True, 'aktiv': True
        },
        {
            'vorname': 'Lisa', 'nachname': 'Müller', 'geschlecht': GeschlechtEnum.W,
            'geburtsdatum': date(1994, 4, 12), 'beruf': 'Medizinische Fachangestellte', 'bereich': BereichEnum.IHK,
            'ausbildungsbeginn': date(2014, 8, 1), 'ausbildungsende': date(2017, 7, 31),
            'schulungsdatum': date(2018, 9, 5), 'betrieb': 'Praxis Dr. Schmidt', 'landkreis_betrieb': 'Böblingen',
            'direktkontakt': False, 'aktiv': True
        },
        {
            'vorname': 'Felix', 'nachname': 'Klein', 'geschlecht': GeschlechtEnum.M,
            'geburtsdatum': date(1996, 9, 30), 'beruf': 'Elektroniker', 'bereich': BereichEnum.IHK,
            'ausbildungsbeginn': date(2016, 8, 1), 'ausbildungsende': date(2019, 7, 31),
            'schulungsdatum': date(2020, 11, 12), 'betrieb': 'Elektro Klein GmbH', 'landkreis_betrieb': 'Göppingen',
            'direktkontakt': True, 'aktiv': True
        },
        {
            'vorname': 'Sarah', 'nachname': 'Fischer', 'geschlecht': GeschlechtEnum.W,
            'geburtsdatum': date(1993, 12, 3), 'beruf': 'Kauffrau im Einzelhandel', 'bereich': BereichEnum.IHK,
            'ausbildungsbeginn': date(2013, 8, 1), 'ausbildungsende': date(2016, 7, 31),
            'schulungsdatum': date(2017, 6, 18), 'betrieb': 'Supermarkt Fischer', 'landkreis_betrieb': 'Waiblingen',
            'direktkontakt': False, 'aktiv': True
        },
        {
            'vorname': 'David', 'nachname': 'Wagner', 'geschlecht': GeschlechtEnum.M,
            'geburtsdatum': date(1997, 6, 25), 'beruf': 'Mechatroniker', 'bereich': BereichEnum.IHK,
            'ausbildungsbeginn': date(2017, 8, 1), 'ausbildungsende': date(2020, 7, 31),
            'schulungsdatum': date(2021, 4, 8), 'betrieb': 'Maschinenbau Wagner', 'landkreis_betrieb': 'Heilbronn',
            'direktkontakt': True, 'aktiv': True
        },
        {
            'vorname': 'Julia', 'nachname': 'Becker', 'geschlecht': GeschlechtEnum.W,
            'geburtsdatum': date(1995, 1, 18), 'beruf': 'Bankkauffrau', 'bereich': BereichEnum.IHK,
            'ausbildungsbeginn': date(2015, 8, 1), 'ausbildungsende': date(2018, 7, 31),
            'schulungsdatum': date(2019, 2, 14), 'betrieb': 'Volksbank Stuttgart', 'landkreis_betrieb': 'Stuttgart',
            'direktkontakt': False, 'aktiv': True
        },
        {
            'vorname': 'Michael', 'nachname': 'Hoffmann', 'geschlecht': GeschlechtEnum.M,
            'geburtsdatum': date(1991, 8, 7), 'beruf': 'Steuerfachangestellter', 'bereich': BereichEnum.IHK,
            'ausbildungsbeginn': date(2011, 8, 1), 'ausbildungsende': date(2014, 7, 31),
            'schulungsdatum': date(2016, 10, 22), 'betrieb': 'Steuerberatung Hoffmann', 'landkreis_betrieb': 'Esslingen',
            'direktkontakt': True, 'aktiv': True
        },
        {
            'vorname': 'Nina', 'nachname': 'Schäfer', 'geschlecht': GeschlechtEnum.W,
            'geburtsdatum': date(1996, 5, 14), 'beruf': 'Kauffrau für Spedition', 'bereich': BereichEnum.IHK,
            'ausbildungsbeginn': date(2016, 8, 1), 'ausbildungsende': date(2019, 7, 31),
            'schulungsdatum': date(2020, 7, 30), 'betrieb': 'Logistik Schäfer', 'landkreis_betrieb': 'Ludwigsburg',
            'direktkontakt': False, 'aktiv': True
        },
        
        # HWK-Bereich
        {
            'vorname': 'Markus', 'nachname': 'Koch', 'geschlecht': GeschlechtEnum.M,
            'geburtsdatum': date(1994, 2, 28), 'beruf': 'Maler und Lackierer', 'bereich': BereichEnum.HWK,
            'ausbildungsbeginn': date(2014, 8, 1), 'ausbildungsende': date(2017, 7, 31),
            'schulungsdatum': date(2018, 5, 12), 'betrieb': 'Malerbetrieb Koch', 'landkreis_betrieb': 'Böblingen',
            'direktkontakt': True, 'aktiv': True
        },
        {
            'vorname': 'Claudia', 'nachname': 'Schwarz', 'geschlecht': GeschlechtEnum.W,
            'geburtsdatum': date(1993, 10, 11), 'beruf': 'Friseurin', 'bereich': BereichEnum.HWK,
            'ausbildungsbeginn': date(2013, 8, 1), 'ausbildungsende': date(2016, 7, 31),
            'schulungsdatum': date(2017, 8, 25), 'betrieb': 'Salon Schwarz', 'landkreis_betrieb': 'Göppingen',
            'direktkontakt': False, 'aktiv': True
        },
        {
            'vorname': 'Stefan', 'nachname': 'Bauer', 'geschlecht': GeschlechtEnum.M,
            'geburtsdatum': date(1996, 12, 19), 'beruf': 'Bäcker', 'bereich': BereichEnum.HWK,
            'ausbildungsbeginn': date(2016, 8, 1), 'ausbildungsende': date(2019, 7, 31),
            'schulungsdatum': date(2020, 3, 10), 'betrieb': 'Bäckerei Bauer', 'landkreis_betrieb': 'Waiblingen',
            'direktkontakt': True, 'aktiv': True
        },
        {
            'vorname': 'Petra', 'nachname': 'Meyer', 'geschlecht': GeschlechtEnum.W,
            'geburtsdatum': date(1992, 6, 8), 'beruf': 'Floristin', 'bereich': BereichEnum.HWK,
            'ausbildungsbeginn': date(2012, 8, 1), 'ausbildungsende': date(2015, 7, 31),
            'schulungsdatum': date(2016, 9, 15), 'betrieb': 'Blumenladen Meyer', 'landkreis_betrieb': 'Heilbronn',
            'direktkontakt': False, 'aktiv': True
        },
        {
            'vorname': 'Andreas', 'nachname': 'Krause', 'geschlecht': GeschlechtEnum.M,
            'geburtsdatum': date(1995, 4, 3), 'beruf': 'Tischler', 'bereich': BereichEnum.HWK,
            'ausbildungsbeginn': date(2015, 8, 1), 'ausbildungsende': date(2018, 7, 31),
            'schulungsdatum': date(2019, 11, 8), 'betrieb': 'Schreinerei Krause', 'landkreis_betrieb': 'Stuttgart',
            'direktkontakt': True, 'aktiv': True
        },
        
        # Sonstiges
        {
            'vorname': 'Sandra', 'nachname': 'Wolf', 'geschlecht': GeschlechtEnum.W,
            'geburtsdatum': date(1994, 9, 16), 'beruf': 'Erzieherin', 'bereich': BereichEnum.SONSTIGES,
            'ausbildungsbeginn': date(2014, 8, 1), 'ausbildungsende': date(2017, 7, 31),
            'schulungsdatum': date(2018, 4, 20), 'betrieb': 'Kindergarten Sonnenschein', 'landkreis_betrieb': 'Esslingen',
            'direktkontakt': False, 'aktiv': True
        },
        {
            'vorname': 'Thomas', 'nachname': 'Neumann', 'geschlecht': GeschlechtEnum.M,
            'geburtsdatum': date(1991, 11, 25), 'beruf': 'Altenpfleger', 'bereich': BereichEnum.SONSTIGES,
            'ausbildungsbeginn': date(2011, 8, 1), 'ausbildungsende': date(2014, 7, 31),
            'schulungsdatum': date(2016, 6, 12), 'betrieb': 'Seniorenheim Neumann', 'landkreis_betrieb': 'Ludwigsburg',
            'direktkontakt': True, 'aktiv': True
        },
        {
            'vorname': 'Monika', 'nachname': 'Richter', 'geschlecht': GeschlechtEnum.W,
            'geburtsdatum': date(1993, 7, 4), 'beruf': 'Krankenschwester', 'bereich': BereichEnum.SONSTIGES,
            'ausbildungsbeginn': date(2013, 8, 1), 'ausbildungsende': date(2016, 7, 31),
            'schulungsdatum': date(2017, 12, 3), 'betrieb': 'Krankenhaus Stuttgart', 'landkreis_betrieb': 'Stuttgart',
            'direktkontakt': False, 'aktiv': True
        },
        {
            'vorname': 'Frank', 'nachname': 'Schubert', 'geschlecht': GeschlechtEnum.M,
            'geburtsdatum': date(1996, 1, 30), 'beruf': 'Physiotherapeut', 'bereich': BereichEnum.SONSTIGES,
            'ausbildungsbeginn': date(2016, 8, 1), 'ausbildungsende': date(2019, 7, 31),
            'schulungsdatum': date(2020, 8, 18), 'betrieb': 'Physiotherapie Schubert', 'landkreis_betrieb': 'Böblingen',
            'direktkontakt': True, 'aktiv': True
        },
        {
            'vorname': 'Katrin', 'nachname': 'Zimmermann', 'geschlecht': GeschlechtEnum.W,
            'geburtsdatum': date(1995, 12, 7), 'beruf': 'Logopädin', 'bereich': BereichEnum.SONSTIGES,
            'ausbildungsbeginn': date(2015, 8, 1), 'ausbildungsende': date(2018, 7, 31),
            'schulungsdatum': date(2019, 5, 22), 'betrieb': 'Logopädie Zimmermann', 'landkreis_betrieb': 'Göppingen',
            'direktkontakt': False, 'aktiv': True
        }
    ]
    
    # ABB erstellen
    abbs = []
    for i, data in enumerate(abb_data):
        # Laufnummer generieren
        data['laufnummer'] = f"ABB-{2024:04d}-{i+1:03d}"
        
        # Zusätzliche Felder
        data['schulabschluss'] = random.choice(['Realschulabschluss', 'Abitur', 'Hauptschulabschluss'])
        data['vorbildung'] = random.choice(['Keine', 'Berufsvorbereitung', 'Praktikum'])
        data['studienabbrecher'] = random.choice([True, False])
        data['zq'] = random.choice(['Keine', 'Zusatzqualifikation', 'Fremdsprachen'])
        data['mobilnummer'] = f"0171-{random.randint(1000000, 9999999)}"
        data['email_beruf'] = f"{data['vorname'].lower()}.{data['nachname'].lower()}@{data['betrieb'].lower().replace(' ', '').replace('gmbh', '').replace('ag', '')}.de"
        data['email_privat'] = f"{data['vorname'].lower()}.{data['nachname'].lower()}@gmail.com"
        data['telefon_beruf'] = f"0711-{random.randint(1000000, 9999999)}"
        data['telefon_privat'] = f"0711-{random.randint(1000000, 9999999)}"
        data['betriebadresse'] = f"Musterstraße {random.randint(1, 100)}, {random.randint(70000, 75000)} {data['landkreis_betrieb']}"
        data['asp_name'] = f"Max Mustermann (ASP)"
        data['asp_telefon'] = f"0711-{random.randint(1000000, 9999999)}"
        data['asp_email'] = f"asp.{data['betrieb'].lower().replace(' ', '').replace('gmbh', '').replace('ag', '')}@ihk.de"
        data['eindruck'] = f"Sehr engagierter Ausbildungsbotschafter mit guter Kommunikationsfähigkeit."
        data['hinweise'] = f"Bevorzugt Einsätze in der Nähe von {data['landkreis_betrieb']}."
        
        abb = ABB(**data)
        db.add(abb)
        abbs.append(abb)
    
    db.commit()
    return abbs

def create_einsatz_seed_data(db) -> list:
    """Erstellt Einsatz-Beispieldaten"""
    
    # Schulen und Schularten
    schulen = [
        "Gymnasium Stuttgart", "Realschule Esslingen", "Hauptschule Ludwigsburg", "Gemeinschaftsschule Böblingen",
        "Berufsschule Göppingen", "Werkrealschule Waiblingen", "Gymnasium Heilbronn", "Realschule Stuttgart",
        "Hauptschule Esslingen", "Gemeinschaftsschule Ludwigsburg", "Berufsschule Böblingen", "Werkrealschule Göppingen",
        "Gymnasium Waiblingen", "Realschule Heilbronn", "Hauptschule Stuttgart", "Gemeinschaftsschule Esslingen",
        "Berufsschule Ludwigsburg", "Werkrealschule Böblingen", "Gymnasium Göppingen", "Realschule Waiblingen"
    ]
    
    schularten = ["Gymnasium", "Realschule", "Hauptschule", "Gemeinschaftsschule", "Berufsschule", "Werkrealschule"]
    staedte = ["Stuttgart", "Esslingen", "Ludwigsburg", "Böblingen", "Göppingen", "Waiblingen", "Heilbronn"]
    landkreise = ["Stuttgart", "Esslingen", "Ludwigsburg", "Böblingen", "Göppingen", "Rems-Murr-Kreis", "Heilbronn"]
    klassenstufen = ["8", "9", "10", "11", "12", "13"]
    
    # Einsätze erstellen
    einsaetze = []
    start_date = date.today() + timedelta(days=30)  # Start in 30 Tagen
    
    for i in range(20):
        # Zufällige Daten
        schulname = random.choice(schulen)
        schulart = random.choice(schularten)
        stadt = random.choice(staedte)
        landkreis = random.choice(landkreise)
        klassenstufe = random.choice(klassenstufen)
        
        # Datum (über die nächsten 6 Monate verteilt)
        einsatzdatum = start_date + timedelta(days=random.randint(0, 180))
        
        # Schüleranzahl (1-25, manchmal mehr für Splitting-Test)
        if random.random() < 0.2:  # 20% Chance für mehr als 25 Schüler
            schueleranzahl = random.randint(26, 50)
        else:
            schueleranzahl = random.randint(15, 25)
        
        einsatz_data = {
            'einsatzdatum': einsatzdatum,
            'schulname': schulname,
            'schulart': schulart,
            'partner': random.choice([None, "IHK Stuttgart", "HWK Stuttgart", "Agentur für Arbeit"]),
            'stadt': stadt,
            'landkreis': landkreis,
            'stubo': random.choice([True, False]),
            'online': random.choice([True, False]),
            'klassenstufe': klassenstufe,
            'schueleranzahl': schueleranzahl
        }
        
        einsatz = Einsatz(**einsatz_data)
        db.add(einsatz)
        einsaetze.append(einsatz)
    
    db.commit()
    return einsaetze

def create_zuordnungs_seed_data(db, abbs, einsaetze):
    """Erstellt Zuordnungs-Beispieldaten"""
    
    # Rollen für Zuordnungen
    rollen = ["Lead", "Co", "Unterstützung", None]
    
    # Zuordnungen erstellen
    for einsatz in einsaetze:
        # 1-3 ABB pro Einsatz zuordnen
        num_abbs = random.randint(1, min(3, len(abbs)))
        selected_abbs = random.sample(abbs, num_abbs)
        
        for abb in selected_abbs:
            rolle = random.choice(rollen)
            kommentar = random.choice([
                "Sehr engagiert bei der Präsentation",
                "Gute Interaktion mit den Schülern",
                "Professioneller Auftritt",
                "Kann gut von der Praxis berichten",
                None
            ])
            
            zuordnung = ABBEinsatz(
                abb_id=abb.id,
                einsatz_id=einsatz.id,
                rolle=rolle,
                kommentar=kommentar
            )
            db.add(zuordnung)
    
    db.commit()

if __name__ == "__main__":
    create_seed_data()
