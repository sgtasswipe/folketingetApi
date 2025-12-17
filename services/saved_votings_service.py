from pydantic import BaseModel
from repositories.saved_votings_repository import save_user_voting_db, fetch_user_saved_votings_db, delete_user_saved_voting_db

class VoteRequest(BaseModel):
    voting_id: int

def get_uid_from_token(token):
    return token.split(" ")[1]

def save_user_voting(params):
    return save_user_voting_db(params)

def fetch_user_saved_votings(params):
    return fetch_user_saved_votings_db(params)

def delete_user_saved_voting(params):
    return delete_user_saved_voting_db(params)