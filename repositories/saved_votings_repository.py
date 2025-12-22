from util.supabase_client_creator import get_supabase_client

supabase = get_supabase_client()

def save_user_voting_db(params):
    return supabase.rpc('save_user_afstemning', params).execute()

def fetch_user_saved_votings_db(params):
    return supabase.rpc('get_user_saved_votes', params).execute()

def delete_user_saved_voting_db(params):
    return supabase.rpc('delete_user_afstemning', params).execute()