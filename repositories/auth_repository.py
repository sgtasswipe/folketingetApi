import os
from supabase import create_client, Client
from folketingetApi.util.supabase_client_creator import get_supabase_client

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
anon_key:str = os.environ.get("SUPABASE_ANON_KEY")

# Public client (for reading user session)
supabase_public: Client = create_client(url, anon_key)

# Admin client (for deleting)
supabase_admin: Client = create_client(url, key)

try:
    supabase: Client = create_client(url, key)
except Exception as e:
    raise RuntimeError(f"Failed to create Supabase Client {e}")

supabase = get_supabase_client()


async def sign_up_supabase(params):
    return supabase.auth.sign_up(params)

async def login_supabase(params):
    return supabase.auth.sign_in_with_password(params)

async def get_user_supabase(access_token):
    return supabase_public.auth.get_user(access_token)

async def delete_user_supabase(user_id):
    return supabase_admin.auth.admin.delete_user(user_id)