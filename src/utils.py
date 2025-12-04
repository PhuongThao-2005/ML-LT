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

def map_price_level(p):
    if p <= 100_000: return 0
    if p <= 300_000: return 1
    return 2
