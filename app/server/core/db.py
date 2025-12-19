from supabase import create_client, Client
from dotenv import load_dotenv
import os

load_dotenv()

url = os.getenv("SUPABASE_URI")
key = os.getenv("SUPABASE_ANON")

class Database():
  def __init__(self):
    self.client: Client = create_client(url, key)
    
  def get_tour_by_ID(self, id: int):
    res = self.client.table("tours").select("*").eq("id", id).execute()
    return res.data[0] if res.data else None

  def save_tour(self, tour_data: dict):
    res = self.client.table("tours").insert(tour_data).execute()
    return res.data[0]["id"] if res.data else None