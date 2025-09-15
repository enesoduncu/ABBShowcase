from typing import List, Optional, Tuple, Dict, Any
from datetime import date
import pandas as pd

from schemas.abb import ABBCreate, ABBUpdate, ABBFilter
from schemas.common import PaginationParams
import database

class ABBService:
    """Service für ABB-Operationen"""
    
    def __init__(self):
        pass
    
    def create(self, abb_data: ABBCreate) -> Dict[str, Any]:
        """Erstellt einen neuen ABB"""
        # Dublettenprüfung
        if self._check_duplicate(abb_data):
            raise ValueError("Ein ABB mit diesen Daten existiert bereits")
        
        query = '''
            INSERT INTO abb (
                laufnummer, aktiv, vorname, nachname, geschlecht, geburtsdatum,
                schulabschluss, vorbildung, studienabbrecher, beruf, zq, bereich,
                ausbildungsbeginn, ausbildungsende, schulungsdatum, mobilnummer,
                email_beruf, email_privat, telefon_beruf, telefon_privat,
                direktkontakt, betrieb, betriebadresse, landkreis_betrieb,
                asp_name, asp_telefon, asp_email, eindruck, hinweise,
                created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        '''
        abb_id = database.execute_insert(query, (
            abb_data.laufnummer,
            abb_data.aktiv,
            abb_data.vorname,
            abb_data.nachname,
            abb_data.geschlecht,
            abb_data.geburtsdatum,
            abb_data.schulabschluss,
            abb_data.vorbildung,
            abb_data.studienabbrecher,
            abb_data.beruf,
            abb_data.zq,
            abb_data.bereich,
            abb_data.ausbildungsbeginn,
            abb_data.ausbildungsende,
            abb_data.schulungsdatum,
            abb_data.mobilnummer,
            abb_data.email_beruf,
            abb_data.email_privat,
            abb_data.telefon_beruf,
            abb_data.telefon_privat,
            abb_data.direktkontakt,
            abb_data.betrieb,
            abb_data.betriebadresse,
            abb_data.landkreis_betrieb,
            abb_data.asp_name,
            abb_data.asp_telefon,
            abb_data.asp_email,
            abb_data.eindruck,
            abb_data.hinweise
        ))
        
        return self.get_by_id(abb_id)
    
    def get_by_id(self, abb_id: int) -> Optional[Dict[str, Any]]:
        """Holt einen ABB anhand der ID"""
        query = 'SELECT * FROM abb WHERE id = ?'
        return database.execute_single_query(query, (abb_id,))
    
    def get_all(self, pagination: PaginationParams = None) -> Tuple[List[Dict[str, Any]], int]:
        """Holt alle ABB mit optionaler Pagination"""
        # Gesamtanzahl
        count_query = 'SELECT COUNT(*) as total FROM abb'
        total_result = database.execute_single_query(count_query)
        total = total_result['total'] if total_result else 0
        
        # Daten mit Pagination
        query = 'SELECT * FROM abb ORDER BY vorname, nachname'
        if pagination:
            query += f' LIMIT {pagination.size} OFFSET {pagination.offset}'
        
        results = database.execute_query(query)
        return results, total
    
    def get_filtered(self, filters: ABBFilter, pagination: PaginationParams = None) -> Tuple[List[Dict[str, Any]], int]:
        """Holt gefilterte ABB"""
        where_conditions = []
        params = []
        
        # Filter anwenden
        if filters.aktiv is not None:
            where_conditions.append("aktiv = ?")
            params.append(1 if filters.aktiv else 0)
        
        if filters.bereich:
            where_conditions.append("bereich = ?")
            params.append(str(filters.bereich))
        
        if filters.landkreis_betrieb:
            where_conditions.append("landkreis_betrieb LIKE ?")
            params.append(f"%{filters.landkreis_betrieb}%")
        
        if filters.suche:
            where_conditions.append("(vorname LIKE ? OR nachname LIKE ? OR beruf LIKE ?)")
            search_term = f"%{filters.suche}%"
            params.extend([search_term, search_term, search_term])
        
        # SQL-Query aufbauen
        where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
        
        # Gesamtanzahl
        count_query = f'SELECT COUNT(*) as total FROM abb WHERE {where_clause}'
        total_result = database.execute_single_query(count_query, tuple(params))
        total = total_result['total'] if total_result else 0
        
        # Daten mit Pagination
        query = f'SELECT * FROM abb WHERE {where_clause} ORDER BY vorname, nachname'
        if pagination:
            query += f' LIMIT {pagination.size} OFFSET {pagination.offset}'
        
        results = database.execute_query(query, tuple(params))
        return results, total
    
    def update(self, abb_id: int, abb_data: ABBUpdate) -> Optional[Dict[str, Any]]:
        """Aktualisiert einen ABB"""
        abb = self.get_by_id(abb_id)
        if not abb:
            return None
        
        # Update-Query aufbauen
        update_fields = []
        params = []
        
        if hasattr(abb_data, 'vorname') and abb_data.vorname:
            update_fields.append("vorname = ?")
            params.append(abb_data.vorname)
        
        if hasattr(abb_data, 'nachname') and abb_data.nachname:
            update_fields.append("nachname = ?")
            params.append(abb_data.nachname)
        
        if hasattr(abb_data, 'bereich') and abb_data.bereich:
            update_fields.append("bereich = ?")
            params.append(str(abb_data.bereich))
        
        if update_fields:
            update_fields.append("updated_at = CURRENT_TIMESTAMP")
            query = f"UPDATE abb SET {', '.join(update_fields)} WHERE id = ?"
            params.append(abb_id)
            
            database.execute_update(query, tuple(params))
            return self.get_by_id(abb_id)
        
        return abb
    
    def delete(self, abb_id: int) -> bool:
        """Löscht einen ABB"""
        query = 'DELETE FROM abb WHERE id = ?'
        affected_rows = database.execute_delete(query, (abb_id,))
        return affected_rows > 0
    
    def _check_duplicate(self, abb_data: ABBCreate) -> bool:
        """Prüft auf Dubletten basierend auf Vorname und Nachname"""
        query = 'SELECT COUNT(*) as count FROM abb WHERE vorname = ? AND nachname = ?'
        result = database.execute_single_query(query, (abb_data.vorname, abb_data.nachname))
        return result['count'] > 0 if result else False
    
    def get_statistics(self) -> dict:
        """Holt Statistiken für das Dashboard"""
        stats = {}
        
        # Gesamtanzahl aktive ABB
        query = "SELECT COUNT(*) as count FROM abb WHERE aktiv = 1"
        result = database.execute_single_query(query)
        stats['aktiv_gesamt'] = result['count'] if result else 0
        
        # ABB nach Bereich
        query = "SELECT bereich, COUNT(*) as count FROM abb GROUP BY bereich"
        results = database.execute_query(query)
        stats['nach_bereich'] = {r['bereich']: r['count'] for r in results}
        
        # ABB nach Status
        query = "SELECT aktiv, COUNT(*) as count FROM abb GROUP BY aktiv"
        results = database.execute_query(query)
        stats['nach_status'] = {('Aktiv' if r['aktiv'] else 'Inaktiv'): r['count'] for r in results}
        
        return stats
    
    def get_kategorien(self) -> List[str]:
        """Gibt alle verfügbaren Kategorien zurück"""
        query = "SELECT DISTINCT bereich FROM abb WHERE bereich IS NOT NULL ORDER BY bereich"
        results = database.execute_query(query)
        return [r['bereich'] for r in results if r['bereich']]
    
    def get_berufe(self) -> List[str]:
        """Gibt alle verfügbaren Berufe zurück"""
        query = "SELECT DISTINCT beruf FROM abb WHERE beruf IS NOT NULL ORDER BY beruf"
        results = database.execute_query(query)
        return [r['beruf'] for r in results if r['beruf']]
    
    def get_schulabschluesse(self) -> List[str]:
        """Gibt alle verfügbaren Schulabschlüsse zurück"""
        query = "SELECT DISTINCT schulabschluss FROM abb WHERE schulabschluss IS NOT NULL ORDER BY schulabschluss"
        results = database.execute_query(query)
        return [r['schulabschluss'] for r in results if r['schulabschluss']]
    
    def get_landkreise(self) -> List[str]:
        """Gibt alle verfügbaren Betriebslandkreise zurück"""
        query = "SELECT DISTINCT landkreis_betrieb FROM abb WHERE landkreis_betrieb IS NOT NULL ORDER BY landkreis_betrieb"
        results = database.execute_query(query)
        return [r['landkreis_betrieb'] for r in results if r['landkreis_betrieb']]
