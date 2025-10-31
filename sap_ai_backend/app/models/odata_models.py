from pydantic import BaseModel
from typing import Dict, Any, Optional

class ODataRequest(BaseModel):
    service_name: str
    entity_name: str
    filters: Optional[Dict[str, Any]] = None
    fields: Optional[list[str]] = None

class ODataResponse(BaseModel):
    data: Dict[str, Any]
    message: str