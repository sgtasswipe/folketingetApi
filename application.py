import gc
import os
from typing import List, Dict, Any

from dotenv import load_dotenv

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
import auth

MODEL_PATH = "embedding_model/danishbert-supabase-embeddings-v3/danishbert-supabase-embeddings-v3"
# The API will use a regular synchronous function (def) for this endpoint,
# which FastAPI automatically runs in a thread pool to avoid blocking the event loop.
# Default is 40 threads for per worker - 40 concurrenct requests.


app = FastAPI(
    title="Sentence Transformer Embedding Service",
    description="Generates embeddings for input text using a fine-tuned Sentence Transformer model."
)

# Allow CORS for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust as needed for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

model: SentenceTransformer = None


@app.on_event("startup")
def startup_event():
    """Load the Sentence Transformer model on app startup."""
    global model
    print("Running script...")
    print(f"Loading SentenceTransformer model from: {MODEL_PATH}...")
    try:
        # Load the local fine-tuned model
        model = SentenceTransformer(MODEL_PATH)
        total_params = sum(p.numel() for p in model.parameters())
        print(f"Model loaded with {total_params} parameters.")
    except Exception as e:
        print(f"Error loading model: {e}")
        # Re-raise the exception
        # For simplicity here, we assume a successful load or the app will fail fast
        raise


app.include_router(auth.router)

# --- Pydantic Models ---


class EmbedRequest(BaseModel):
    """Schema for the incoming embedding request."""
    # Pydantic automatically validates that 'texts' is a list of strings
    texts: List[str]


class EmbedResponse(BaseModel):
    """Schema for the outgoing embedding response."""
    # The embeddings are returned as a list of lists (vectors)
    embeddings: List[List[float]]


# --- API ENDPOINT ---
@app.post("/embed", response_model=EmbedResponse)
def embed_text(request_data: EmbedRequest) -> Dict[str, Any]:
    """
    Generates embedding vectors for the provided list of texts.

    Since this is a synchronous function (def), FastAPI runs it in a background 
    thread to prevent the CPU-intensive operation from blocking the main event loop.
    """
    if model is None:
        raise HTTPException(
            status_code=503, detail="Embedding model not loaded")

    texts = request_data.texts
    print(f"this is text obj: {texts}")
    try:
        # (CPU-bound)
        embeddings = model.encode(texts)
        print(embeddings.shape)  # output dimension size
        response = {"embeddings": embeddings}

        del embeddings
        gc.collect()

        return response

    except Exception as e:
        print(f"Encoding error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred during embedding generation: {str(e)}"
        )

# fetch_similiar_items  rpc call on supabase


# uvicorn application:app --reload --host 0.0.0.0 --port 5001
# used for running the script

# fetch similar items
