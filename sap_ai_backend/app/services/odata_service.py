import httpx, json
from pathlib import Path
from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)
CONFIG_PATH = Path("config/odata_endpoints.json")

async def get_odata_data(service_name: str, entity_name: str, filters=None, fields=None):
    """Build dynamic OData URL and fetch data from SAP."""
    logger.info(f"Fetching SAP OData: service={service_name}, entity={entity_name}")

    if not CONFIG_PATH.exists():
        raise FileNotFoundError("Configuration file missing.")

    config = json.loads(CONFIG_PATH.read_text())

    if service_name not in config["Services"]:
        raise ValueError(f"Invalid service '{service_name}'")
    if entity_name not in config["Services"][service_name]["Entities"]:
        raise ValueError(f"Invalid entity '{entity_name}'")

    base_url = settings.sap_base_url.rstrip("/")
    odata_url = f"{base_url}/{service_name}/{entity_name}"

    params = []
    if filters:
        filter_str = " and ".join([f"{k} eq '{v}'" for k, v in filters.items()])
        params.append(f"$filter={filter_str}")
    if fields:
        select_str = ",".join(fields)
        params.append(f"$select={select_str}")

    query = "&".join(params)
    final_url = f"{odata_url}?{query}" if query else odata_url
    logger.debug(f"Final OData URL: {final_url}")

    async with httpx.AsyncClient(auth=(settings.sap_username, settings.sap_password)) as client:
        resp = await client.get(final_url)
        resp.raise_for_status()
        data = resp.json()

    logger.info(f"Data fetched for entity {entity_name}")
    return data