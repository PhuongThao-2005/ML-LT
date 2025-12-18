from supabase import create_client, Client
from dotenv import load_dotenv
import os

load_dotenv()

url = os.getenv("SUPABASE_URI")
key = os.getenv("SUPABASE_ANON")

supabase: Client = create_client(url, key)

def get_tour_by_ID(id: int):
  res = supabase.table("tours").select("*").eq("id", id).execute()
  return res.data[0] if res.data else None

def save_tour(tour_data: dict):
  res = supabase.table("tours").insert(tour_data).select("id").execute()
  return res.data[0]["id"] if res.data else None

