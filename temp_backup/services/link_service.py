from typing import List, Optional, Tuple, Dict, Any
from datetime import date

from schemas.abb_einsatz import ABBEinsatzCreate, ABBEinsatzUpdate
from schemas.common import PaginationParams
import database

class LinkService:
    """Service für ABB-Einsatz-Verknüpfungen"""
    
    def __init__(self):
        pass
    
    def assign_abb_to_einsatz(self, abb_id: int, einsatz_id: int, rolle: str = None, kommentar: str = None) -> Dict[str, Any]:
        """Ordnet einen ABB einem Einsatz zu"""
        # Prüfen, ob die Verknüpfung bereits existiert
        existing = self.get_link(abb_id, einsatz_id)
        if existing:
            raise ValueError("Diese Verknüpfung existiert bereits")
        
        # Prüfen, ob ABB und Einsatz existieren
        abb = database.execute_single_query('SELECT * FROM abb WHERE id = ?', (abb_id,))
        if not abb:
            raise ValueError("ABB nicht gefunden")
        
        einsatz = database.execute_single_query('SELECT * FROM einsatz WHERE id = ?', (einsatz_id,))
        if not einsatz:
            raise ValueError("Einsatz nicht gefunden")
        
        # Verknüpfung erstellen
        query = '''
            INSERT INTO abb_einsatz (abb_id, einsatz_id, zuordnungs_datum, notizen)
            VALUES (?, ?, CURRENT_DATE, ?)
        '''
        link_id = database.execute_insert(query, (abb_id, einsatz_id, kommentar or ''))
        
        return self.get_link(abb_id, einsatz_id)
    
    def remove_abb_from_einsatz(self, abb_id: int, einsatz_id: int) -> bool:
        """Entfernt einen ABB von einem Einsatz"""
        query = 'DELETE FROM abb_einsatz WHERE abb_id = ? AND einsatz_id = ?'
        affected_rows = database.execute_delete(query, (abb_id, einsatz_id))
        return affected_rows > 0
    
    def get_link(self, abb_id: int, einsatz_id: int) -> Optional[Dict[str, Any]]:
        """Holt eine spezifische Verknüpfung"""
        query = 'SELECT * FROM abb_einsatz WHERE abb_id = ? AND einsatz_id = ?'
        return database.execute_single_query(query, (abb_id, einsatz_id))
    
    def get_links_by_einsatz(self, einsatz_id: int) -> List[Dict[str, Any]]:
        """Holt alle ABB für einen bestimmten Einsatz"""
        query = '''
            SELECT ae.*, 
                   a.vorname || ' ' || a.nachname as abb_name, 
                   a.beruf as abb_beruf
            FROM abb_einsatz ae
            JOIN abb a ON ae.abb_id = a.id
            WHERE ae.einsatz_id = ?
        '''
        return database.execute_query(query, (einsatz_id,))
    
    def get_links_by_abb(self, abb_id: int) -> List[Dict[str, Any]]:
        """Holt alle Einsätze für einen bestimmten ABB"""
        query = '''
            SELECT ae.*, e.name as einsatz_name, e.beschreibung as einsatz_beschreibung
            FROM abb_einsatz ae
            JOIN einsatz e ON ae.einsatz_id = e.id
            WHERE ae.abb_id = ?
        '''
        return database.execute_query(query, (abb_id,))
    
    def get_all_links(self, pagination: PaginationParams = None) -> Tuple[List[Dict[str, Any]], int]:
        """Holt alle Verknüpfungen mit optionaler Pagination"""
        # Gesamtanzahl
        count_query = 'SELECT COUNT(*) as total FROM abb_einsatz'
        total_result = database.execute_single_query(count_query)
        total = total_result['total'] if total_result else 0
        
        # Daten mit Pagination
        query = '''
            SELECT ae.*, 
                   a.vorname || ' ' || a.nachname as abb_name, 
                   e.name as einsatz_name
            FROM abb_einsatz ae
            JOIN abb a ON ae.abb_id = a.id
            JOIN einsatz e ON ae.einsatz_id = e.id
            ORDER BY ae.zuordnungs_datum DESC
        '''
        if pagination:
            query += f' LIMIT {pagination.size} OFFSET {pagination.offset}'
        
        results = database.execute_query(query)
        return results, total
    
    def update_link(self, abb_id: int, einsatz_id: int, link_data: ABBEinsatzUpdate) -> Optional[Dict[str, Any]]:
        """Aktualisiert eine Verknüpfung"""
        link = self.get_link(abb_id, einsatz_id)
        if not link:
            return None
        
        # Update-Query aufbauen
        update_fields = []
        params = []
        
        if hasattr(link_data, 'notizen') and link_data.notizen:
            update_fields.append("notizen = ?")
            params.append(link_data.notizen)
        
        if update_fields:
            query = f"UPDATE abb_einsatz SET {', '.join(update_fields)} WHERE abb_id = ? AND einsatz_id = ?"
            params.extend([abb_id, einsatz_id])
            
            database.execute_update(query, tuple(params))
            return self.get_link(abb_id, einsatz_id)
        
        return link
    
    def bulk_assign_abbs_to_einsatz(self, abb_ids: List[int], einsatz_id: int, rolle: str = None) -> List[Dict[str, Any]]:
        """Ordnet mehrere ABB einem Einsatz zu"""
        links = []
        
        for abb_id in abb_ids:
            try:
                link = self.assign_abb_to_einsatz(abb_id, einsatz_id, rolle)
                links.append(link)
            except ValueError as e:
                # Verknüpfung existiert bereits, überspringen
                continue
        
        return links
    
    def bulk_assign_einsaetze_to_abb(self, abb_id: int, einsatz_ids: List[int], rolle: str = None) -> List[Dict[str, Any]]:
        """Ordnet einen ABB mehreren Einsätzen zu"""
        links = []
        
        for einsatz_id in einsatz_ids:
            try:
                link = self.assign_abb_to_einsatz(abb_id, einsatz_id, rolle)
                links.append(link)
            except ValueError as e:
                # Verknüpfung existiert bereits, überspringen
                continue
        
        return links
    
    def get_einsatz_statistics(self, einsatz_id: int) -> dict:
        """Holt Statistiken für einen bestimmten Einsatz"""
        stats = {}
        
        # Anzahl der zugeordneten ABB
        query = "SELECT COUNT(*) as count FROM abb_einsatz WHERE einsatz_id = ?"
        result = database.execute_single_query(query, (einsatz_id,))
        stats['abb_anzahl'] = result['count'] if result else 0
        
        # ABB nach Bereich
        query = '''
            SELECT a.bereich, COUNT(*) as count
            FROM abb_einsatz ae
            JOIN abb a ON ae.abb_id = a.id
            WHERE ae.einsatz_id = ?
            GROUP BY a.bereich
        '''
        results = database.execute_query(query, (einsatz_id,))
        stats['abb_nach_bereich'] = {r['bereich']: r['count'] for r in results}
        
        return stats
    
    def get_abb_statistics(self, abb_id: int) -> dict:
        """Holt Statistiken für einen bestimmten ABB"""
        stats = {}
        
        # Anzahl der Einsätze
        query = "SELECT COUNT(*) as count FROM abb_einsatz WHERE abb_id = ?"
        result = database.execute_single_query(query, (abb_id,))
        stats['einsatz_anzahl'] = result['count'] if result else 0
        
        # Einsätze nach Status
        query = '''
            SELECT e.status, COUNT(*) as count
            FROM abb_einsatz ae
            JOIN einsatz e ON ae.einsatz_id = e.id
            WHERE ae.abb_id = ?
            GROUP BY e.status
        '''
        results = database.execute_query(query, (abb_id,))
        stats['einsaetze_nach_status'] = {r['status']: r['count'] for r in results}
        
        return stats
    
    def get_available_abbs_for_einsatz(self, einsatz_id: int) -> List[Dict[str, Any]]:
        """Holt alle verfügbaren ABB für einen Einsatz (noch nicht zugeordnet)"""
        query = '''
            SELECT a.* FROM abb a
            WHERE a.aktiv = 1
            AND a.id NOT IN (
                SELECT abb_id FROM abb_einsatz WHERE einsatz_id = ?
            )
        '''
        return database.execute_query(query, (einsatz_id,))
    
    def get_available_einsaetze_for_abb(self, abb_id: int) -> List[Dict[str, Any]]:
        """Holt alle verfügbaren Einsätze für einen ABB (noch nicht zugeordnet)"""
        query = '''
            SELECT e.* FROM einsatz e
            WHERE e.id NOT IN (
                SELECT einsatz_id FROM abb_einsatz WHERE abb_id = ?
            )
        '''
        return database.execute_query(query, (abb_id,))
