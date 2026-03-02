FROM pytorch/pytorch:2.4.1-cuda12.1-cudnn9-runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
	PYTHONUNBUFFERED=1 \
	PIP_NO_CACHE_DIR=1 \
	DEBIAN_FRONTEND=noninteractive \
	HF_HOME=/opt/hf-cache \
	CCPA_PDF_PATH=ccpa_statute.pdf \
	RETRIEVAL_TOP_K=3

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
	libgomp1 \
	&& rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

ARG HF_TOKEN=""
ARG MODEL_ID="microsoft/Phi-3-mini-4k-instruct"
ARG EMBEDDING_MODEL="sentence-transformers/all-MiniLM-L6-v2"

ENV HF_TOKEN=${HF_TOKEN}
ENV MODEL_ID=${MODEL_ID}
ENV EMBEDDING_MODEL=${EMBEDDING_MODEL}



COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]