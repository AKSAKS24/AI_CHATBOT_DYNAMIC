from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from app.core.config import settings
from app.core.logger import get_logger
import json

logger = get_logger(__name__)

# --- Helper to instantiate models ---
def get_llm():
    return OpenAI(
        temperature=0.2,
        openai_api_key=settings.openai_api_key,
        model_name=settings.model_name
    )

# --- Step 1. Translate user query to OData payload ---
def parse_nl_query(query: str, service_description: dict):
    logger.info("Interpreting natural language to OData JSON...")
    prompt = PromptTemplate(
        template=(
            "You are an assistant that converts natural-language questions "
            "into valid SAP OData JSON payloads.\n\n"
            "Allowed metadata:\n{service_description}\n\n"
            "User query: {query}\n\n"
            "Respond ONLY with well‑formed JSON:\n"
            "{"
            '"service_name": "...", '
            '"entity_name": "...", '
            '"fields": ["..."], '
            '"filters": {"Field": "Value"}'
            "}"
        ),
        input_variables=["service_description", "query"],
    )
    llm = get_llm()
    chain = LLMChain(llm=llm, prompt=prompt)
    result = chain.run(service_description=json.dumps(service_description, indent=2), query=query)
    try:
        payload = json.loads(result)
        return payload
    except json.JSONDecodeError as err:
        logger.error(f"LLM produced invalid JSON: {result}")
        raise ValueError("Invalid JSON returned by LLM") from err

# --- Step 2. Summarize API result naturally ---
def summarize_odata_result(query, odata_query_payload, data):
    logger.info("Generating natural language summary of SAP data.")
    prompt = PromptTemplate(
        template=(
            "You are an SAP data analyst.\n"
            "Question: {query}\n\n"
            "OData executed: {odata_query}\n\n"
            "Data:\n{data}\n\n"
            "Answer in plain English business language. "
            "Do not show JSON or technical fields; produce 1‑2 sentences summary."
        ),
        input_variables=["query", "odata_query", "data"],
    )
    llm = get_llm()
    chain = LLMChain(llm=llm, prompt=prompt)
    summary = chain.run(
        query=query,
        odata_query=json.dumps(odata_query_payload, indent=2),
        data=json.dumps(data, indent=2),
    )
    return summary.strip()