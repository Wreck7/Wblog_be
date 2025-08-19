import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_ROLE_KEY = os.getenv("SUPABASE_ROLE_KEY")

db = create_client(SUPABASE_URL, SUPABASE_KEY)
db_admin = create_client(SUPABASE_URL, SUPABASE_ROLE_KEY)


# this file is used to load .env variables all over the project!