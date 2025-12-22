from folketingetApi.util.supabase_client_creator import get_supabase_client

supabase = get_supabase_client()

def fetch_similar_items(params):
    return supabase.rpc("fetch_similar_items_v2", params).execute