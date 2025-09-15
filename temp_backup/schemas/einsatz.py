from pydantic import BaseModel, Field
from typing import Optional
from datetime import date
from .common import BaseResponse

class EinsatzCreate(BaseModel):
    """Schema für das Erstellen eines Einsatzes"""
    name: str = Field(..., min_length=1, max_length=200)
    beschreibung: Optional[str] = Field(None, max_length=500)
    start_datum: Optional[date] = None
    end_datum: Optional[date] = None
    status: Optional[str] = Field(None, max_length=50)
    prioritaet: Optional[str] = Field(None, max_length=50)
    # Neue Felder für detaillierte Einsatz-Verwaltung
    einsatzdatum: Optional[date] = None
    schulname: Optional[str] = Field(None, max_length=200)
    schulart: Optional[str] = Field(None, max_length=100)
    partner: Optional[str] = Field(None, max_length=200)
    stadt: Optional[str] = Field(None, max_length=100)
    landkreis: Optional[str] = Field(None, max_length=100)
    studienbotschafter: bool = False
    online: bool = False
    klassenstufe: Optional[str] = Field(None, max_length=50)
    schueleranzahl: Optional[int] = Field(None, ge=1)

class EinsatzUpdate(BaseModel):
    """Schema für das Aktualisieren eines Einsatzes"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    beschreibung: Optional[str] = Field(None, max_length=500)
    start_datum: Optional[date] = None
    end_datum: Optional[date] = None
    status: Optional[str] = Field(None, max_length=50)
    prioritaet: Optional[str] = Field(None, max_length=50)

class EinsatzResponse(BaseResponse):
    """Schema für die Einsatz-Response"""
    name: str
    beschreibung: Optional[str]
    start_datum: Optional[date]
    end_datum: Optional[date]
    status: Optional[str]
    prioritaet: Optional[str]

class EinsatzFilter(BaseModel):
    """Schema für Einsatz-Filter"""
    start_datum_von: Optional[date] = None
    start_datum_bis: Optional[date] = None
    name: Optional[str] = None
    beschreibung: Optional[str] = None
    status: Optional[str] = None
    prioritaet: Optional[str] = None

class EinsatzSplitRequest(BaseModel):
    """Schema für die Anfrage zum Aufteilen eines Einsatzes"""
    einsatz: EinsatzCreate
    schueleranzahl_gesamt: int = Field(..., gt=25, description="Gesamtanzahl der Schüler")
    
    @property
    def anzahl_einsaetze(self) -> int:
        """Berechnet die Anzahl der benötigten Einsätze"""
        import math
        return math.ceil(self.schueleranzahl_gesamt / 25)
    
    @property
    def einsaetze(self) -> list[EinsatzCreate]:
        """Erstellt die aufgeteilten Einsätze"""
        einsaetze = []
        rest = self.schueleranzahl_gesamt
        
        for i in range(self.anzahl_einsaetze):
            schueler_im_einsatz = min(25, rest)
            einsatz_data = self.einsatz.dict()
            einsatz_data['schueleranzahl'] = schueler_im_einsatz
            einsaetze.append(EinsatzCreate(**einsatz_data))
            rest -= schueler_im_einsatz
            
        return einsaetze
