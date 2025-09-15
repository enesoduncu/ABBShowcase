from pydantic import BaseModel, Field
from typing import Optional, List, Any, Dict
from datetime import datetime

class PaginationParams(BaseModel):
    """Parameter für Pagination"""
    page: int = Field(default=1, ge=1, description="Seitennummer")
    size: int = Field(default=25, ge=1, le=100, description="Seitengröße")
    
    @property
    def offset(self) -> int:
        """Offset für SQL-Query"""
        return (self.page - 1) * self.size

class CSVImportResult(BaseModel):
    """Ergebnis eines CSV-Imports"""
    success: bool
    total_rows: int
    imported_rows: int
    errors: List[Dict[str, Any]] = []
    warnings: List[str] = []
    
    @property
    def error_count(self) -> int:
        """Anzahl der Fehler"""
        return len(self.errors)
    
    @property
    def warning_count(self) -> int:
        """Anzahl der Warnungen"""
        return len(self.warnings)

class BaseResponse(BaseModel):
    """Basis-Response-Model"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True
