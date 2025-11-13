from supabase import create_client, Client
from dotenv import load_dotenv
import os

load_dotenv()  # loads .env into environ
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")


async def create_supabase_client():
    try:
        supabase: Client = create_client(url, key)
        return supabase
    except Exception as e:
        raise RuntimeError(f"Failed to create Supabase Client {e}")
