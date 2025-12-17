from pydantic import BaseModel
from repositories.auth_repository import sign_up_supabase, login_supabase, get_user_supabase, delete_user_supabase


class DeleteUserRequest(BaseModel):
    """Schema to delete a user"""
    access_token: str  # Supabase user ID

class UserCredentials(BaseModel):
    """Schema for User Information"""
    email: str
    password: str


async def sign_up_user(params):
    return await sign_up_supabase(params)

async def login_user(params):
    return await login_supabase(params)

async def get_user(access_token):
    return await get_user_supabase(access_token)

async def delete_target_user(user_id):
    return await delete_user_supabase(user_id)