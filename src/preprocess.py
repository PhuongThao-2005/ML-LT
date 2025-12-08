import pandas as pd
from utils import map_price_level, is_similar_type, generate_price_rules

def load_and_clean_data(file_path="data/POI.csv"):
    df = pd.read_csv(file_path)
    df = df[["poi_id","name","city_norm","type","price","rating","latitude","longitude", "category"]]
    
    rules = generate_price_rules(df)
    # print("\n=== Auto-Generated Price Level Rules ===")
    # for cat, r in rules.items():
    #     print(f"\nCategory: {cat}")
    #     print(f"Type: {r['type']}")
    #     print(f"L0 (Low threshold): {r['L0']}")
    #     print(f"L1 (Medium threshold): {r['L1']}")
    #     print(f"Quantiles = {r['details']}")
    
    df["price_level"] = df.apply(
        lambda r: map_price_level(r["category"], r["price"], rules),
        axis=1
    )
    df["city_norm"] = df["city_norm"].str.strip().str.lower()
    df["type"] = df["type"].str.strip().str.lower()
    return df

def generate_training_dataset(df, save_path=None):
    context_types = df["type"].unique()
    context_price_levels = [0,1,2]
    rows = []

    for _, poi in df.iterrows():
        user_city = poi["city_norm"]
        for user_type in context_types:
            for user_price in context_price_levels:
                label = 0.0
                label += 0.4  # same city
                if poi["type"] == user_type:
                    label += 0.3
                elif is_similar_type(user_type, poi["type"]):
                    label += 0.15
                if abs(poi["price_level"] - user_price) <= 1:
                    label += 0.2
                label += float(poi["rating"]) / 5 * 0.1

                rows.append({
                    "user_city": user_city,
                    "user_type": user_type,
                    "user_price": user_price,
                    "poi_city": poi["city_norm"],
                    "poi_type": poi["type"],
                    "poi_price": poi["price_level"],
                    "rating": poi["rating"],
                    "latitude": poi["latitude"],
                    "longitude": poi["longitude"],
                    "poi_id": poi["poi_id"],
                    "label": label
                })

    train_df = pd.DataFrame(rows)
    
    if save_path:  # nếu có path thì lưu
        train_df.to_csv(save_path, index=False)
        print(f"Saved training dataset to {save_path}, shape={train_df.shape}")

    return train_df