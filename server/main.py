from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
  CORSMiddleware,
  allow_origins=["http://localhost:3000"],
  allow_credentials=True,
  allow_methods=["POST"],
  allow_headers=["apiKey"],
)

@app.get("/")
async def root():
  return {"message": "Tour Planer API is running."}

@app.post("/plan")
async def plan_tour():
  return {"id": 2}

@app.get("/history/{id}")
async def get_tour(id: int):
  return {"id": id, "destination": "Da Lat", "duration": 3, "preferences": ["nature", "food"]}