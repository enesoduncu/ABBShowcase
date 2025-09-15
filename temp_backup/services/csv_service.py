import pandas as pd
import io
from typing import List, Dict, Any, Tuple
from datetime import datetime, date
import config

from schemas.abb import ABBCreate, ABBUpdate
from schemas.einsatz import EinsatzCreate, EinsatzUpdate
from schemas.abb_einsatz import ABBEinsatzCreate, ABBEinsatzUpdate
from schemas.common import CSVImportResult

class CSVService:
    """Service für CSV-Import und -Export"""
    
    @staticmethod
    def export_abb_to_csv(abbs: List[Dict[str, Any]], filters: Dict[str, Any] = None) -> bytes:
        """Exportiert ABB-Daten als CSV"""
        data = []
        
        for abb in abbs:
            row = {
                'ID': abb.get('id', ''),
                'Name': abb.get('name', ''),
                'Beschreibung': abb.get('beschreibung', ''),
                'Kategorie': abb.get('kategorie', ''),
                'Status': abb.get('status', ''),
                'Erstellt am': abb.get('erstellt_am', ''),
                'Aktualisiert am': abb.get('aktualisiert_am', '')
            }
            data.append(row)
        
        df = pd.DataFrame(data)
        
        # CSV in Bytes konvertieren
        output = io.BytesIO()
        df.to_csv(output, index=False, sep=config.CSV_DELIMITER, encoding=config.CSV_ENCODING)
        output.seek(0)
        
        return output.getvalue()
    
    @staticmethod
    def export_einsatz_to_csv(einsaetze: List[Dict[str, Any]], filters: Dict[str, Any] = None) -> bytes:
        """Exportiert Einsatz-Daten als CSV"""
        data = []
        
        for einsatz in einsaetze:
            row = {
                'ID': einsatz.get('id', ''),
                'Name': einsatz.get('name', ''),
                'Beschreibung': einsatz.get('beschreibung', ''),
                'Start Datum': einsatz.get('start_datum', ''),
                'End Datum': einsatz.get('end_datum', ''),
                'Status': einsatz.get('status', ''),
                'Priorität': einsatz.get('prioritaet', ''),
                'Erstellt am': einsatz.get('erstellt_am', ''),
                'Aktualisiert am': einsatz.get('aktualisiert_am', '')
            }
            data.append(row)
        
        df = pd.DataFrame(data)
        
        # CSV in Bytes konvertieren
        output = io.BytesIO()
        df.to_csv(output, index=False, sep=config.CSV_DELIMITER, encoding=config.CSV_ENCODING)
        output.seek(0)
        
        return output.getvalue()
    
    @staticmethod
    def export_abb_einsatz_to_csv(links: List[Dict[str, Any]], filters: Dict[str, Any] = None) -> bytes:
        """Exportiert ABB-Einsatz-Verknüpfungen als CSV"""
        data = []
        
        for link in links:
            row = {
                'ID': link.get('id', ''),
                'ABB ID': link.get('abb_id', ''),
                'ABB Name': link.get('abb_name', ''),
                'Einsatz ID': link.get('einsatz_id', ''),
                'Einsatz Name': link.get('einsatz_name', ''),
                'Zuordnungs Datum': link.get('zuordnungs_datum', ''),
                'Notizen': link.get('notizen', '')
            }
            data.append(row)
        
        df = pd.DataFrame(data)
        
        # CSV in Bytes konvertieren
        output = io.BytesIO()
        df.to_csv(output, index=False, sep=config.CSV_DELIMITER, encoding=config.CSV_ENCODING)
        output.seek(0)
        
        return output.getvalue()
    
    @staticmethod
    def import_abb_from_csv(file_content: bytes) -> CSVImportResult:
        """Importiert ABB-Daten aus CSV"""
        try:
            # CSV einlesen
            df = pd.read_csv(
                io.BytesIO(file_content),
                sep=config.CSV_DELIMITER,
                encoding=config.CSV_ENCODING
            )
            
            total_rows = len(df)
            imported_rows = 0
            errors = []
            warnings = []
            
            # Spalten-Mapping (deutsche Spaltennamen zu englischen)
            column_mapping = {
                'Name': 'name',
                'Beschreibung': 'beschreibung',
                'Kategorie': 'kategorie',
                'Status': 'status'
            }
            
            # Spalten umbenennen
            df = df.rename(columns=column_mapping)
            
            # Daten validieren und konvertieren
            for index, row in df.iterrows():
                try:
                    # Pflichtfelder prüfen
                    required_fields = ['name']
                    for field in required_fields:
                        if field not in row or pd.isna(row[field]):
                            errors.append({
                                'row': index + 1,
                                'field': field,
                                'value': '',
                                'error': f'Pflichtfeld fehlt: {field}'
                            })
                            continue
                    
                    imported_rows += 1
                    
                except Exception as e:
                    errors.append({
                        'row': index + 1,
                        'field': 'all',
                        'value': str(row),
                        'error': f'Allgemeiner Fehler: {str(e)}'
                    })
            
            success = len(errors) == 0
            
            return CSVImportResult(
                success=success,
                total_rows=total_rows,
                imported_rows=imported_rows,
                errors=errors,
                warnings=warnings
            )
            
        except Exception as e:
            return CSVImportResult(
                success=False,
                total_rows=0,
                imported_rows=0,
                errors=[{
                    'row': 0,
                    'field': 'file',
                    'value': '',
                    'error': f'Datei konnte nicht gelesen werden: {str(e)}'
                }]
            )
    
    @staticmethod
    def import_einsatz_from_csv(file_content: bytes) -> CSVImportResult:
        """Importiert Einsatz-Daten aus CSV"""
        try:
            # CSV einlesen
            df = pd.read_csv(
                io.BytesIO(file_content),
                sep=config.CSV_DELIMITER,
                encoding=config.CSV_ENCODING
            )
            
            total_rows = len(df)
            imported_rows = 0
            errors = []
            warnings = []
            
            # Spalten-Mapping
            column_mapping = {
                'Name': 'name',
                'Beschreibung': 'beschreibung',
                'Start Datum': 'start_datum',
                'End Datum': 'end_datum',
                'Status': 'status',
                'Priorität': 'prioritaet'
            }
            
            # Spalten umbenennen
            df = df.rename(columns=column_mapping)
            
            # Daten validieren und konvertieren
            for index, row in df.iterrows():
                try:
                    # Datum-Felder konvertieren
                    for date_field in ['start_datum', 'end_datum']:
                        if date_field in row and pd.notna(row[date_field]):
                            try:
                                if isinstance(row[date_field], str):
                                    # Verschiedene Datumsformate unterstützen
                                    for fmt in ['%d.%m.%Y', '%Y-%m-%d', '%d.%m.%y', '%d/%m/%Y']:
                                        try:
                                            row[date_field] = datetime.strptime(row[date_field], fmt).date()
                                            break
                                        except ValueError:
                                            continue
                                    else:
                                        raise ValueError(f"Ungültiges Datumsformat: {row[date_field]}")
                            except Exception as e:
                                errors.append({
                                    'row': index + 1,
                                    'field': date_field,
                                    'value': row[date_field],
                                    'error': f"Ungültiges Datum: {str(e)}"
                                })
                                continue
                    
                    # Pflichtfelder prüfen
                    required_fields = ['name']
                    for field in required_fields:
                        if field not in row or pd.isna(row[field]):
                            errors.append({
                                'row': index + 1,
                                'field': field,
                                'value': '',
                                'error': f'Pflichtfeld fehlt: {field}'
                            })
                            continue
                    
                    imported_rows += 1
                    
                except Exception as e:
                    errors.append({
                        'row': index + 1,
                        'field': 'all',
                        'value': str(row),
                        'error': f'Allgemeiner Fehler: {str(e)}'
                    })
            
            success = len(errors) == 0
            
            return CSVImportResult(
                success=success,
                total_rows=total_rows,
                imported_rows=imported_rows,
                errors=errors,
                warnings=warnings
            )
            
        except Exception as e:
            return CSVImportResult(
                success=False,
                total_rows=0,
                imported_rows=0,
                errors=[{
                    'row': 0,
                    'field': 'file',
                    'value': '',
                    'error': f'Datei konnte nicht gelesen werden: {str(e)}'
                }]
            )
