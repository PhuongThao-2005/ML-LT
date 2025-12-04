import pickle
from catboost import CatBoostRegressor, Pool
from preprocess import load_and_clean_data, generate_training_dataset
from utils import cat_features

def train_model(train_df):
    for col in ["user_city", "user_type", "poi_city", "poi_type"]:
        train_df[col] = train_df[col].fillna("unknown").astype(str)
    train_df = train_df.fillna(0)

    X = train_df[[
        "user_city", "user_type", "user_price",
        "poi_city", "poi_type", "poi_price",
        "rating", "latitude", "longitude"
    ]]
    y = train_df["label"]

    train_pool = Pool(X, y, cat_features=cat_features)

    model = CatBoostRegressor(
        iterations=500,
        depth=8,
        learning_rate=0.1,
        loss_function="RMSE",
        verbose=False
    )
    model.fit(train_pool)

    with open("models/poi_rank_model.pkl", "wb") as f:
        pickle.dump(model, f)

    print("Model saved!")
    return model