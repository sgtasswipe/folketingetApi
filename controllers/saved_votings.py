# This should be moved into a separate file
from fastapi import HTTPException, APIRouter, Header
from util.supabase_client_creator import get_supabase_client
from dotenv import load_dotenv
from typing import Optional
from services.saved_votings_service import VoteRequest, get_uid_from_token, save_user_voting, fetch_user_saved_votings, delete_user_saved_voting

load_dotenv()

router = APIRouter(
    prefix="/vote"
)

supabase = get_supabase_client()

@router.get("/saved-votings")
async def get_saved_votings(Authorization: Optional[str] = Header(None)):
    if not Authorization or not Authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Header missing or malformed.")

    user_id = get_uid_from_token(Authorization)

    try:
        params = {
            "user_id": user_id
        }

        response = fetch_user_saved_votings(params)
        
        if response.data is None:
             return []
        else: 
            return response.data

    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=400, detail=f"Database error: {e}")
    
@router.post("/save-voting")
async def save_voting(payload: VoteRequest, Authorization: Optional[str] = Header(None)):
    if not Authorization or not Authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authorization header missing.")

    user_id = Authorization.split(" ")[1]

    try:
        params = {
            "p_user_id": user_id,
            "p_afstemning_id": payload.voting_id
        }

        save_user_voting(params)

        return {"status": "success", "message": f"Vote {payload.voting_id} saved for user {user_id}"}

    except Exception as e:
        print(f"Error saving vote: {e}")
        raise HTTPException(status_code=400, detail=f"Database error: {e}")
    
@router.delete("/delete-voting")
async def delete_voting(payload: VoteRequest, Authorization: Optional[str] = Header(None)):
    if not Authorization or not Authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authorization header missing.")

    user_id = get_uid_from_token(Authorization)

    try:
        params = {
            "p_user_id": user_id,
            "p_afstemning_id": payload.voting_id
        }

        delete_user_saved_voting(params)

        return {"status": "success", "message": f"Vote {payload.voting_id} removed for user {user_id}"}

    except Exception as e:
        print(f"Error deleting vote: {e}")
        raise HTTPException(status_code=400, detail=f"Database error: {e}")