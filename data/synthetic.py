#này làm hồi data rồi nên giờ đổi tên file thì có thể khác

import pandas as pd
import random

df = pd.read_csv("POI.csv")

# group theo city_norm
hotels = df[df["poi_id"].str.startswith("hotel")]
attractions = df[df["poi_id"].str.startswith("attraction")]
restaurants = df[df["poi_id"].str.startswith("restaurant")]

hotels_by_city = hotels.groupby("city_norm")
attractions_by_city = attractions.groupby("city_norm")
restaurants_by_city = restaurants.groupby("city_norm")

# =====================================
# TRIP GENERATOR
# =====================================
def generate_trip(city, trip_index, min_days=1, max_days=4):
    missing = []

    if city not in hotels_by_city.groups:
        missing.append("hotel")
    if city not in attractions_by_city.groups:
        missing.append("attraction")
    if city not in restaurants_by_city.groups:
        missing.append("restaurant")

    if missing:
        print(f"[SKIP] City '{city}' thiếu: {', '.join(missing)} → bỏ {trip_index}")
        return None

    hotel_list = hotels_by_city.get_group(city)
    attr_list = attractions_by_city.get_group(city)
    rest_list = restaurants_by_city.get_group(city)

    trip_id = f"trip{trip_index:05d}"
    num_days = random.randint(min_days, max_days)

    fixed_hotel = hotel_list.sample(1).iloc[0]["poi_id"]
    rows = []

    used_attr = set()

    for d in range(1, num_days + 1):
        day_label = f"day{d}"
        order = 1

        # Start at hotel
        rows.append([trip_id, day_label, order, fixed_hotel])
        order += 1

        # ===========================
        # PICK STYLE FOR THE DAY
        # ===========================
        style = random.choice(["play_heavy", "food_heavy", "balanced"])

        if style == "play_heavy":
            n_attr = random.randint(3, 5)
            n_rest = random.randint(1, 2)
        elif style == "food_heavy":
            n_attr = random.randint(1, 2)
            n_rest = random.randint(3, 4)
        else:
            n_attr = random.randint(2, 3)
            n_rest = random.randint(2, 3)

        # ===========================
        # PICK ATTRACTIONS (no repeat)
        # ===========================
        available_attr = attr_list[~attr_list["poi_id"].isin(used_attr)]
        count_attr = len(available_attr)

        activity_list = []  # list các POI trong ngày

        if count_attr > 0:
            take_attr = min(n_attr, count_attr)
            chosen_attr = available_attr.sample(n=take_attr, replace=False)

            for _, row_attr in chosen_attr.iterrows():
                poi = row_attr["poi_id"]
                activity_list.append(poi)
                used_attr.add(poi)

        # ===========================
        # PICK RESTAURANTS (can repeat)
        # ===========================
        for _ in range(n_rest):
            poi = rest_list.sample(1).iloc[0]["poi_id"]
            activity_list.append(poi)

        # ===========================
        # SHUFFLE ACTIVITIES FOR RANDOM ORDER
        # ===========================
        random.shuffle(activity_list)

        # append shuffled activities
        for poi in activity_list:
            rows.append([trip_id, day_label, order, poi])
            order += 1

        # End at hotel
        rows.append([trip_id, day_label, order, fixed_hotel])

    return rows

# =====================================
# MAIN LOOP – SKIP THÀNH PHỐ SAU LẦN ĐẦU FAIL
# =====================================

all_rows = []
trip_counter = 1
skip_cities = set()          # <---- chứa city bị skip ngay lần đầu
cities = df["city_norm"].dropna().unique()

for city in cities:

    if city in skip_cities:
        continue  # bỏ qua hoàn toàn

    # for _ in range(random.randint(50, 200)):
    for _ in range(250):
        trip_rows = generate_trip(city, trip_counter)

        if trip_rows is None:  # <---- city bị thiếu dữ liệu
            skip_cities.add(city)
            break              # <---- ngưng tạo thêm cho city này

        all_rows.extend(trip_rows)
        trip_counter += 1


# =====================================
# EXPORT CSV
# =====================================

output = pd.DataFrame(all_rows, columns=["itinerary_id", "day", "order", "poi_id"])
output.to_csv("out.csv", index=False)

print("DONE! File out.csv đã tạo.")
print("\nCÁC CITY BỊ LOẠI HOÀN TOÀN:")
print(skip_cities)
