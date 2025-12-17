import gc
from typing import List, Dict, Any
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi import HTTPException
from sentence_transformers import SentenceTransformer
import folketingetApi.controllers.auth as auth
import folketingetApi.controllers.saved_votings as saved_votings
from folketingetApi.services.search_service import get_model, fetch_similar_items_from_supabase, SearchRequest, startup_event

# --- Configuration ---
load_dotenv()  # Load environment variables

startup_event()

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

# Include other controller endpoints
app.include_router(auth.router)
app.include_router(saved_votings.router)

# --- API Endpoint ---


@app.post("/search", response_model=List[Dict[str, Any]])
async def search_similar_items(request_data: SearchRequest, model: SentenceTransformer = Depends(get_model)) -> List[Dict[str, Any]]:
    """
    Handles the end-to-end process: embeds the query and searches Supabase for similar items.
    """
    if model is None:
        raise HTTPException(
            status_code=503, detail="Embedding model not loaded")

    query_text = request_data.query_text
    match_count = request_data.match_count or 1000

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
        query_text=query_text,
        embedding=query_embedding,
        match_count=match_count,
        match_threshold=request_data.match_threshold
    )
    print(len(similar_items))
    # Return the results directly to the React Native app
    return similar_items

# uvicorn controllers.search:app --reload --host 0.0.0.0 --port 5001