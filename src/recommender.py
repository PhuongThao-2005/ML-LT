import pickle
import pandas as pd
from catboost import Pool
from utils import similarity_weight, cat_features
from preprocess import load_and_clean_data

df = load_and_clean_data()

def get_top_poi(city, user_types, price, top_k=10):
    if isinstance(user_types,str): user_types=[user_types]
    expanded = set()
    for ut in user_types:
        ut = ut.strip().lower()
        expanded.add(ut)
        from utils import TYPE_RELATIONS_LOWER
        if ut in TYPE_RELATIONS_LOWER:
            expanded.update(TYPE_RELATIONS_LOWER[ut])
    expanded = list(expanded)

    city_norm = city.strip().lower()
    subset = df[df["city_norm"]==city_norm].copy()
    if subset.empty: return f"❌ City '{city}' not found!"

    rows=[]
    for _,poi in subset.iterrows():
        for ut in expanded:
            rows.append({
                "user_city": city_norm,
                "user_type": ut,
                "user_price": price,
                "poi_city": poi["city_norm"],
                "poi_type": poi["type"],
                "poi_price": poi["price_level"],
                "rating": poi["rating"],
                "latitude": poi["latitude"],
                "longitude": poi["longitude"],
                "poi_id": poi["poi_id"]
            })
    inf_df=pd.DataFrame(rows)
    poi_ids=inf_df["poi_id"]
    inf_df_nopoi=inf_df.drop(columns=["poi_id"])

    with open("models/poi_rank_model.pkl","rb") as f:
        model=pickle.load(f)

    inf_pool=Pool(inf_df_nopoi,cat_features=cat_features)
    inf_df["score"]=model.predict(inf_pool)

    inf_df["score"]=inf_df.apply(lambda r: r["score"]*similarity_weight(r["user_type"],r["poi_type"]),axis=1)
    agg=inf_df.groupby("poi_id")["score"].mean().reset_index()
    agg=agg.merge(df[["poi_id","name","city_norm","type","price_level"]],on="poi_id",how="left")
    return agg.sort_values("score",ascending=False).head(top_k)