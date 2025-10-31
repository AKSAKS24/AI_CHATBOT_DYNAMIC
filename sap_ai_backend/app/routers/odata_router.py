from fastapi import APIRouter, HTTPException
from app.models.odata_models import ODataRequest
from app.services.odata_service import get_odata_data
from app.core.logger import get_logger

router = APIRouter(prefix="/odata", tags=["OData"])
logger = get_logger(__name__)

@router.post("/fetch")
async def fetch_odata(request: ODataRequest):
    try:
        result = await get_odata_data(
            request.service_name,
            request.entity_name,
            request.filters,
            request.fields,
        )
        return {"data": result}
    except Exception as e:
        logger.exception("OData fetch failed.")
        raise HTTPException(status_code=500, detail=str(e))