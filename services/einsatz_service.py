from typing import List, Optional, Tuple, Dict, Any
from datetime import date, datetime
import math

from schemas.einsatz import EinsatzCreate, EinsatzUpdate, EinsatzFilter, EinsatzSplitRequest
from schemas.common import PaginationParams
import config
import database

class EinsatzService:
    """Service für Einsatz-Operationen"""
    
    def __init__(self):
        pass
    
    def create(self, einsatz_data: EinsatzCreate) -> Dict[str, Any]:
        """Erstellt einen neuen Einsatz"""
        query = '''
            INSERT INTO einsatz (name, beschreibung, start_datum, end_datum, status, prioritaet, erstellt_am, aktualisiert_am)
            VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        '''
        einsatz_id = database.execute_insert(query, (
            einsatz_data.name,
            einsatz_data.beschreibung,
            einsatz_data.start_datum,
            einsatz_data.end_datum,
            'geplant',
            'normal'
        ))
        
        return self.get_by_id(einsatz_id)
    
    def create_multiple(self, einsaetze: List[EinsatzCreate]) -> List[Dict[str, Any]]:
        """Erstellt mehrere Einsätze in einer Transaktion"""
        einsatz_objects = []
        for einsatz_data in einsaetze:
            einsatz = self.create(einsatz_data)
            einsatz_objects.append(einsatz)
        
        return einsatz_objects
    
    def split_einsatz_by_25(self, einsatz_input: EinsatzCreate, schueleranzahl_gesamt: int) -> List[EinsatzCreate]:
        """Teilt einen Einsatz mit mehr als 25 Schülern automatisch auf"""
        if schueleranzahl_gesamt <= config.MAX_STUDENTS_PER_EINSATZ:
            return [einsatz_input]
        
        einsaetze = []
        rest = schueleranzahl_gesamt
        
        while rest > 0:
            schueler_im_einsatz = min(config.MAX_STUDENTS_PER_EINSATZ, rest)
            einsatz_data = einsatz_input.dict()
            einsatz_data['schueleranzahl'] = schueler_im_einsatz
            einsaetze.append(EinsatzCreate(**einsatz_data))
            rest -= schueler_im_einsatz
        
        return einsaetze
    
    def get_by_id(self, einsatz_id: int) -> Optional[Dict[str, Any]]:
        """Holt einen Einsatz anhand der ID"""
        query = 'SELECT * FROM einsatz WHERE id = ?'
        return database.execute_single_query(query, (einsatz_id,))
    
    def get_all(self, pagination: PaginationParams = None) -> Tuple[List[Dict[str, Any]], int]:
        """Holt alle Einsätze mit optionaler Pagination"""
        # Gesamtanzahl
        count_query = 'SELECT COUNT(*) as total FROM einsatz'
        total_result = database.execute_single_query(count_query)
        total = total_result['total'] if total_result else 0
        
        # Daten mit Pagination
        query = 'SELECT * FROM einsatz ORDER BY start_datum'
        if pagination:
            query += f' LIMIT {pagination.size} OFFSET {pagination.offset}'
        
        results = database.execute_query(query)
        return results, total
    
    def get_filtered(self, filters: EinsatzFilter, pagination: PaginationParams = None) -> Tuple[List[Dict[str, Any]], int]:
        """Holt gefilterte Einsätze"""
        where_conditions = []
        params = []
        
        # Filter anwenden
        if filters.start_datum_von:
            where_conditions.append("start_datum >= ?")
            params.append(filters.start_datum_von)
        
        if filters.start_datum_bis:
            where_conditions.append("start_datum <= ?")
            params.append(filters.start_datum_bis)
        
        if filters.name:
            where_conditions.append("name LIKE ?")
            params.append(f"%{filters.name}%")
        
        if filters.beschreibung:
            where_conditions.append("beschreibung LIKE ?")
            params.append(f"%{filters.beschreibung}%")
        
        if filters.status:
            where_conditions.append("status = ?")
            params.append(filters.status)
        
        if filters.prioritaet:
            where_conditions.append("prioritaet = ?")
            params.append(filters.prioritaet)
        
        # SQL-Query aufbauen
        where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
        
        # Gesamtanzahl
        count_query = f'SELECT COUNT(*) as total FROM einsatz WHERE {where_clause}'
        total_result = database.execute_single_query(count_query, tuple(params))
        total = total_result['total'] if total_result else 0
        
        # Daten mit Pagination
        query = f'SELECT * FROM einsatz WHERE {where_clause} ORDER BY start_datum'
        if pagination:
            query += f' LIMIT {pagination.size} OFFSET {pagination.offset}'
        
        results = database.execute_query(query, tuple(params))
        return results, total
    
    def update(self, einsatz_id: int, einsatz_data: EinsatzUpdate) -> Optional[Dict[str, Any]]:
        """Aktualisiert einen Einsatz"""
        einsatz = self.get_by_id(einsatz_id)
        if not einsatz:
            return None
        
        # Update-Query aufbauen
        update_fields = []
        params = []
        
        if hasattr(einsatz_data, 'name') and einsatz_data.name:
            update_fields.append("name = ?")
            params.append(einsatz_data.name)
        
        if hasattr(einsatz_data, 'beschreibung') and einsatz_data.beschreibung:
            update_fields.append("beschreibung = ?")
            params.append(einsatz_data.beschreibung)
        
        if hasattr(einsatz_data, 'start_datum') and einsatz_data.start_datum:
            update_fields.append("start_datum = ?")
            params.append(einsatz_data.start_datum)
        
        if hasattr(einsatz_data, 'end_datum') and einsatz_data.end_datum:
            update_fields.append("end_datum = ?")
            params.append(einsatz_data.end_datum)
        
        if hasattr(einsatz_data, 'status') and einsatz_data.status:
            update_fields.append("status = ?")
            params.append(einsatz_data.status)
        
        if update_fields:
            update_fields.append("aktualisiert_am = CURRENT_TIMESTAMP")
            query = f"UPDATE einsatz SET {', '.join(update_fields)} WHERE id = ?"
            params.append(einsatz_id)
            
            database.execute_update(query, tuple(params))
            return self.get_by_id(einsatz_id)
        
        return einsatz
    
    def delete(self, einsatz_id: int) -> bool:
        """Löscht einen Einsatz"""
        query = 'DELETE FROM einsatz WHERE id = ?'
        affected_rows = database.execute_delete(query, (einsatz_id,))
        return affected_rows > 0
    
    def get_statistics(self) -> dict:
        """Holt Statistiken für das Dashboard"""
        stats = {}
        
        # Gesamtanzahl Einsätze
        query = "SELECT COUNT(*) as count FROM einsatz"
        result = database.execute_single_query(query)
        stats['gesamt'] = result['count'] if result else 0
        
        # Einsätze nach Status
        query = "SELECT status, COUNT(*) as count FROM einsatz GROUP BY status"
        results = database.execute_query(query)
        stats['nach_status'] = {r['status']: r['count'] for r in results}
        
        # Einsätze nach Priorität
        query = "SELECT prioritaet, COUNT(*) as count FROM einsatz GROUP BY prioritaet"
        results = database.execute_query(query)
        stats['nach_prioritaet'] = {r['prioritaet']: r['count'] for r in results}
        
        # Einsätze nach Monat (aktuelles Jahr)
        current_year = datetime.now().year
        query = f"""
            SELECT strftime('%m', start_datum) as monat, COUNT(*) as count 
            FROM einsatz 
            WHERE strftime('%Y', start_datum) = ? 
            GROUP BY monat
        """
        results = database.execute_query(query, (str(current_year),))
        stats['nach_monat'] = {r['monat']: r['count'] for r in results}
        
        return stats
    
    def get_status(self) -> List[str]:
        """Gibt alle verfügbaren Status zurück"""
        return ['geplant', 'bestätigt', 'in Bearbeitung', 'abgeschlossen', 'abgesagt']
    
    def get_prioritaeten(self) -> List[str]:
        """Gibt alle verfügbaren Prioritäten zurück"""
        return ['niedrig', 'normal', 'hoch', 'kritisch']
    
    def get_landkreise(self) -> List[str]:
        """Gibt alle verfügbaren Landkreise zurück"""
        query = "SELECT DISTINCT landkreis FROM einsatz WHERE landkreis IS NOT NULL ORDER BY landkreis"
        results = database.execute_query(query)
        return [r['landkreis'] for r in results if r['landkreis']]
    
    def get_schularten(self) -> List[str]:
        """Gibt alle verfügbaren Schularten zurück"""
        query = "SELECT DISTINCT schulart FROM einsatz WHERE schulart IS NOT NULL ORDER BY schulart"
        results = database.execute_query(query)
        return [r['schulart'] for r in results if r['schulart']]
