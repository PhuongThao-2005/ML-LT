from google import genai
import json
import re

def build_prompt(user_text):
    return f"""
Bạn là trợ lý lập lịch trình du lịch.

NHIỆM VỤ BẮT BUỘC:
- Trích xuất thông tin từ câu người dùng
- KHÔNG được để trống bất kỳ trường nào
- Nếu người dùng không cung cấp → TỰ ĐIỀN GIÁ TRỊ PHỔ BIẾN
- user_type có thể là NHIỀU loại
- CHỈ trả về JSON đúng schema, không thêm chữ
=====================
SCHEMA JSON (BẮT BUỘC – KHÔNG NULL)
=====================
{{
  "filled": {{
    "user_city": string,
    "user_type": list[string],
    "user_price": 0 | 1 | 2,
    "total_days": number
  }}
}}

=====================
QUY ƯỚC CHUẨN HÓA
=====================

1. user_city:
- lowercase, không dấu
- CHỈ ĐƯỢC CHỌN 1 trong danh sách sau:
  ba dinh, ba ria vung tau, binh duong, da lat, da nang,
  dong nai, ha giang, ha noi, hai phong, ho chi minh,
  hoi an, hue, hung yen, khanh hoa, lai chau, lam dong,
  lao cai, long an, nha trang, quang nam, tan thanh,
  tay ninh, tien giang, vinh
- Nếu KHÔNG nhắc → tự chọn thành phố phù hợp (ưu tiên Hà Nội, Hồ Chí Minh, Đà Nẵng)

2. user_price:
- 0 = rẻ, tiết kiệm
- 1 = trung bình (DEFAULT)
- 2 = cao, sang
- Nếu không nhắc → dùng 1

3. user_type:
CHỈ ĐƯỢC CHỌN từ danh sách (có thể nhiều):
- apartment
- attraction
- bakery
- bar/pub
- coffee shop
- cultural
- entertainment
- historical
- homestay
- hostel
- hotel
- natural
- resort
- restaurant
- shopping
- tea shop
- vegetarian
- villa

Mapping ví dụ:
- ăn uống, quán ăn → restaurant
- cafe, cà phê → coffee shop
- trà sữa → tea shop
- đi chơi, giải trí → entertainment
- tham quan → attraction
- thiên nhiên, biển, núi → natural

Nếu KHÔNG nhắc type → dùng ["attraction", "restaurant"]

4. total_days:
- Nếu người dùng nhắc → lấy số đó
- Nếu KHÔNG nhắc → dùng 3

=====================
QUY TẮC TRẢ LỜI
=====================
- CHỈ TRẢ JSON
- KHÔNG markdown
- KHÔNG giải thích
- KHÔNG text thừa

USER TEXT:
\"{user_text}\"
"""

def call_gemini(user_text):
    try:
        client = genai.Client(api_key="AIzaSyA9ybFOe0BXP2AxmPDgeiVVpomn-p5-yt0")
        
        # Gọi model
        response = client.models.generate_content(
            model="gemini-2.5-flash", # Hoặc "gemini-1.5-flash"
            contents=build_prompt(user_text)
        )
        
        raw_text = response.text
        # print("Raw Gemini:", raw_text) # Bật lên nếu muốn debug

        # --- BƯỚC QUAN TRỌNG: LÀM SẠCH JSON ---
        # Xóa ```json và ``` ở đầu cuối nếu có
        cleaned_text = re.sub(r"```json\s*|\s*```", "", raw_text).strip()
        
        # Parse JSON
        data = json.loads(cleaned_text)
        
        # Trả về phần 'filled' để code bên ngoài dùng trực tiếp được
        return data.get("filled", {})

    except Exception as e:
        print(f"Lỗi Gemini: {e}")
        # Trả về mặc định nếu lỗi
        return {
            "user_city": "ha noi",
            "user_type": ["attraction"],
            "user_price": 1,
            "total_days": 3
        }