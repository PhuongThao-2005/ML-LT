import re
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import pandas as pd

# Import các class logic của bạn
from core.planner import TimeAwareMultiDayPlanner, RouteOptimizer, HistoryAnalyzer
from core.recommender import CatBoostRecommender
from core.llm_processor import call_gemini

PATH = {
    "poi": 'data/POI.csv',
    "dist": 'data/distance_km.csv',
    "dur": 'data/duration_min.csv',
    "history": 'data/itinerary_history.csv',
    "model_rec": 'models/catboost_rec_final.pkl'
}

app = FastAPI(title="Travel Itinerary AI")
engine_instance = {}

@app.on_event("startup")
def load_resources():
    print(">>> Server starting... Loading Data & Models...")
    
    # Load Dataframes
    df_poi = pd.read_csv("data/POI.csv")
    df_dur = pd.read_csv("data/duration_min.csv")
    df_dist = pd.read_csv("data/distance_km.csv")
    
    # Load Engines
    rec = CatBoostRecommender()
    rec.load("models/catboost_rec_final.pkl")
    
    opt = RouteOptimizer(PATH["dur"], PATH["dist"], PATH["poi"])
    hist = HistoryAnalyzer()
    hist.fit(PATH["history"]) 
    
    # Init Planner
    planner = TimeAwareMultiDayPlanner(rec, opt, df_poi, hist)
    
    # Lưu vào biến global để dùng lại
    engine_instance["planner"] = planner
    engine_instance["df_poi"] = df_poi
    print(">>> Ready to serve requests!")

class NaturalLanguageRequest(BaseModel):
    query: str

# --- 3. API ENDPOINT ---
@app.post("/api/chat-plan")
async def create_plan(req: NaturalLanguageRequest):
    planner = engine_instance.get("planner")
    df_poi = engine_instance.get("df_poi")

    print(f"Received query: {req.query}")
    
    # 1. Chuẩn hóa tên thành phố từ input
    # (Dùng req.user_city thay vì req['user_city'])
    trip_info = call_gemini(req.query)
    city_key = trip_info.get("user_city", "ha noi").lower().strip()
    user_days = trip_info.get("total_days", 3)
    user_type = trip_info.get("user_type", ["attraction"])
    user_price = trip_info.get("user_price", 1)

    print(f"Parsed Input - City: {city_key}, Days: {user_days}, Type: {user_type}, Price: {user_price}")
    
    # 2. Lọc POI theo thành phố (Logic của bạn)
    city_pois = df_poi[df_poi['city_norm'] == city_key]
    
    # [QUAN TRỌNG] Xử lý ngay nếu không tìm thấy thành phố
    if city_pois.empty:
        raise HTTPException(status_code=404, detail=f"Không tìm thấy dữ liệu cho thành phố: {req.user_city}")

    # 3. Tìm khách sạn (Logic của bạn)
    hotels = city_pois[city_pois['type'].str.contains('hotel', case=False, na=False)]
    
    start_id = None
    start_name = "Unknown"
    
    if not hotels.empty:
        start_id = hotels.iloc[0]['poi_id']
        start_name = hotels.iloc[0]['name']
        print(f"Chọn khách sạn: {start_name}")
    else:
        # Fallback: Lấy điểm đầu tiên
        start_id = city_pois.iloc[0]['poi_id']
        start_name = city_pois.iloc[0]['name']
        print(f"Không có khách sạn, xuất phát từ: {start_name}")
    
    # 4. Chạy thuật toán
    print(f"Planning for: {city_key}, {user_days} days...")
    
    user_profile = {
        "user_city": city_key, # Dùng key đã chuẩn hóa
        "user_type": user_type,
        "user_price": user_price
    }
    
    try:
        schedule = planner.plan_itinerary(
            user_profile, 
            total_days=user_days, 
            start_poi_id=start_id, 
            pois_per_day=4
        )
        
        if not schedule:
            return {"status": "error", "message": "Không thể tạo lịch trình."}
            
        return {
            "status": "success",
            "city": city_key,
            "start_point": start_name,
            "days": user_days,
            "itinerary": schedule
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))