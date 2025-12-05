import pytest
import pytest_asyncio
import time
import os
from fastapi import HTTPException
from folketingetApi.auth import DeleteUserRequest, delete_user, sign_up_with_email, login, UserCredentials, supabase
from supabase import create_client
import folketingetApi.auth as auth

# Testing with overriding supabase client
@pytest.fixture
def supabase_admin():
    url = os.environ.get("SUPABASE_URL")
    service_role_key = os.environ.get("SUPABASE_KEY")
    return create_client(url, service_role_key)

@pytest.fixture(scope="module")
def shared_credentials():
    return UserCredentials(
        email=f"test_{int(time.time())}@example.com",
        password="deez123456"
    )

@pytest.fixture(autouse=True)
def override_supabase(monkeypatch, supabase_admin):
    # Replace the supabase client inside auth.py

    monkeypatch.setattr(auth, "supabase", supabase_admin)

# ----- Integration tests -----

@pytest.mark.order(1)
@pytest.mark.asyncio
async def test_signup_supabase(shared_credentials):
    result = await sign_up_with_email(shared_credentials)
    assert result["access_token"] is not None

# @pytest.mark.asyncio
# async def test_signup_supabase_no_access_token(mock_credentials):
#     # Verify client exists
#     assert supabase is not None
    
#     result = await sign_up_with_email(mock_credentials)
    
#     assert result["access_token"] is None

@pytest.mark.order(2)
@pytest.mark.asyncio
async def test_login_supabase_with_account(shared_credentials):
    result = await login(shared_credentials)
    assert result["access_token"] is not None


@pytest.mark.order(3)
@pytest.mark.asyncio
async def test_login_supabase_without_account():
    mock_user = UserCredentials(email="non_existent_user@test.com", password="onetwothreefour567")
    
    with pytest.raises(HTTPException) as exc_info:
        await login(mock_user)

    assert exc_info.value.status_code == 400


# Delete user
@pytest_asyncio.fixture
async def access_token(shared_credentials):
    result = await login(shared_credentials)
    return result["access_token"]

@pytest.mark.order(5)
@pytest.mark.asyncio
async def test_delete_supabase_with_account(access_token, shared_credentials):
    request = DeleteUserRequest(access_token=access_token)
    result = await delete_user(request)

    assert "deleted successfully" in result["message"]

    with pytest.raises(HTTPException):
        await login(shared_credentials)


# pytest -v -s