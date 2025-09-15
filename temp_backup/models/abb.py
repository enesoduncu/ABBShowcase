from sqlalchemy import Column, Integer, String, Boolean, Date, Text, Enum, UniqueConstraint, Index
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin
import enum

class BereichEnum(enum.Enum):
    IHK = "IHK"
    HWK = "HWK"
    SONSTIGES = "sonstiges"

class GeschlechtEnum(enum.Enum):
    M = "M"
    W = "W"
    D = "D"

class SchulabschlussEnum(enum.Enum):
    HAUPTSCHULABSCHLUSS = "Hauptschulabschluss"
    REALSCHULABSCHLUSS = "Realschulabschluss"
    MITTLERE_REIFE = "Mittlere Reife"
    FACHHOCHSCHULREIFE = "Fachhochschulreife"
    ABITUR = "Abitur"
    FACHABITUR = "Fachabitur"
    OHNE_ABSCHLUSS = "Ohne Abschluss"
    ANDERER = "Anderer Abschluss"

class StudiumStatusEnum(enum.Enum):
    KEIN_STUDIUM = "Kein Studium"
    STUDIUM_ABGESCHLOSSEN = "Studium abgeschlossen"
    STUDIUM_ABGEBROCHEN = "Studium abgebrochen"
    STUDIUM_LAUFEND = "Studium läuft noch"

class ABB(Base, TimestampMixin):
    """Ausbildungsbotschafter Model"""
    __tablename__ = "abb"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    laufnummer = Column(String(50), unique=True, nullable=True)
    aktiv = Column(Boolean, default=True, nullable=False)
    vorname = Column(String(100), nullable=False)
    nachname = Column(String(100), nullable=False)
    geschlecht = Column(Enum(GeschlechtEnum), nullable=False)
    geburtsdatum = Column(Date, nullable=False)
    schulabschluss = Column(Enum(SchulabschlussEnum), nullable=True)
    vorbildung = Column(String(200), nullable=True)
    studium_status = Column(Enum(StudiumStatusEnum), nullable=True)
    studium_fach = Column(String(200), nullable=True)  # Welches Studium abgebrochen/abgeschlossen
    beruf = Column(String(100), nullable=False)
    zq = Column(String(100), nullable=True)
    bereich = Column(Enum(BereichEnum), nullable=False)
    ausbildungsbeginn = Column(Date, nullable=False)
    ausbildungsende = Column(Date, nullable=True)
    schulungsdatum = Column(Date, nullable=True)
    mobilnummer = Column(String(20), nullable=True)
    email_beruf = Column(String(200), nullable=True)
    email_privat = Column(String(200), nullable=True)
    telefon_beruf = Column(String(20), nullable=True)
    telefon_privat = Column(String(20), nullable=True)
    direktkontakt = Column(Boolean, default=False, nullable=False)
    betrieb = Column(String(200), nullable=True)
    betriebadresse = Column(String(300), nullable=True)
    landkreis_betrieb = Column(String(100), nullable=True)
    asp_name = Column(String(200), nullable=True)
    asp_telefon = Column(String(20), nullable=True)
    asp_email = Column(String(200), nullable=True)
    notizen = Column(Text, nullable=True)  # Notizen für Koordinator*innen
    hinweise = Column(Text, nullable=True)
    
    # Beziehungen
    einsaetze = relationship("ABBEinsatz", back_populates="abb", cascade="all, delete-orphan")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('vorname', 'nachname', 'geburtsdatum', name='uq_abb_person'),
        Index('idx_abb_aktiv', 'aktiv'),
        Index('idx_abb_bereich', 'bereich'),
        Index('idx_abb_landkreis', 'landkreis_betrieb'),
        Index('idx_abb_ausbildungsbeginn', 'ausbildungsbeginn'),
    )
    
    def __repr__(self):
        return f"<ABB(id={self.id}, name='{self.vorname} {self.nachname}', bereich='{self.bereich.value}')>"
    
    @property
    def vollname(self):
        """Vollständiger Name des ABB"""
        return f"{self.vorname} {self.nachname}"
    
    @property
    def alter(self):
        """Alter des ABB basierend auf Geburtsdatum"""
        from datetime import date
        if self.geburtsdatum:
            today = date.today()
            return today.year - self.geburtsdatum.year - ((today.month, today.day) < (self.geburtsdatum.month, self.geburtsdatum.day))
        return None
