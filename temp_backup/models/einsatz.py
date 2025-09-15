from sqlalchemy import Column, Integer, String, Boolean, Date, Text, Index, Enum
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin
import enum

class SchulartEnum(enum.Enum):
    GYMNASIUM = "Gymnasium"
    REALSCHULE = "Realschule"
    HAUPTSCHULE = "Hauptschule"
    WERKREALSCHULE = "Werkrealschule"
    GEMEINSCHAFTSSCHULE = "Gemeinschaftsschule"
    BERUFSGESCHULE = "Berufsschule"
    BERUFSKOLLEG = "Berufskolleg"
    FACHOBERSCHULE = "Fachoberschule"
    BERUFSFACHSCHULE = "Berufsfachschule"
    FACHGYMNASIUM = "Fachgymnasium"
    GESAMTSCHULE = "Gesamtschule"
    ANDERE = "Andere"

class Einsatz(Base, TimestampMixin):
    """Schuleinsatz Model"""
    __tablename__ = "einsatz"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    einsatzdatum = Column(Date, nullable=False)
    schulname = Column(String(200), nullable=False)
    schulart = Column(Enum(SchulartEnum), nullable=False)
    partner = Column(String(200), nullable=True)
    stadt = Column(String(100), nullable=False)
    landkreis = Column(String(100), nullable=False)
    studienbotschafter = Column(Boolean, default=False, nullable=False)  # Studienbotschafter
    online = Column(Boolean, default=False, nullable=False)
    klassenstufe = Column(String(50), nullable=False)
    schueleranzahl = Column(Integer, nullable=False)
    
    # Beziehungen
    abbs = relationship("ABBEinsatz", back_populates="einsatz", cascade="all, delete-orphan")
    
    # Constraints
    __table_args__ = (
        Index('idx_einsatz_datum', 'einsatzdatum'),
        Index('idx_einsatz_landkreis', 'landkreis'),
        Index('idx_einsatz_schule', 'schulname'),
        Index('idx_einsatz_online', 'online'),
        Index('idx_einsatz_klassenstufe', 'klassenstufe'),
    )
    
    def __repr__(self):
        return f"<Einsatz(id={self.id}, schule='{self.schulname}', datum='{self.einsatzdatum}', schueler={self.schueleranzahl})>"
    
    @property
    def ist_online(self):
        """Gibt True zurück, wenn der Einsatz online stattfindet"""
        return self.online
    
    @property
    def hat_studienbotschafter(self):
        """Gibt True zurück, wenn Studienbotschafter vorhanden ist"""
        return self.studienbotschafter
    
    @property
    def formatierter_datum(self):
        """Formatiertes Datum für die Anzeige"""
        from datetime import datetime
        if self.einsatzdatum:
            return self.einsatzdatum.strftime("%d.%m.%Y")
        return ""
    
    @property
    def abbs_anzahl(self):
        """Anzahl der zugeordneten ABB"""
        return len(self.abbs)
    
    @property
    def anzahl_einsaetze(self):
        """Berechnet die Anzahl der Einsätze basierend auf der Schüleranzahl (max. 25 pro Einsatz)"""
        if self.schueleranzahl <= 25:
            return 1
        else:
            # Aufrunden bei Rest - bei 75 Schülern = 3 Einsätze (25+25+25)
            return (self.schueleranzahl + 24) // 25
