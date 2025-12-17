from functools import lru_cache
from supabase import create_client, Client
from dotenv import load_dotenv
import os

load_dotenv()  # loads .env into environ
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")

@lru_cache(maxsize=1)
def get_supabase_client() -> Client:
        print("Supabase Client created once with singleton")
        try:
            return create_client(url, key)
        except Exception as e:
             raise RuntimeError(f"Failed to create Supabase Client {e}")
