import os
# from supabase_py_async import AsyncClient, create_client
from dotenv import load_dotenv
from supabase import create_client, AsyncClient

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_ROLE_KEY = os.getenv("SUPABASE_ROLE_KEY")

db: AsyncClient = create_client(SUPABASE_URL, SUPABASE_KEY)
db_admin: AsyncClient = create_client(SUPABASE_URL, SUPABASE_ROLE_KEY)


# this file is used to load .env variables all over the project!