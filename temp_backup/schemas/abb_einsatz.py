from pydantic import BaseModel, Field
from typing import Optional
from .common import BaseResponse

class ABBEinsatzCreate(BaseModel):
    """Schema für das Erstellen einer ABB-Einsatz-Verknüpfung"""
    abb_id: int = Field(..., gt=0)
    einsatz_id: int = Field(..., gt=0)
    rolle: Optional[str] = Field(None, max_length=100)
    kommentar: Optional[str] = None

class ABBEinsatzUpdate(BaseModel):
    """Schema für das Aktualisieren einer ABB-Einsatz-Verknüpfung"""
    rolle: Optional[str] = Field(None, max_length=100)
    kommentar: Optional[str] = None

class ABBEinsatzResponse(BaseResponse):
    """Schema für die ABB-Einsatz-Response"""
    abb_id: int
    einsatz_id: int
    rolle: Optional[str]
    kommentar: Optional[str]
    
    # Beziehungsdaten (werden von den Services gefüllt)
    abb_name: Optional[str] = None
    einsatz_info: Optional[str] = None
