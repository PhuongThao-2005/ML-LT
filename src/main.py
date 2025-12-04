# main.py
from preprocess import load_and_clean_data, generate_training_dataset
from catboost_train import train_model
from recommender import get_top_poi

#Nếu cần train lại
# =======================================================
# df = load_and_clean_data("data/POI.csv")
# train_df = generate_training_dataset(df)
# train_model(train_df)
# =======================================================

# =======================================================
# TEST RECOMMEND FUNCTION
# =======================================================

# 1) Nhiều types, city có trong dữ liệu
top1 = get_top_poi("da nang", ["coffee shop", "natural"], price=1, top_k=10)
print("Test 1: Da Nang, coffee shop + natural, price=1")
print(top1, "\n")

# 2) Chỉ 1 type, khác case
top2 = get_top_poi("ho chi minh", "restaurant", price=2, top_k=10)
print("Test 2: Ho Chi Minh, single type restaurant, price=2")
print(top2, "\n")

# 3) City không tồn tại
top3 = get_top_poi("unknown city", ["hotel"], price=0, top_k=10)
print("Test 3: Unknown city")
print(top3, "\n")

# 4) Type tương tự, xem boost có hoạt động
top4 = get_top_poi("ha noi", ["bar/pub"], price=1, top_k=10)
print("Test 4: Ha Noi, bar/pub → should include restaurant/bakery/vegetarian")
print(top4, "\n")

# 5) Giá cực thấp (price=0) và price cao (price=2)
top5 = get_top_poi("da nang", ["natural"], price=0, top_k=10)
top6 = get_top_poi("da nang", ["natural"], price=2, top_k=10)
print("Test 5: Da Nang, natural, price=0")
print(top5, "\n")
print("Test 6: Da Nang, natural, price=2")
print(top6, "\n")

