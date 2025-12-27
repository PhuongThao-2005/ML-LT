import pandas as pd
from collections import defaultdict
import numpy as np
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp

TYPE_RELATIONS = {
    "coffee shop": ["cafe", "tea shop", "bakery"],
    "restaurant": ["vegetarian", "bakery", "food", "restaurant"],
    "bar/pub": ["restaurant"],
    "natural": ["attraction", "entertainment", "park", "beach"],
    "attraction": ["natural", "cultural", "historical"],
    "cultural": ["attraction", "historical", "museum"],
    "historical": ["attraction", "cultural"],
    "hotel": ["villa", "resort", "homestay", "hostel", "apartment"],
    "shopping": ["entertainment", "market", "mall"],
    "entertainment": ["shopping", "natural"],
}

class RouteOptimizer:
    def __init__(self, duration_file, distance_file, poi_file):
        # Load dữ liệu ma trận
        # fillna(0) để đảm bảo không lỗi tính toán
        self.duration_matrix = pd.read_csv(duration_file, index_col='poi_id').fillna(0)
        self.distance_matrix = pd.read_csv(distance_file, index_col='poi_id').fillna(0)
        
    def get_time_between(self, from_id, to_id):
        try:
            # OR-Tools cần int
            val = self.duration_matrix.loc[from_id, to_id]
            return int(val)
        except KeyError:
            return 30 * 60 # Phạt 30 phút nếu không tìm thấy dữ liệu

    def optimize_route(self, selected_poi_ids, start_poi_id, max_time_minutes=720, visit_time_per_poi=60):
        """
        Sắp xếp thứ tự đi tối ưu cho một danh sách điểm.
        """
        # 1. Chuẩn bị dữ liệu (Đưa điểm xuất phát lên đầu list)
        targets = [pid for pid in selected_poi_ids if pid != start_poi_id]
        full_ids = [start_poi_id] + targets
        
        # Map: Index (0,1,2) <-> POI_ID (String)
        idx_to_id = {i: pid for i, pid in enumerate(full_ids)}
        n = len(full_ids)
        
        # Tạo ma trận thời gian con (Sub-matrix)
        time_matrix = {}
        for i in range(n):
            time_matrix[i] = {}
            for j in range(n):
                if i == j: 
                    time_matrix[i][j] = 0
                else:
                    travel = self.get_time_between(idx_to_id[i], idx_to_id[j])
                    # Nếu j là điểm đến, cộng thêm thời gian chơi. Về khách sạn (node 0) thì không cộng.
                    visit = 0 if j == 0 else int(visit_time_per_poi)
                    time_matrix[i][j] = travel + visit

        # 2. Cấu hình OR-Tools
        manager = pywrapcp.RoutingIndexManager(n, 1, 0) # 1 xe, xuất phát tại 0
        routing = pywrapcp.RoutingModel(manager)
        
        def time_callback(from_idx, to_idx):
            from_node = manager.IndexToNode(from_idx)
            to_node = manager.IndexToNode(to_idx)
            return time_matrix[from_node][to_node]

        transit_idx = routing.RegisterTransitCallback(time_callback)
        routing.SetArcCostEvaluatorOfAllVehicles(transit_idx)
        
        # Thêm ràng buộc thời gian (Max 12 tiếng/ngày)
        routing.AddDimension(transit_idx, 30, int(max_time_minutes), True, "Time")
        
        # Cho phép bỏ điểm (Penalty) nếu không kịp giờ
        for node in range(1, n):
            routing.AddDisjunction([manager.NodeToIndex(node)], 100000)

        # 3. Chạy thuật toán
        search_params = pywrapcp.DefaultRoutingSearchParameters()
        # Chiến lược tham lam (nhanh) để khởi tạo
        search_params.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
        # Chiến lược Metaheuristic (thông minh) để tối ưu
        search_params.local_search_metaheuristic = routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
        search_params.time_limit.seconds = 2

        solution = routing.SolveWithParameters(search_params)

        if solution:
            route = []
            index = routing.Start(0)
            total_time = 0
            while not routing.IsEnd(index):
                node_idx = manager.IndexToNode(index)
                poi_id = idx_to_id[node_idx]
                
                route.append({
                    "order": len(route) + 1,
                    "poi_id": poi_id,
                    "type": "Start" if len(route)==0 else "Visit"
                })
                
                index = solution.Value(routing.NextVar(index))
                if not routing.IsEnd(index):
                    next_node = manager.IndexToNode(index)
                    total_time += time_matrix[node_idx][next_node]
            
            return {"status": "success", "total_time": total_time, "route": route}
        
        return {"status": "fail"}
    


class HistoryAnalyzer:
    def __init__(self):
        self.co_occurrence = defaultdict(lambda: defaultdict(int))

    def fit(self, history_csv_path):
        """Học: Người ta thường đi đâu sau điểm A?"""
        try:
            df = pd.read_csv(history_csv_path)
            # Sắp xếp đúng thứ tự chuyến đi
            df = df.sort_values(['itinerary_id', 'day', 'order'])
            
            for _, group in df.groupby(['itinerary_id', 'day']):
                pois = group['poi_id'].tolist()
                for i in range(len(pois) - 1):
                    curr, next_p = pois[i], pois[i+1]
                    self.co_occurrence[curr][next_p] += 1
            print(f"History Patterns Learned: {len(self.co_occurrence)} nodes.")
        except Exception as e:
            print(f"History load failed: {e}")

    def get_popularity_score(self, current_poi, candidate_poi):
        """Tính điểm phổ biến của cặp (A -> B)"""
        if current_poi not in self.co_occurrence: return 0.0
        
        transitions = self.co_occurrence[current_poi]
        count = transitions.get(candidate_poi, 0)
        total = sum(transitions.values())
        
        return count / total if total > 0 else 0
    
class TimeAwareMultiDayPlanner:
    def __init__(self, recommender, optimizer, df_poi, history_engine=None):
        self.recommender = recommender
        self.optimizer = optimizer
        self.history_engine = history_engine
        self.poi_df = df_poi.copy()
        if "poi_id" in self.poi_df.columns:
            self.poi_df = self.poi_df.set_index("poi_id")

    # =========================
    # UTILS
    # =========================
    def _get_type_group(self, poi_type):
        t = str(poi_type).lower()
        if any(k in t for k in TYPE_RELATIONS["restaurant"]):
            return 'food'
        elif any(k in t for k in TYPE_RELATIONS["coffee shop"]):
            return 'cafe'
        else:
            return 'attraction'

    def _distance(self, id1, id2):
        """Tính khoảng cách Euclidean đơn giản (để tính score nhanh)"""
        try:
            lat1, lon1 = self.poi_df.loc[id1, ['latitude', 'longitude']]
            lat2, lon2 = self.poi_df.loc[id2, ['latitude', 'longitude']]
            return np.sqrt((lat1 - lat2)**2 + (lon1 - lon2)**2)
        except:
            return 999.0

    # =========================
    # SMART NEARBY POI SELECTOR
    # =========================
    def _find_smart_next_poi(self, center_id, candidate_df, fallback_type=None, max_time_limit=None, exclude_ids=None):
        """
        Tìm POI tiếp theo. 
        - max_time_limit (int): Nếu set, chỉ trả về POI cách center_id dưới số phút này.
        """
        if center_id is None: return None
        if exclude_ids is None: exclude_ids = []

        # 1. Tiền xử lý: Loại bỏ các ID bị loại trừ (tránh trùng lặp 100%)
        if not candidate_df.empty:
            candidate_df = candidate_df[~candidate_df['poi_id'].isin(exclude_ids)].copy()

        # 2. Lọc Junk POIs (Văn phòng, đại lý tour ảo) để lịch trình sạch hơn
        junk_keywords = ['tours', 'travel co', 'agency', 'office', 'motorcycle rental', 'rentabike']
        if fallback_type == 'attraction' or fallback_type is None:
            # Chỉ lọc rác nếu là tìm điểm tham quan
            mask_junk = candidate_df['name'].str.lower().str.contains('|'.join(junk_keywords))
            candidate_df = candidate_df[~mask_junk].copy()

        # 3. Fallback: Nếu candidate_df rỗng, lấy từ DB gốc
        if candidate_df.empty and fallback_type:
            mask = self.poi_df['type'].apply(self._get_type_group) == fallback_type
            candidate_df = self.poi_df[mask].reset_index()
            # Loại trừ ID hiện tại và junk một lần nữa trong fallback
            candidate_df = candidate_df[~candidate_df['poi_id'].isin(exclude_ids)]
            if fallback_type == 'attraction':
                mask_junk = candidate_df['name'].str.lower().str.contains('|'.join(junk_keywords))
                candidate_df = candidate_df[~mask_junk]

        if candidate_df.empty: return None

        # 4. Lọc theo khoảng cách địa lý (Sơ loại để tăng tốc)
        if len(candidate_df) > 50:
            lat_c, lon_c = self.poi_df.loc[center_id, ['latitude', 'longitude']]
            mask_geo = (np.abs(candidate_df['latitude'] - lat_c) < 0.1) & (np.abs(candidate_df['longitude'] - lon_c) < 0.1)
            candidate_df = candidate_df[mask_geo].copy()

        if candidate_df.empty: return None

        # 5. Lọc chính xác theo thời gian di chuyển
        valid_rows = []
        candidate_ids = candidate_df['poi_id'].tolist()
        limit = max_time_limit if max_time_limit else 30 
        
        for idx, pid in enumerate(candidate_ids):
            try:
                t = self.optimizer.get_time_between(center_id, pid)
                if t is not None and t <= limit: 
                    valid_rows.append(candidate_df.iloc[idx])
            except: continue

        # 6. Chọn POI tốt nhất dựa trên điểm số
        if valid_rows:
            candidate_df = pd.DataFrame(valid_rows).reset_index(drop=True)
        else:
            if max_time_limit: return None # Trả về None nếu yêu cầu "phải gần" mà không có
            # Nếu không tìm được điểm gần, nới lỏng giới hạn hoặc lấy điểm gần nhất về mặt địa lý
            return None 

        dist_vals = np.array([self._distance(center_id, pid) for pid in candidate_df['poi_id']])
        dist_score = 1 / (dist_vals + 1e-6)
        
        hist_scores = np.zeros(len(candidate_df))
        if self.history_engine:
            for i, pid in enumerate(candidate_df['poi_id']):
                hist_scores[i] = self.history_engine.get_popularity_score(center_id, pid)

        # Cân bằng: 80% Khoảng cách, 20% Độ phổ biến/Gợi ý
        final_scores = 0.8 * dist_score + 0.2 * hist_scores
        best_idx = np.argmax(final_scores)
        
        return candidate_df.iloc[best_idx]['poi_id']

    # =========================
    # TIME PACING
    # =========================
    def _calculate_dynamic_pacing(self, num_pois):
        available_hours = 6.5
        if num_pois <= 0:
            return 60
        return int(np.clip((available_hours * 60) / num_pois, 45, 150))

    # =========================
    # BALANCED CLUSTERING
    # =========================
    def _balanced_clustering(self, df_points, k_days):
        n = len(df_points)
        if n == 0:
            return []
        if k_days <= 1:
            return [0] * n

        df_calc = df_points.copy()
        center_lat = df_calc['latitude'].mean()
        center_lon = df_calc['longitude'].mean()

        df_calc['angle'] = np.arctan2(
            df_calc['latitude'] - center_lat,
            df_calc['longitude'] - center_lon
        )

        df_sorted = df_calc.sort_values('angle')
        sorted_ids = df_sorted['poi_id'].values
        chunks = np.array_split(sorted_ids, k_days)

        cluster_map = {}
        for day_id, chunk_ids in enumerate(chunks):
            for pid in chunk_ids:
                cluster_map[pid] = day_id

        # Map lại vào dataframe gốc để giữ đúng thứ tự index
        return (
            df_points['poi_id']
            .map(cluster_map)
            .fillna(0)
            .astype(int)
            .tolist()
        )

    # =========================
    # MAIN PLANNER
    # =========================
    def plan_itinerary(self, user_profile, total_days, start_poi_id, pois_per_day):
        # 1. Recommendation (Giữ nguyên logic của bạn)
        all_scored = self.recommender.recommend(self.poi_df.reset_index(), user_profile['user_city'], 
                                               user_profile['user_type'], user_profile['user_price'], top_k=200)
        if all_scored.empty: return []

        all_scored['group'] = all_scored['poi_type'].apply(self._get_type_group)
        pool_attr = all_scored[all_scored['group'] == 'attraction'].copy().head(total_days * pois_per_day)
        pool_food = self.recommender.recommend(self.poi_df.reset_index(), user_profile['user_city'], ['restaurant'], user_profile['user_price'], top_k=50)
        pool_cafe = all_scored[all_scored['group'] == 'cafe'].copy()

        pool_attr['day_cluster'] = self._balanced_clustering(pool_attr.copy(), total_days)
        full_schedule = []

        for day_idx, cluster_id in enumerate(sorted(pool_attr['day_cluster'].unique())):
            if day_idx >= total_days: break
            
            day_attr_ids = pool_attr[pool_attr['day_cluster'] == cluster_id]['poi_id'].tolist()
            visit_time = self._calculate_dynamic_pacing(len(day_attr_ids))
            opt_res = self.optimizer.optimize_route(day_attr_ids, start_poi_id, max_time_minutes=960, visit_time_per_poi=visit_time)
            
            if opt_res['status'] != 'success': continue

            skeleton = opt_res['route']
            final_day_route = []
            current_time = 8.5 
            has_lunch = has_cafe = has_dinner = False
            prev_id = None
            visited_in_day = [start_poi_id] 

            # --- SKELETON LOOP ---
            for step in skeleton:
                poi_id = step['poi_id']
                visited_in_day.append(poi_id)

                travel_min = self.optimizer.get_time_between(prev_id, poi_id) if prev_id else 0
                current_time += travel_min / 60.0

                # Append Visit
                final_day_route.append({
                    "poi_id": poi_id,
                    "order": 0, # Sẽ re-index sau
                    "type": step['type'],
                    "name": self.poi_df.loc[poi_id, 'name'],
                    "arrival_time": f"{int(current_time):02d}:{int((current_time%1)*60):02d}",
                    "travel_before_min": int(travel_min),
                    "duration_min": int(visit_time) if step['type'] == 'Visit' else 0,
                    "longitude": float(self.poi_df.loc[poi_id, 'longitude']),
                    "latitude": float(self.poi_df.loc[poi_id, 'latitude']),
                    "address": str(self.poi_df.loc[poi_id, 'address']),
                    "rating": float(self.poi_df.loc[poi_id, 'rating'])
                })
                
                if step['type'] == 'Visit': current_time += visit_time / 60.0
                prev_id = poi_id

                # --- LUNCH INSERTION ---
                if not has_lunch and current_time >= 11.5:
                    lunch_id = self._find_smart_next_poi(prev_id, pool_food, 'food', exclude_ids=visited_in_day)
                    if lunch_id:
                        visited_in_day.append(lunch_id)
                        t = self.optimizer.get_time_between(prev_id, lunch_id)
                        current_time += t / 60.0
                        final_day_route.append({
                            "poi_id": lunch_id,
                            "order": 0,
                            "type": "Lunch",
                            "name": self.poi_df.loc[lunch_id, 'name'],
                            "arrival_time": f"{int(current_time):02d}:{int((current_time%1)*60):02d}",
                            "travel_before_min": int(t),
                            "duration_min": 90,
                            "longitude": float(self.poi_df.loc[lunch_id, 'longitude']),
                            "latitude": float(self.poi_df.loc[lunch_id, 'latitude']),
                            "address": str(self.poi_df.loc[lunch_id, 'address']),
                            "rating": float(self.poi_df.loc[lunch_id, 'rating'])
                        })
                        current_time += 1.5; prev_id = lunch_id; has_lunch = True

            # --- GAP FILLING ---
            if current_time < 16.5:
                extra_pool = all_scored[~all_scored['poi_id'].isin(visited_in_day) & (all_scored['group'] == 'attraction')]
                extra_id = self._find_smart_next_poi(prev_id, extra_pool, max_time_limit=20, exclude_ids=visited_in_day)
                if extra_id:
                    visited_in_day.append(extra_id)
                    t = self.optimizer.get_time_between(prev_id, extra_id)
                    current_time += t/60.0
                    final_day_route.append({
                        "poi_id": extra_id,
                        "order": 0,
                        "type": "Visit",
                        "name": self.poi_df.loc[extra_id, 'name'] + " (Extra)",
                        "arrival_time": f"{int(current_time):02d}:{int((current_time%1)*60):02d}",
                        "travel_before_min": int(t),
                        "duration_min": 60,
                        "longitude": float(self.poi_df.loc[extra_id, 'longitude']),
                        "latitude": float(self.poi_df.loc[extra_id, 'latitude']),
                        "address": str(self.poi_df.loc[extra_id, 'address']),
                        "rating": float(self.poi_df.loc[extra_id, 'rating'])
                    })
                    current_time += 1.0; prev_id = extra_id

            # --- CAFE ---
            if not has_cafe and 15.0 <= current_time < 17.5:
                cafe_id = self._find_smart_next_poi(prev_id, pool_cafe, 'cafe', exclude_ids=visited_in_day)
                if cafe_id:
                    visited_in_day.append(cafe_id)
                    t = self.optimizer.get_time_between(prev_id, cafe_id)
                    current_time += t/60.0
                    final_day_route.append({
                        "poi_id": cafe_id,
                        "order": 0,
                        "type": "Coffee",
                        "name": self.poi_df.loc[cafe_id, 'name'],
                        "arrival_time": f"{int(current_time):02d}:{int((current_time%1)*60):02d}",
                        "travel_before_min": int(t),
                        "duration_min": 60,
                        "longitude": float(self.poi_df.loc[cafe_id, 'longitude']),
                        "latitude": float(self.poi_df.loc[cafe_id, 'latitude']),
                        "address": str(self.poi_df.loc[cafe_id, 'address']),
                        "rating": float(self.poi_df.loc[cafe_id, 'rating'])
                    })
                    current_time += 1.0; prev_id = cafe_id; has_cafe = True

            # --- ELASTIC PACING ---
            if current_time < 18.5:
                wait_min = int((18.5 - current_time) * 60)
                if final_day_route:
                    final_day_route[-1]['duration_min'] += wait_min
                    if final_day_route[-1]['type'] in ['Visit', 'Coffee']:
                        final_day_route[-1]['name'] += " Relax Time"
                current_time = 18.5

            # --- DINNER ---
            if not has_dinner:
                dinner_id = self._find_smart_next_poi(prev_id, pool_food, 'food', max_time_limit=25, exclude_ids=visited_in_day)
                if not dinner_id:
                    dinner_id = self._find_smart_next_poi(start_poi_id, pool_food, 'food', max_time_limit=15, exclude_ids=visited_in_day)
                
                if dinner_id:
                    t = self.optimizer.get_time_between(prev_id, dinner_id)
                    current_time += t/60.0
                    final_day_route.append({
                        "poi_id": dinner_id,
                        "order": 0,
                        "type": "Dinner",
                        "name": self.poi_df.loc[dinner_id, 'name'],
                        "arrival_time": f"{int(current_time):02d}:{int((current_time%1)*60):02d}",
                        "travel_before_min": int(t),
                        "duration_min": 90,
                        "longitude": float(self.poi_df.loc[dinner_id, 'longitude']),
                        "latitude": float(self.poi_df.loc[dinner_id, 'latitude']),
                        "address": str(self.poi_df.loc[dinner_id, 'address']),
                        "rating": float(self.poi_df.loc[dinner_id, 'rating'])
                    })
                    current_time += 1.5; prev_id = dinner_id; has_dinner = True

            # --- RETURN HOTEL ---
            t_home = self.optimizer.get_time_between(prev_id, start_poi_id)
            current_time += t_home / 60.0
            final_day_route.append({
                "poi_id": start_poi_id,
                "order": 0,
                "type": "Return Hotel",
                "name": "End of Day",
                "arrival_time": f"{int(current_time):02d}:{int((current_time%1)*60):02d}",
                "travel_before_min": int(t_home),
                "duration_min": 0,
                "longitude": float(self.poi_df.loc[start_poi_id, 'longitude']),
                "latitude": float(self.poi_df.loc[start_poi_id, 'latitude']),
                "address": str(self.poi_df.loc[start_poi_id, 'address']),
                "rating": float(self.poi_df.loc[start_poi_id, 'rating'])
            })

            # Re-index order & Clean data types
            for idx, item in enumerate(final_day_route): 
                item['order'] = idx + 1
            
            full_schedule.append({"day": day_idx + 1, "route": final_day_route})

        export_df = self.export_csv(full_schedule)
        self.export_df = export_df.to_csv("a.csv",index=False)  # Lưu CSV trong bộ nhớ nếu cần
        return full_schedule

    # =========================
    # EXPORT
    # =========================
    def export_csv(self, schedule):
        rows = []
        for day_plan in schedule:
            for item in day_plan['route']:
                rows.append({
                    "day": day_plan['day'],
                    "order": item['order'],
                    "poi_id": item['poi_id'],
                    "name": item['name'],
                    "type": item['type'],
                    "arrival_time": item['arrival_time'],
                    "travel_before_min": item['travel_before_min'],
                    "duration_min": item['duration_min']
                })
        return pd.DataFrame(rows)