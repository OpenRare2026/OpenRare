FROM python:3.12-slim

WORKDIR /app

# ── Python dependencies (CPU-only torch to keep image small) ──
COPY requirements-docker.txt .
RUN pip install --no-cache-dir --extra-index-url https://download.pytorch.org/whl/cpu \
    -r requirements-docker.txt

# ── Pre-download embedding model (cached layer when dependencies don't change) ──
ARG EMBEDDING_MODEL="pritamdeka/SapBERT-mnli-snli-scinli-scitail-mednli-stsb"
ENV HF_HOME=/app/.cache/huggingface \
    EMBEDDING_MODEL=${EMBEDDING_MODEL}
RUN python -c "from sentence_transformers import SentenceTransformer; import os; \
    model = os.environ['EMBEDDING_MODEL']; \
    SentenceTransformer(model); \
    print(f'Model {model} cached.')"

# ── Application code ──
COPY dev/ dev/
COPY hp.obo hpo_meta.json hpo_embedded.npz hpo_terms_full.csv system_prompts.json ./

# ── Runtime ──
ENV HF_HOME=/app/.cache/huggingface \
    HF_HUB_OFFLINE=1 \
    TRANSFORMERS_OFFLINE=1
EXPOSE 8000
VOLUME ["/data"]
CMD ["uvicorn", "dev.server:app", "--host", "0.0.0.0", "--port", "8000"]
