import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from pydantic import BaseModel, ConfigDict

from .loader import load_ccpa_sections
from .model import ComplianceLLM
from .retriever import CCPASectionRetriever
from .rules import detect_high_confidence_violation
from .utils import (
    build_llm_prompt,
    extract_allowed_sections,
    safe_output,
    validate_and_normalize_output,
)

logger = logging.getLogger("ccpa")
logging.basicConfig(level=logging.INFO)


class AnalyzeRequest(BaseModel):
    prompt: str
    model_config = ConfigDict(extra="forbid")


class AnalyzeResponse(BaseModel):
    harmful: bool
    articles: list[str]


@asynccontextmanager
async def lifespan(application: FastAPI):
    pdf_path = os.getenv("CCPA_PDF_PATH", "ccpa_statute.pdf")
    model_id = os.getenv("MODEL_ID", "microsoft/Phi-3-mini-4k-instruct")
    embedding_model = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    top_k = int(os.getenv("RETRIEVAL_TOP_K", "3"))

    sections = load_ccpa_sections(pdf_path)
    retriever = CCPASectionRetriever(sections=sections, embedding_model=embedding_model)
    llm = ComplianceLLM(model_id=model_id, hf_token=os.getenv("HF_TOKEN"))

    application.state.retriever = retriever
    application.state.llm = llm
    application.state.top_k = top_k

    logger.info("Startup complete: sections=%s top_k=%s model=%s", len(sections), top_k, model_id)
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/health", status_code=200)
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/analyze", response_model=AnalyzeResponse)
def analyze(request: AnalyzeRequest) -> AnalyzeResponse:
    try:
        rule_match = detect_high_confidence_violation(request.prompt)
        if rule_match is not None:
            return AnalyzeResponse(**rule_match)

        retrieved_sections = app.state.retriever.retrieve(request.prompt, k=app.state.top_k)
        llm_prompt = build_llm_prompt(request.prompt, retrieved_sections)
        raw_output = app.state.llm.generate(llm_prompt)

        allowed_sections = extract_allowed_sections(retrieved_sections)
        normalized = validate_and_normalize_output(raw_output, allowed_sections)
        return AnalyzeResponse(**normalized)
    except Exception:
        logger.exception("analyze_failed")
        return AnalyzeResponse(**safe_output())