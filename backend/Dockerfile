FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV OLLAMA_MODEL=qwen3:1.7b

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
    "fastapi==0.137.1" \
    "uvicorn[standard]==0.49.0" \
    "chromadb==1.5.9" \
    "sentence-transformers==5.6.0" \
    "requests==2.34.2"

COPY backend ./backend
COPY data ./data

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
