import pandas as pd
import numpy as np
import pickle
import os
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import LabelEncoder
from utils import calculate_similarity_score

# ================= 1. DOMAIN LOGIC ===================
TYPE_RELATIONS = {
    "coffee shop": ["cafe", "tea shop", "bakery"],
    "restaurant": ["bar/pub", "vegetarian", "bakery", "food"],
    "bar/pub": ["restaurant"],
    "natural": ["attraction", "entertainment", "park", "beach"],
    "attraction": ["natural", "cultural", "historical"],
    "cultural": ["attraction", "historical", "museum"],
    "historical": ["attraction", "cultural"],
    "hotel": ["villa", "resort", "homestay", "hostel", "apartment"],
    "shopping": ["entertainment", "market", "mall"],
    "entertainment": ["shopping", "natural"],
}

# ================= 2. BASE CLASS =====================
class BaseRecommender:
    def __init__(self, model_name="base"):
        self.model = None
        self.model_name = model_name
        self.encoders = {}
        self.scaler = None # Dùng cho Linear Regression nếu cần

        self.cat_features = ["user_city", "user_type", "poi_city", "poi_type"]
        
        self.num_features = ["user_price", "poi_price", "rating", "latitude", "longitude", "type_match_score"]
        self.features = self.cat_features + self.num_features

    # -------- Feature Engineering ----------
    def feature_engineering(self, df):
        df = df.copy()
        df["type_match_score"] = df.apply(
            lambda x: calculate_similarity_score(x.get("user_type", ""), x.get("poi_type", "")),
            axis=1,
        )
        # Fill NA cho các cột số
        for col in ["user_price", "poi_price", "rating"]:
            if col in df.columns: df[col] = df[col].fillna(0)
        
        # Fill NA cho tọa độ (tránh lỗi Planner)
        for col in ["latitude", "longitude"]:
            if col in df.columns: df[col] = df[col].fillna(0.0)
            
        return df

    # -------- Encoding ---------------------
    def fit_encoders(self, df):
        for col in self.cat_features:
            le = LabelEncoder()
            df[col] = df[col].astype(str).fillna("unknown")
            df[col] = le.fit_transform(df[col])
            self.encoders[col] = le
        return df

    def transform_encoders(self, df):
        df = df.copy()
        for col in self.cat_features:
            if col in self.encoders:
                le = self.encoders[col]
                # Map an toàn: nếu gặp nhãn lạ -> -1
                df[col] = df[col].astype(str).map(
                    lambda s: le.transform([s])[0] if s in le.classes_ else -1
                )
        return df

    # -------- Helpers ---------------------
    def split_data(self, X, y):
        X_train, X_temp, y_train, y_temp = train_test_split(X, y, test_size=0.3, random_state=42)
        X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=0.5, random_state=42)
        return X_train, X_val, X_test, y_train, y_val, y_test

    def evaluate(self, X_test, y_test):
        preds = self.model.predict(X_test)
        rmse = np.sqrt(mean_squared_error(y_test, preds))
        return {
            "MAE": mean_absolute_error(y_test, preds),
            "RMSE": rmse,
            "R2": r2_score(y_test, preds),
        }

    # -------- Save / Load --------------------------
    def save(self, path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        # Lưu cả model, encoder và scaler
        payload = {"model": self.model, "encoders": self.encoders, "scaler": self.scaler}
        with open(path, "wb") as f:
            pickle.dump(payload, f)
        print(f"✓ [{self.model_name}] Model saved to {path}")

    def load(self, path):
        if not os.path.exists(path):
            raise FileNotFoundError(f"File not found: {path}")
        with open(path, "rb") as f:
            payload = pickle.load(f)
        self.model = payload["model"]
        self.encoders = payload.get("encoders", {})
        self.scaler = payload.get("scaler", None)
        print(f"✓ [{self.model_name}] Model loaded.")

    # -------- RECOMMEND (CORE FUNCTION) ----------
    def recommend(self, df_raw, city, user_type, user_price, top_k=100):
        """
        Dự đoán và trả về danh sách POI kèm Score và các thông tin cần thiết cho Planner.
        """
        city_norm = city.lower().strip()
        
        # Hỗ trợ user_type là list hoặc string
        if isinstance(user_type, str):
            user_types = [user_type.lower().strip()]
        else:
            user_types = [ut.lower().strip() for ut in user_type]

        # Lọc theo thành phố
        subset = df_raw[df_raw["city_norm"] == city_norm].copy()
        if subset.empty: return pd.DataFrame()

        # Tạo input giả lập (Cartesian Product: User x All POIs)
        rows = []
        for _, poi in subset.iterrows():
            for ut in user_types:
                rows.append({
                    "user_city": city_norm,
                    "user_type": ut,
                    "user_price": user_price,
                    
                    # Mapping từ dữ liệu gốc (POI.csv)
                    "poi_city": poi.get("city_norm", ""),
                    "poi_type": poi.get("type", "unknown"),

                    "poi_price": poi.get("price_level", 0), 
                    "price": poi.get("price", 0),

                    "rating": poi.get("rating", 0),
                    "latitude": poi.get("latitude", 0.0),
                    "longitude": poi.get("longitude", 0.0),
                    "poi_id": poi["poi_id"],
                    "name": poi["name"],
                })

        inf = pd.DataFrame(rows)

        # 1. Feature Engineering
        processed = self.feature_engineering(inf)

        # 2. Xử lý Input tùy theo Model Type
        if "CatBoost" in self.model_name:
            # CatBoost cần string, không cần transform số
            for col in self.cat_features:
                processed[col] = processed[col].astype(str).fillna("unknown")
            X_pred = processed[self.features]
        else:
            # Linear/RandomForest cần transform số
            processed = self.transform_encoders(processed)
            X_pred = processed[self.features]
            # Linear cần Scaler
            if self.scaler:
                X_pred = self.scaler.transform(X_pred)

        # 3. Predict Score
        inf["score"] = self.model.predict(X_pred)

        # 4. Gom nhóm & Trả về đủ cột cho Planner/Optimizer
        # (latitude, longitude, poi_type, poi_price là bắt buộc để Planner chạy)
        out = (
            inf.groupby("poi_id", as_index=False)
            .agg({
                "name": "first",
                "score": "mean",
                "latitude": "first",
                "longitude": "first",
                "poi_type": "first",
                "poi_price": "first",  # price level
                "price": "first"       #  giá thật
            })
            .sort_values("score", ascending=False)
            .head(top_k)
        )

        return out[[
            "poi_id",
            "name",
            "score",
            "latitude",
            "longitude",
            "poi_type",
            "poi_price",
            "price"
        ]]

    # Hàm abstract
    def train(self, df):
        raise NotImplementedError