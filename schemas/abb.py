from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime
from schemas.common import BaseResponse

class ABBCreate(BaseModel):
    """Schema für das Erstellen eines ABB"""
    laufnummer: Optional[int] = None
    aktiv: bool = True
    vorname: str = Field(..., min_length=1, max_length=100)
    nachname: str = Field(..., min_length=1, max_length=100)
    geschlecht: Optional[str] = Field(None, regex='^(m|w|d)$')
    geburtsdatum: Optional[date] = None
    schulabschluss: Optional[str] = Field(None, max_length=100)
    vorbildung: Optional[str] = Field(None, max_length=200)
    studienabbrecher: bool = False
    beruf: Optional[str] = Field(None, max_length=100)
    zq: Optional[str] = Field(None, max_length=100)
    bereich: str = Field(..., regex='^(IHK|HWK|sonstiges)$')
    ausbildungsbeginn: Optional[date] = None
    ausbildungsende: Optional[date] = None
    schulungsdatum: Optional[date] = None
    mobilnummer: Optional[str] = Field(None, max_length=20)
    email_beruf: Optional[str] = Field(None, max_length=100)
    email_privat: Optional[str] = Field(None, max_length=100)
    telefon_beruf: Optional[str] = Field(None, max_length=20)
    telefon_privat: Optional[str] = Field(None, max_length=20)
    direktkontakt: bool = False
    betrieb: Optional[str] = Field(None, max_length=200)
    betriebadresse: Optional[str] = Field(None, max_length=500)
    landkreis_betrieb: Optional[str] = Field(None, max_length=100)
    asp_name: Optional[str] = Field(None, max_length=100)
    asp_telefon: Optional[str] = Field(None, max_length=20)
    asp_email: Optional[str] = Field(None, max_length=100)
    eindruck: Optional[str] = Field(None, max_length=1000)
    hinweise: Optional[str] = Field(None, max_length=1000)

class ABBUpdate(BaseModel):
    """Schema für das Aktualisieren eines ABB"""
    laufnummer: Optional[int] = None
    aktiv: Optional[bool] = None
    vorname: Optional[str] = Field(None, min_length=1, max_length=100)
    nachname: Optional[str] = Field(None, min_length=1, max_length=100)
    geschlecht: Optional[str] = Field(None, regex='^(m|w|d)$')
    geburtsdatum: Optional[date] = None
    schulabschluss: Optional[str] = Field(None, max_length=100)
    vorbildung: Optional[str] = Field(None, max_length=200)
    studienabbrecher: Optional[bool] = None
    beruf: Optional[str] = Field(None, max_length=100)
    zq: Optional[str] = Field(None, max_length=100)
    bereich: Optional[str] = Field(None, regex='^(IHK|HWK|sonstiges)$')
    ausbildungsbeginn: Optional[date] = None
    ausbildungsende: Optional[date] = None
    schulungsdatum: Optional[date] = None
    mobilnummer: Optional[str] = Field(None, max_length=20)
    email_beruf: Optional[str] = Field(None, max_length=100)
    email_privat: Optional[str] = Field(None, max_length=100)
    telefon_beruf: Optional[str] = Field(None, max_length=20)
    telefon_privat: Optional[str] = Field(None, max_length=20)
    direktkontakt: Optional[bool] = None
    betrieb: Optional[str] = Field(None, max_length=200)
    betriebadresse: Optional[str] = Field(None, max_length=500)
    landkreis_betrieb: Optional[str] = Field(None, max_length=100)
    asp_name: Optional[str] = Field(None, max_length=100)
    asp_telefon: Optional[str] = Field(None, max_length=20)
    asp_email: Optional[str] = Field(None, max_length=100)
    eindruck: Optional[str] = Field(None, max_length=1000)
    hinweise: Optional[str] = Field(None, max_length=1000)

class ABBResponse(BaseResponse):
    """Schema für die ABB-Response"""
    laufnummer: Optional[int]
    aktiv: bool
    vorname: str
    nachname: str
    geschlecht: Optional[str]
    geburtsdatum: Optional[date]
    schulabschluss: Optional[str]
    vorbildung: Optional[str]
    studienabbrecher: bool
    beruf: Optional[str]
    zq: Optional[str]
    bereich: str
    ausbildungsbeginn: Optional[date]
    ausbildungsende: Optional[date]
    schulungsdatum: Optional[date]
    mobilnummer: Optional[str]
    email_beruf: Optional[str]
    email_privat: Optional[str]
    telefon_beruf: Optional[str]
    telefon_privat: Optional[str]
    direktkontakt: bool
    betrieb: Optional[str]
    betriebadresse: Optional[str]
    landkreis_betrieb: Optional[str]
    asp_name: Optional[str]
    asp_telefon: Optional[str]
    asp_email: Optional[str]
    eindruck: Optional[str]
    hinweise: Optional[str]
    
    @property
    def vollname(self) -> str:
        """Vollständiger Name des ABB"""
        return f"{self.vorname} {self.nachname}"

class ABBFilter(BaseModel):
    """Filter für ABB-Suche"""
    aktiv: Optional[bool] = None
    bereich: Optional[str] = None
    landkreis_betrieb: Optional[str] = None
    suche: Optional[str] = None  # Suche in Vorname, Nachname, Beschreibung
