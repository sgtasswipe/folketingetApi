from pydantic import BaseModel, Field
from typing import Optional, List
from starlette.concurrency import run_in_threadpool
from fastapi import HTTPException
from sentence_transformers import SentenceTransformer
from folketingetApi.repositories.search_repository import fetch_similar_items
from typing import Dict, Any

MODEL_PATH = "folketingetApi/embedding_model/danishbert-cosine-embeddings"
model: Optional[SentenceTransformer] = None

# --- Pydantic Models ---

def startup_event():
    """Load the Sentence Transformer model on app startup."""
    global model
    print("Running script...")
    print(f"Loading SentenceTransformer model from: {MODEL_PATH}...")
    try:
        model = SentenceTransformer(MODEL_PATH)
        total_params = sum(p.numel() for p in model.parameters())
        print(f"Model loaded with {total_params} parameters.")
        print(f"Deployed via workflow file")
    except Exception as e:
        print(f"Error loading model: {e}")
        raise

class SearchRequest(BaseModel):
    """Schema for the incoming search request."""
    query_text: str = Field(...,
                            # ... =  "ellipsis" value used for explicitly stating the field is required.
                            description="The text query to be embedded and searched.")
    # not needed as no default value also means required, but stated expilicitly as the query need a str to embed.
    match_count: Optional[int] = Field(
        None, description="The maximum number of similar items to return. If no explicit value is specified, will return all above match_threshold")
    match_threshold: float = Field(
        0.5, description="The minimum similarity score for a match.")

# --- Supabase Search Function (Async) ---

async def fetch_similar_items_from_supabase(query_text: str, embedding: List[float], match_count: int, match_threshold: float) -> List[Dict[str, Any]]:
    """
    Connects to Supabase and calls the 'fetch_similar_items' RPC function.
    """
    try:
        # Parameters for the Supabase RPC function
        params = {
            "query_text": query_text,
            "query_embedding": embedding,
            "match_count": match_count,
            "match_threshold": match_threshold,
        }

        response = await run_in_threadpool(
            fetch_similar_items(params)
        )
        print(response)
        print(response.data)
        return response.data
        # The data property contains the result from the RPC call. This will be returned to caller.

    except Exception as e:
        print(f"Supabase RPC error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred during Supabase similarity search: {str(e)}"
        )

def get_model():
    if model is None:
        raise RuntimeError("Model not loaded")
    return model