import requests
import json
import time

# URL API của bạn
API_URL = "http://127.0.0.1:8000/api/chat-plan"

def test_api_response(query_text):
    print(f"\n{'='*50}")
    print(f"💬 Gửi câu hỏi: {query_text}")
    print(f"{'='*50}")

    payload = {"query": query_text}

    try:
        response = requests.post(API_URL, json=payload)
        
        if response.status_code == 200:
            res_data = response.json()
            
            # Kiểm tra status từ server
            if res_data.get("status") == "success":
                print(f"✅ KẾT QUẢ TỪ SERVER:")
                print(f"📍 Thành phố: {res_data.get('city').upper()}")
                print(f"🏨 Điểm xuất phát: {res_data.get('start_point')}")
                print(f"📅 Số ngày: {res_data.get('days')}")
                
                # Duyệt qua lịch trình (Itinerary)
                itinerary = res_data.get("itinerary", [])
                for day_data in itinerary:
                    day_num = day_data.get("day")
                    route = day_data.get("route", [])
                    
                    print(f"\n--- 🗓️ NGÀY {day_num} ({len(route)} địa điểm) ---")
                    
                    for step in route:
                        # Lấy thông tin từng bước
                        arrival = step.get("arrival_time")
                        name = step.get("name")
                        poi_type = step.get("type")
                        duration = step.get("duration_min")
                        travel = step.get("travel_before_min", 0)

                        # Định dạng hiển thị
                        line = f"  🕒 {arrival} | {name.ljust(30)} | Type: {poi_type.get('type') if isinstance(poi_type, dict) else poi_type}"
                        if travel > 0:
                            line += f" (🚗 Di chuyển: {travel}p)"
                        
                        print(line)
                        
                        # Nếu là điểm tham quan hoặc ăn uống thì in thời gian ở lại
                        if duration > 0:
                            print(f"      ┕━━ ⌛ Ở lại: {duration} phút")
            else:
                print(f"❌ Server báo lỗi: {res_data.get('message')}")
        
        elif response.status_code == 404:
            print(f"❌ Lỗi 404: {response.json().get('detail')}")
        else:
            print(f"❌ Lỗi HTTP {response.status_code}: {response.text}")

    except Exception as e:
        print(f"❌ Lỗi kết nối hoặc xử lý: {str(e)}")

if __name__ == "__main__":
    # Test 1: Câu hỏi thực tế cho Đà Lạt
    test_api_response("Lên kế hoạch đi Đà Lạt 3 ngày, ưu tiên cafe và thiên nhiên")
    
    # Nghỉ 2s tránh bị Gemini khóa vì gọi quá nhanh
    time.sleep(2)
    
    # Test 2: Câu hỏi cho Hà Nội
    test_api_response("Đi Hà Nội 2 ngày ăn uống tiết kiệm")