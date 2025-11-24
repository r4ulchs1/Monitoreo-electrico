import os

from dotenv import load_dotenv
from supabase import Client, create_client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError(
        "ERROR: Debes definir SUPABASE_URL y SUPABASE_KEY en un archivo .env"
    )


def get_supabase() -> Client:
    """Retorna una instancia única del cliente Supabase."""
    return create_client(SUPABASE_URL, SUPABASE_KEY)
