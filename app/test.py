# from supabase import create_client
from app.config import db_admin as supabase
import requests

# Supabase project credentials
# SUPABASE_URL = "https://cbmhooddclbrpopzrbxx.supabase.co/"
# SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNibWhvb2RkY2xicnBvcHpyYnh4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTUxNzYwNTUsImV4cCI6MjA3MDc1MjA1NX0.wxK5XR1REp9TOApdM4licFNYsX99mdI7JZymvohdnYg"

# Create client
# supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

# ====== STEP 1: LOGIN USER ======
email = "vishwagovula07@gmail.com"
password = "vishwa@9959"

auth_response = supabase.auth.sign_in_with_password({
    "email": email,
    "password": password
})

if auth_response.user is None:
    print("❌ Login failed:", auth_response)
else:
    print("✅ Logged in as:", auth_response.user.email)

# Extract token
access_token = auth_response.session.access_token
print("Access Token:", access_token)

# ====== STEP 2: TEST FASTAPI ENDPOINT ======
FASTAPI_URL = "http://localhost:8000/auth/me"

headers = {
    "Authorization": f"Bearer {access_token}"
}

response = requests.get(FASTAPI_URL, headers=headers)

print("\nFastAPI /auth/me response:")
print(response.json())
