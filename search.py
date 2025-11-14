import gc
import os
from typing import List, Dict, Any, Optional

from dotenv import load_dotenv
from util.supabase_client_creator import get_supabase_client
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sentence_transformers import SentenceTransformer
from starlette.concurrency import run_in_threadpool
import asyncio
import auth

# --- Configuration ---
load_dotenv()  # Load environment variables
MODEL_PATH = "embedding_model/danishbert-cosine-embeddings"

# --- FastAPI App Setup ---
app = FastAPI(
    title="Sentence Transformer Embedding Service",
    description="Generates embeddings and performs similarity search via Supabase."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for production!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

model: Optional[SentenceTransformer] = None


@app.on_event("startup")
def startup_event():
    """Load the Sentence Transformer model on app startup."""
    global model
    print("Running script...")
    print(f"Loading SentenceTransformer model from: {MODEL_PATH}...")
    try:
        model = SentenceTransformer(MODEL_PATH)
        total_params = sum(p.numel() for p in model.parameters())
        print(f"Model loaded with {total_params} parameters.")
    except Exception as e:
        print(f"Error loading model: {e}")
        raise


app.include_router(auth.router)

# --- Pydantic Models ---


class SearchRequest(BaseModel):
    """Schema for the incoming search request."""
    query_text: str = Field(...,
                            # ... =  "ellipsis" value used for explicitly stating the field is required.
                            description="The text query to be embedded and searched.")
    # not needed as no default value also means required, but stated expilicitly as the query need a str to embed.
    match_count: int = Field(
        10, description="The maximum number of similar items to return.")
    match_threshold: float = Field(
        0.5, description="The minimum similarity score for a match.")


# --- Supabase Search Function (Async) ---

async def fetch_similar_items_from_supabase(embedding: List[float], match_count: int, match_threshold: float) -> List[Dict[str, Any]]:
    """
    Connects to Supabase and calls the 'fetch_similar_items' RPC function.
    """
    try:
        supabase = get_supabase_client()

        # Parameters for the Supabase RPC function
        params = {
            "query_embedding": embedding,
            "match_count": match_count,
            "match_threshold": match_threshold,
        }

        response = await run_in_threadpool(
            supabase.rpc("fetch_similar_items", params).execute
        )

        return response.data
        # The data property contains the result from the RPC call. This will be returned to caller.

    except Exception as e:
        print(f"Supabase RPC error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred during Supabase similarity search: {str(e)}"
        )


# --- API Endpoint ---

@app.post("/search", response_model=List[Dict[str, Any]])
async def search_similar_items(request_data: SearchRequest) -> List[Dict[str, Any]]:
    """
    Handles the end-to-end process: embeds the query and searches Supabase for similar items.
    """
    if model is None:
        raise HTTPException(
            status_code=503, detail="Embedding model not loaded")

    query_text = request_data.query_text

    try:
        # Note: model.encode returns a numpy array for a list of texts (even one text)
        # We take the first (and only) embedding vector and convert it to a list of floats
        embedding_array = model.encode([query_text])[0]
        print(type(model.encode([query_text])))
        query_embedding: List[float] = embedding_array.tolist()

        # Clean up memory
        del embedding_array
        gc.collect()

    except Exception as e:
        print(f"Encoding error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred during embedding generation: {str(e)}"
        )

    # Search Supabase (I/O-bound, so we must await the async function)
    # The result will be a list of dicts (votings with titel, id etc.)
    similar_items = await fetch_similar_items_from_supabase(
        embedding=query_embedding,
        match_count=request_data.match_count,
        match_threshold=request_data.match_threshold
    )

    # 3. Return the results directly to the React Native app
    return similar_items
# uvicorn search:app --reload --host 0.0.0.0 --port 5001