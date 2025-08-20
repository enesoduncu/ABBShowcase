#!/usr/bin/env python3
"""
Smoke-Tests für ABB Streamlit
Testet die grundlegenden CRUD-Operationen und die Splitting-Logik
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from database import get_db, create_tables, drop_tables
from services.abb_service import ABBService
from services.einsatz_service import EinsatzService
from services.link_service import LinkService
from schemas.abb import ABBCreate
from schemas.einsatz import EinsatzCreate
from models.abb import BereichEnum, GeschlechtEnum
from datetime import date, timedelta

def test_abb_crud():
    """Testet ABB CRUD-Operationen"""
    print("🧪 Teste ABB CRUD-Operationen...")
    
    db = get_db()
    abb_service = ABBService(db)
    
    try:
        # ABB erstellen
        abb_data = ABBCreate(
            vorname="Test",
            nachname="ABB",
            geschlecht=GeschlechtEnum.M,
            geburtsdatum=date(1995, 1, 1),
            beruf="Testberuf",
            bereich=BereichEnum.IHK,
            ausbildungsbeginn=date(2015, 8, 1)
        )
        
        abb = abb_service.create(abb_data)
        print(f"✅ ABB erstellt: ID {abb.id}")
        
        # ABB abrufen
        retrieved_abb = abb_service.get_by_id(abb.id)
        assert retrieved_abb is not None, "ABB konnte nicht abgerufen werden"
        assert retrieved_abb.vorname == "Test", "Vorname stimmt nicht überein"
        print("✅ ABB erfolgreich abgerufen")
        
        # ABB aktualisieren
        updated_abb = abb_service.update(abb.id, {"beruf": "Aktualisierter Testberuf"})
        assert updated_abb.beruf == "Aktualisierter Testberuf", "Beruf wurde nicht aktualisiert"
        print("✅ ABB erfolgreich aktualisiert")
        
        # ABB löschen
        success = abb_service.delete(abb.id)
        assert success, "ABB konnte nicht gelöscht werden"
        print("✅ ABB erfolgreich gelöscht")
        
        print("✅ ABB CRUD-Tests bestanden!")
        return True
        
    except Exception as e:
        print(f"❌ ABB CRUD-Test fehlgeschlagen: {str(e)}")
        return False

def test_einsatz_splitting():
    """Testet die automatische 25er-Gruppen-Aufteilung"""
    print("🧪 Teste Einsatz-Splitting-Logik...")
    
    db = get_db()
    einsatz_service = EinsatzService(db)
    
    try:
        # Test-Einsatz mit 100 Schülern
        einsatz_data = EinsatzCreate(
            einsatzdatum=date.today() + timedelta(days=30),
            schulname="Test-Schule",
            schulart="Gymnasium",
            stadt="Teststadt",
            landkreis="Testkreis",
            klassenstufe="10",
            schueleranzahl=25  # Wird für Splitting-Test überschrieben
        )
        
        # Splitting testen
        split_einsaetze = einsatz_service.split_einsatz_by_25(einsatz_data, 100)
        
        # Prüfen, ob korrekt aufgeteilt wurde
        assert len(split_einsaetze) == 4, f"Erwartet: 4 Einsätze, erhalten: {len(split_einsaetze)}"
        
        # Schüleranzahl prüfen
        total_schueler = sum(e.schueleranzahl for e in split_einsaetze)
        assert total_schueler == 100, f"Erwartet: 100 Schüler, erhalten: {total_schueler}"
        
        # Max. 25 Schüler pro Einsatz prüfen
        for einsatz in split_einsaetze:
            assert einsatz.schueleranzahl <= 25, f"Einsatz hat mehr als 25 Schüler: {einsatz.schueleranzahl}"
        
        print("✅ Einsatz-Splitting-Tests bestanden!")
        return True
        
    except Exception as e:
        print(f"❌ Einsatz-Splitting-Test fehlgeschlagen: {str(e)}")
        return False

def test_link_service():
    """Testet den Link-Service"""
    print("🧪 Teste Link-Service...")
    
    db = get_db()
    link_service = LinkService(db)
    abb_service = ABBService(db)
    einsatz_service = EinsatzService(db)
    
    try:
        # Test-ABB erstellen
        abb_data = ABBCreate(
            vorname="Link",
            nachname="Test",
            geschlecht=GeschlechtEnum.W,
            geburtsdatum=date(1995, 1, 1),
            beruf="Linktestberuf",
            bereich=BereichEnum.HWK,
            ausbildungsbeginn=date(2015, 8, 1)
        )
        abb = abb_service.create(abb_data)
        
        # Test-Einsatz erstellen
        einsatz_data = EinsatzCreate(
            einsatzdatum=date.today() + timedelta(days=30),
            schulname="Link-Test-Schule",
            schulart="Realschule",
            stadt="Linkteststadt",
            landkreis="Linktestkreis",
            klassenstufe="9",
            schueleranzahl=20
        )
        einsatz = einsatz_service.create(einsatz_data)
        
        # Verknüpfung erstellen
        link = link_service.assign_abb_to_einsatz(abb.id, einsatz.id, "Lead", "Test-Kommentar")
        assert link is not None, "Verknüpfung konnte nicht erstellt werden"
        print("✅ Verknüpfung erfolgreich erstellt")
        
        # Verknüpfung abrufen
        retrieved_link = link_service.get_link(abb.id, einsatz.id)
        assert retrieved_link is not None, "Verknüpfung konnte nicht abgerufen werden"
        assert retrieved_link.rolle == "Lead", "Rolle stimmt nicht überein"
        print("✅ Verknüpfung erfolgreich abgerufen")
        
        # Verknüpfung löschen
        success = link_service.remove_abb_from_einsatz(abb.id, einsatz.id)
        assert success, "Verknüpfung konnte nicht gelöscht werden"
        print("✅ Verknüpfung erfolgreich gelöscht")
        
        # Aufräumen
        abb_service.delete(abb.id)
        einsatz_service.delete(einsatz.id)
        
        print("✅ Link-Service-Tests bestanden!")
        return True
        
    except Exception as e:
        print(f"❌ Link-Service-Test fehlgeschlagen: {str(e)}")
        return False

def run_all_tests():
    """Führt alle Tests aus"""
    print("🚀 Starte Smoke-Tests für ABB Streamlit...")
    print("=" * 50)
    
    # Datenbank vorbereiten
    try:
        drop_tables()
        create_tables()
        print("✅ Datenbank für Tests vorbereitet")
    except Exception as e:
        print(f"❌ Fehler bei der Datenbankvorbereitung: {str(e)}")
        return False
    
    # Tests ausführen
    tests = [
        test_abb_crud,
        test_einsatz_splitting,
        test_link_service
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    # Zusammenfassung
    print("=" * 50)
    print(f"📊 Testergebnis: {passed}/{total} Tests bestanden")
    
    if passed == total:
        print("🎉 Alle Tests erfolgreich!")
        return True
    else:
        print("⚠️ Einige Tests fehlgeschlagen")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
