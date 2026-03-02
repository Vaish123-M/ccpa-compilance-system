from fastapi import FastAPI
from pydantic import BaseModel
from retriever import load_ccpa_sections, CCPAIndex
from model import LLM
import os
import json

app = FastAPI()

class RequestBody(BaseModel):
    prompt: str

# Startup loading
sections = load_ccpa_sections("ccpa_statute.pdf")
index = CCPAIndex(sections)
llm = LLM()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/analyze")
def analyze(request: RequestBody):

    retrieved = index.retrieve(request.prompt, k=3)
    prompt = build_prompt(request.prompt, retrieved)

    output = llm.generate(prompt)

    # Extract JSON safely
    try:
        json_start = output.index("{")
        json_str = output[json_start:]
        result = json.loads(json_str)
    except:
        result = {"harmful": False, "articles": []}

    return result