"""
main.py
-------
FastAPI service exposing the Fake News Detector ML model.

Run locally:
    pip install -r requirements.txt
    uvicorn main:app --host 0.0.0.0 --port 5000 --reload

Endpoints:
    GET  /            -> service metadata
    GET  /health       -> health check
    POST /predict      -> { "text": "..." } -> label + confidence + probabilities
    POST /reload-model  -> forces model retraining (for demo/admin use)
"""

from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

import model as ml_model

app = FastAPI(
    title="Fake News Detector - ML Service",
    description="TF-IDF + Logistic Regression text classification service for fake news detection.",
    version="1.0.0",
)

# Allow the Java gateway (and, for local debugging, the React dev server) to call this API directly.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class PredictRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Article text or headline to analyze")


class Probabilities(BaseModel):
    REAL: float
    FAKE: float


class PredictResponse(BaseModel):
    label: str
    confidence: float
    probabilities: Probabilities
    timestamp: str


@app.get("/")
def root():
    return {
        "service": "fake-news-detector-ml",
        "status": "running",
        "model": "tfidf-logistic-regression",
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/predict", response_model=PredictResponse)
def predict(payload: PredictRequest):
    text = payload.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Text field cannot be empty")

    try:
        result = ml_model.predict(text)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:  # noqa: BLE001 - surface any unexpected inference error to the caller
        raise HTTPException(status_code=500, detail=f"Prediction failed: {exc}")

    return {
        "label": result["label"],
        "confidence": result["confidence"],
        "probabilities": result["probabilities"],
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.post("/reload-model")
def reload_model():
    ml_model.reload_model()
    return {"status": "model retrained and reloaded"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=5000, reload=True)
