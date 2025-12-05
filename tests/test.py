# import pytest
# from dotenv import load_dotenv
# import os
# from supabase.client import create_client, Client
# from auth import sign_up_with_email, UserCredentials 

# @pytest.fixture(scope="session")
# def sample_credentials():
#     """Set up user credentials."""
#     return UserCredentials(email="test@admin.com", password="123456")

# def supabase_client():
#     """Test DB Connection."""
#     load_dotenv()
#     SUPABASE_URL = os.environ.get("SUPABASE_URL")
#     SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
#     assert SUPABASE_URL is not None, "SUPABASE_URL is not set in environment"
#     assert SUPABASE_KEY is not None, "SUPABASE_KEY is not set in environment"
#     client = create_client(SUPABASE_URL, SUPABASE_KEY)
#     assert isinstance(client, Client), "Failed to create a Supabase Client connection"
#     return client

# @pytest.mark.asyncio
# async def test_signup_email_real_supabase(sample_credentials, supabase_client):
#     """Test ACTUAL Supabase signup with unique email."""
    
#     # Use unique email to avoid conflicts
#     unique_email = f"test-{int(os.times()[4])}@example.com"
    
#     result = await sign_up_with_email(sample_credentials)
    
#     assert result["email"] == unique_email
#     assert result["uid"] is not None
    
#     # Check both possible Supabase responses
#     if "access_token" in result:
#         assert len(result["access_token"]) > 10  # Real JWT token
#         assert result["message"] == "user has been registered and is able to log in"
#     else:
#         assert result["message"] == "User has been created. Needs confirmation before login available"

# # @pytest.mark.asyncio
# # @patch('auth.supabase.auth.sign_up', new_callable=AsyncMock)
# # async def test_signup_needs_confirmation(mock_sign_up, sample_credentials):
# #     """Test signup when response.session is None (needs email confirmation)."""
# #     mock_response = AsyncMock()
# #     mock_response.session = None  # No session
# #     mock_response.user = AsyncMock()
# #     mock_response.user.id = "user-uuid-456"
# #     mock_response.user.email = sample_credentials.email
# #     mock_sign_up.return_value = mock_response
    
# #     result = await sign_up_with_email(sample_credentials)
    
# #     assert result["message"] == "User has been created. Needs confirmation before login available"
# #     assert "access_token" not in result
# #     mock_sign_up.assert_called_once_with({"email": sample_credentials.email, "password": sample_credentials.password})
