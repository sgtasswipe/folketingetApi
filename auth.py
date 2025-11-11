import os
from supabase import create_client, Client
from dotenv import load_dotenv
from fastapi import APIRouter
from typing import Dict, Any
from pydantic import BaseModel

load_dotenv() #loads .env into environ 

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
try:
    supabase: Client = create_client(url, key)
except Exception as e:
    raise

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
   
    response = supabase.auth.sign_up({
    "email": email,
        "password": password,
        })
    raw = response.model_dump()
    print(raw)

  

@router.post("/login/password")
async def login(credentials: UserCredentials):
    email=credentials.email
    password=credentials.password
    response = supabase.auth.sign_in_with_password({
        "email":email,
        "password": password,
    })
    raw = response.model_dump()
    print(raw)
