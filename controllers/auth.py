from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
from services.auth_service import UserCredentials, DeleteUserRequest, sign_up_user, login_user, get_user, delete_target_user

load_dotenv()  # loads .env into environ

router = APIRouter(
    prefix="/auth"
)

@router.post("/signup/email")
async def sign_up_with_email(credentials: UserCredentials):
    email = credentials.email
    password = credentials.password

    try:
        params = {
            "email": email,
            "password": password,
        }

        response = await sign_up_user(params)

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
        params = {
            "email": email,
            "password": password,
        }

        response = await login_user(params)

    except Exception as e:
        # Supabase throws here for invalid credentials
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    if not response.user or not response.session or not response.session.access_token:
        raise HTTPException(
            status_code=422,
            detail="Unable to process login."
        )

    return {
        "message": "User signed in successfully",
        "uid": response.user.id,
        "access_token": response.session.access_token,
    }

@router.post("/delete_user")
async def delete_user(request: DeleteUserRequest):
    try:
        user_data = await get_user(request.access_token)

        if not user_data or not user_data.user:
            raise HTTPException(status_code=401, detail="Invalid access token")

        user_id = user_data.user.id

        await delete_target_user(user_id)
        
        return {"message": f"User {user_id} deleted successfully."}
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to delete user: {e}")