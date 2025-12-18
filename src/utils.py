cat_features = ["user_city", "user_type", "poi_city", "poi_type"]

TYPE_RELATIONS = {
    "Coffee Shop": ["Cafe", "Tea Shop", "Bakery"],
    "Restaurant": ["Bar/Pub", "Vegetarian", "Bakery"],
    "Bar/Pub": ["Restaurant"],
    "Natural": ["Attraction", "Entertainment"],
    "Attraction": ["Natural", "Cultural", "Historical"],
    "Cultural": ["Attraction", "Historical"],
    "Historical": ["Attraction", "Cultural"],
    "Hotel": ["Villa", "Resort", "Homestay", "Hostel", "Apartment"],
    "Homestay": ["Hotel", "Hostel"],
    "Hostel": ["Homestay", "Hotel"],
    "Villa": ["Hotel", "Resort"],
    "Resort": ["Hotel", "Villa"],
    "Apartment": ["Hotel"],
    "Shopping": ["Entertainment"],
    "Entertainment": ["Shopping", "Natural"],
    "Vegetarian": ["Restaurant"],
    "Tea Shop": ["Coffee Shop"],
}

TYPE_RELATIONS_LOWER = {k.lower(): [v.lower() for v in vals] for k, vals in TYPE_RELATIONS.items()}

def is_similar_type(user_type, poi_type):
    u = user_type.lower().strip()
    p = poi_type.lower().strip()
    if u == p:
        return True
    return u in TYPE_RELATIONS_LOWER and p in TYPE_RELATIONS_LOWER[u]

def similarity_weight(user_type, poi_type):
    u = user_type.lower().strip()
    p = poi_type.lower().strip()
    if u == p:
        return 1.20
    if is_similar_type(u, p):
        return 1.05
    return 0.90

def generate_price_rules(df, medium_cap_default=200_000):
    quantiles = df.groupby("category")["poi_price"].quantile([0.25, 0.5, 0.75]).unstack()
    quantiles.columns = ["Q1", "Q2", "Q3"]

    rules = {}

    for cat, row in quantiles.iterrows():
        q1, q2, q3 = row["Q1"], row["Q2"], row["Q3"]

        if q1 == 0 and q2 == 0 and q3 == 0:
            rules[cat.lower()] = {
                "type": "skewed_zero",
                "L0": 0,
                "L1": medium_cap_default,
                "details": row.to_dict()
            }
        else:
            rules[cat.lower()] = {
                "type": "normal",
                "L0": q1,
                "L1": q3,
                "details": row.to_dict()
            }

    return rules


def map_price_level(category, price, rules):
    cat = category.lower()
    if cat not in rules:
        return 1

    r = rules[cat]

    if r["type"] == "skewed_zero":
        if price == 0:
            return 0
        if price <= r["L1"]:
            return 1
        return 2

    # normal category
    if price <= r["L0"]:
        return 0
    if price <= r["L1"]:
        return 1
    return 2