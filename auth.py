import os
from supabase import create_client, Client
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from pydantic import BaseModel


load_dotenv()  # loads .env into environ

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
try:
    supabase: Client = create_client(url, key)
except Exception as e:
    raise RuntimeError(f"Failed to create Supabase Client {e}")

router = APIRouter(
    prefix="/auth"
)


class UserCredentials(BaseModel):
    """Schema for User Information"""
    email: str
    password: str


@router.post("/signup/email")
async def sign_up_with_email(credentials: UserCredentials):
    email = credentials.email
    password = credentials.password
    try:
        response = supabase.auth.sign_up({
            "email": email,
            "password": password,
        })
        raw = response.model_dump()
        print(raw)

        if response.session:
            return {
                "message": "user has been registered and is able to log in",
                "uid": response.user.id,
                "access_token": response.session.access_token,
                "email": response.user.email,

            }
        if response.user:
            return {
                "message": "User has been created. Needs confirmation before login available",
                "uid": response.user.id,
                "email": response.user.email,
            }

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Signup failed: {e}")


@router.post("/login/password")
async def login(credentials: UserCredentials):
    email = credentials.email
    password = credentials.password
    try:
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password,
        })
        print(response.model_dump())

        if response.user is None and response.session.access_token is None:
            raise HTTPException(
                status_code=422,
                detail="The login was unable to proccess. Please try again later. Details:"
            )
        return {
            "message": "User signed in succesfully",
            "uid": response.user.id,
            "access_token": response.session.access_token
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"failed to sign in: {e}")


class DeleteUserRequest(BaseModel):
    """Schema to delete a user"""
    access_token: str  # Supabase user ID


@router.post("/delete_user")
async def delete_user(request: DeleteUserRequest):
    token = request.access_token

    try:
        user_data = supabase.auth.get_user(token)
        if not user_data.user:
            raise HTTPException(status_code=401, detail="Invalid access token")

        user_id = user_data.user.id

        # Delete the user
        response = supabase.auth.admin.delete_user(user_id)
        return {"message": f"User {user_id} deleted successfully."}

    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Failed to delete user: {e}")
