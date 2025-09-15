from sqlalchemy import Column, Integer, String, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin

class ABBEinsatz(Base, TimestampMixin):
    """Verknüpfung zwischen ABB und Einsätzen (Many-to-Many)"""
    __tablename__ = "abb_einsatz"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    abb_id = Column(Integer, ForeignKey("abb.id", ondelete="CASCADE"), nullable=False)
    einsatz_id = Column(Integer, ForeignKey("einsatz.id", ondelete="CASCADE"), nullable=False)
    rolle = Column(String(100), nullable=True)  # z.B. "Lead", "Co"
    kommentar = Column(Text, nullable=True)
    
    # Beziehungen
    abb = relationship("ABB", back_populates="einsaetze")
    einsatz = relationship("Einsatz", back_populates="abbs")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('abb_id', 'einsatz_id', name='uq_abb_einsatz'),
    )
    
    def __repr__(self):
        return f"<ABBEinsatz(abb_id={self.abb_id}, einsatz_id={self.einsatz_id}, rolle='{self.rolle}')>"
    
    @property
    def abb_name(self):
        """Name des ABB für die Anzeige"""
        if self.abb:
            return self.abb.vollname
        return f"ABB ID {self.abb_id}"
    
    @property
    def einsatz_info(self):
        """Einsatz-Informationen für die Anzeige"""
        if self.einsatz:
            return f"{self.einsatz.schulname} - {self.einsatz.formatierter_datum}"
        return f"Einsatz ID {self.einsatz_id}"
