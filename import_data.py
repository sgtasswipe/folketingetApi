import requests
import json
import os
import time
import gc
from typing import List, Dict, Any
import torch  # Import torch for GPU detection and management
from util.supabase_client_creator import get_supabase_client
from starlette.concurrency import run_in_threadpool
import asyncio
from huggingface_hub import snapshot_download

from dotenv import load_dotenv
from supabase.client import create_client, Client
from sentence_transformers import SentenceTransformer

HF_TOKEN = os.environ.get("HF_TOKEN")

os.makedirs("embedding_model", exist_ok=True)

snapshot_download(
    repo_id="heizetagram/danishbert-cosine-embeddings",
    local_dir="embedding_model",
    local_dir_use_symlinks=False,
    use_auth_token=True
)

# CUDA GPU CHECKS
print(f"CUDA Available: {torch.cuda.is_available()}")
print(f"PyTorch CUDA Version: {torch.version.cuda}")
if torch.cuda.is_available():
    print(f"Detected GPU: {torch.cuda.get_device_name(0)}")
if torch.cuda.is_available():
    device = torch.device("cuda")
    x = torch.ones(5, device=device)
    print(f"Test Tensor Device: {x.device}")

# --- Configuration ---
load_dotenv()
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
# Assumes you have the model locally
MODEL_PATH = "embedding_model/danishbert-cosine-embeddings"
API_BASE_URL = "https://oda.ft.dk/api/Afstemning"
BATCH_SIZE = 100  # Size of each upload batch to Supabase
TARGET_TABLE = "afstemninger_bert_v2"  # The new table

# OData Query to fetch all votes of type 1 or 3
# We expand Sagstrin and Sag to get title, resume, and afstemningskonklusion
API_QUERY = f"{API_BASE_URL}?$inlinecount=allpages&$orderby=opdateringsdato desc&$expand=Sagstrin,Sagstrin/Sag &$filter=(typeid eq 1 or typeid eq 3)"

# --- Initialization ---
try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("Supabase client created.")
except Exception as e:
    print(f"Error creating Supabase client: {e}")
    exit(1)

# Determine the device for computation (GPU if available, otherwise CPU)
if torch.cuda.is_available():
    DEVICE = "cuda"
    # Using torch.cuda.get_device_name(0) to confirm which GPU is used
    print(f"CUDA is available. Using GPU: {torch.cuda.get_device_name(0)}")
elif torch.backends.mps.is_available():
    DEVICE = "mps"
    print("MPS (Apple Silicon) is available. Using MPS.")
else:
    DEVICE = "cpu"
    print("CUDA/MPS not available. Falling back to CPU.")
    print(f"Model path: {MODEL_PATH}")

try:
    # Load the Sentence Transformer model and explicitly assign the device
    # This moves the model weights to the GPU for processing
    model = SentenceTransformer(MODEL_PATH, device=DEVICE)
    print(
        f"Embedding model loaded from: {MODEL_PATH} and assigned to {DEVICE}.")
except Exception as e:
    print(f"Error loading model on {DEVICE}: {e}")
    # Note: If the model fails to load on 'cuda' or 'mps',
    # you might try reloading it with 'cpu' as a fallback here.
    exit(1)


# --- Functions ---

async def get_latest_voting_date_from_db():
    supabase = get_supabase_client()

    response = await run_in_threadpool(
        lambda: supabase.rpc("fetch_latest_voting", {"tbl_name": TARGET_TABLE}).execute()
    )

    return response.data

def fetch_all_afstemninger(latest_result) -> List[Dict[str, Any]]:
    all_records = []
    skip = 0
    total_count = None

    print("Starting data retrieval from the Folketing API...")

    while True:
        url = f"{API_QUERY}&$skip={skip}"

        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.RequestException as e:
            print(f"API Error at skip={skip}: {e}")
            break

        if total_count is None:
            total_count = int(data.get('odata.count', 0))
            print(f"Found a total of {total_count} votes to fetch.")
        
        records = data.get('value', [])

        if not records:
            break

        if latest_result:
            filtered_records = []
            latest_date = latest_result[0]['afstemning_dato']
            for record in records:
                record_date = record.get('Sagstrin', {}).get('dato')
                if record_date and record_date > latest_date:
                    filtered_records.append(record)
            
            if not filtered_records:
                break
            
            all_records.extend(filtered_records)
        else:
            all_records.extend(records)

        skip += len(records)

        print(f"Fetched {skip}/{total_count} records...")

        if len(records) < 100 or skip >= total_count:
            break

    print(f"Retrieval complete. Total records: {len(all_records)}")
    return all_records

def prepare_and_embed_data(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Prepares data and generates embeddings."""
    processed_records = []
    texts_to_embed = []

    print("Starting data preparation and embedding...")

    for record in records:
        sagstrin = record.get('Sagstrin', {})
        sag = sagstrin.get('Sag', {})

        # 1. Extract relevant fields
        afstemning_id = record.get('id')
        konklusion_afstemning = record.get('konklusion', '')
        sag_id = sag.get('id')
        titel = sag.get('titel', '')
        titelkort = sag.get('titelkort', '')
        resume = sag.get('resume', '')
        opdateringsdato = record.get('opdateringsdato')

        # NEW FIELDS ADDED
        afstemning_dato = sagstrin.get('dato')       # Date from Sagstrin
        sagstrin_titel = sagstrin.get('titel', '')   # Title from Sagstrin
        vedtaget = record.get('vedtaget')            # Boolean from Afstemning

        # 2. Combine text fields for embedding
        embedding_text = f"{titel}. {titelkort}. {resume}."

        texts_to_embed.append(embedding_text)

        # Store the pre-processed data (without embedding yet)
        processed_records.append({
            'afstemning_id': afstemning_id,
            'sag_id': sag_id,
            'titel': titel,
            'titelkort': titelkort,
            'resume': resume,
            'konklusion': konklusion_afstemning,

            # NEW FIELDS ADDED HERE
            'afstemning_dato': afstemning_dato,
            'sagstrin_titel': sagstrin_titel,
            'vedtaget': vedtaget,

            'opdateringsdato': opdateringsdato,
            'embedding_text': embedding_text,
            'embedding_v5': None  # Placeholder
        })

    # 3. Generate embeddings
    # IMPORTANT: Pass the determined DEVICE to ensure the GPU is used for encoding
    try:
        embeddings = model.encode(
            texts_to_embed, show_progress_bar=True, device=DEVICE)
    except Exception as e:
        print(f"Error during embedding: {e}")
        return []

    # 4. Assign embeddings to records
    for i, embedding in enumerate(embeddings):
        # Convert numpy array to standard Python list of floats
        processed_records[i]['embedding_v5'] = embedding.tolist()

    print("Embedding complete.")
    del embeddings, texts_to_embed
    gc.collect()  # Free up memory
    if DEVICE.startswith('cuda'):
        torch.cuda.empty_cache()  # Clear GPU memory cache

    return processed_records


def save_to_supabase_in_batches(data: List[Dict[str, Any]]):
    """Saves the prepared data to Supabase in batches."""
    total_records = len(data)

    print(f"Starting upload to Supabase in batches of {BATCH_SIZE}...")

    for i in range(0, total_records, BATCH_SIZE):
        batch = data[i:i + BATCH_SIZE]

        try:
            # Upsert ensures existing records (same afstemning_id) are updated
            response = supabase.table(TARGET_TABLE).upsert(
                batch,
                on_conflict='afstemning_id'
            ).execute()

            # Check for errors in response
            if response.data is None or 'error' in response.data:
                print(
                    f"Error in Supabase batch {i//BATCH_SIZE + 1}: {response.data}")

            print(
                f"Uploaded batch {i // BATCH_SIZE + 1}. Records saved: {len(batch)}.")

        except Exception as e:
            print(
                f"Critical error during Supabase upload of batch {i//BATCH_SIZE + 1}: {e}")

        time.sleep(1)  # Wait 1 second between batches to avoid rate-limiting

    print("Upload to Supabase finished.")


# --- Main Execution ---
if __name__ == "__main__":
    start_time = time.time()

    latest_result = asyncio.run(get_latest_voting_date_from_db())
    if latest_result and 'afstemning_dato' in latest_result[0] and latest_result[0]['afstemning_dato']:
        print(f"Latest voting date found in DB: {latest_result[0]['afstemning_dato']}")
    else:
        print("No voting date found in DB")

    # 1. Fetch all votes
    all_afstemninger = fetch_all_afstemninger(latest_result)

    if all_afstemninger:
        # 2. Prepare data and generate embeddings
        embedded_data = prepare_and_embed_data(all_afstemninger)

        # 3. Save to Supabase in batches
        if embedded_data:
            save_to_supabase_in_batches(embedded_data)

    end_time = time.time()
    print(f"\n--- Script finished in {end_time - start_time:.2f} seconds. ---")
