import csv
import os

# --- MAPPINGS ---

ATTRACTION_KEYWORDS = [
    'Museum', 'Beach', 'Mountain', 'Pagoda', 'Church', 
    'Temple', 'Market', 'Park', 'Cathedral', 'Sanctuary',
    'Waterfall', 'Lake', 'River', 'Island', 'Cave',
    'Chùa', 'Biển', 'Núi', 'Đồi', 'Đền', 'Tháp'
]

ATTRACTION_MAP = {
    'Museum': 'Historical',
    'Beach': 'Natural',
    'Mountain': 'Natural',
    'Pagoda': 'Cultural',
    'Church': 'Cultural',
    'Temple': 'Cultural',
    'Market': 'Shopping',
    'Park': 'Natural',
    'Cathedral': 'Cultural',
    'Sanctuary': 'Cultural',
    'Waterfall': 'Natural',
    'Lake': 'Natural',
    'River': 'Natural',
    'Island': 'Natural',
    'Cave': 'Natural',
    'Chùa': 'Cultural',
    'Biển': 'Natural',
    'Núi': 'Natural',
    'Đồi': 'Natural',
    'Đền': 'Cultural',
    'Tháp': 'Cultural',
}

HOTEL_KEYWORDS = [
    'Resort', 'Homestay', 'Hostel', 'Villa', 'Apartment', 'Hotel'
]

HOTEL_MAP = {
    'Resort': 'Resort',
    'Homestay': 'Homestay',
    'Hostel': 'Hostel',
    'Villa': 'Villa',
    'Apartment': 'Apartment',
    'Hotel': 'Hotel'
}

RESTAURANT_KEYWORDS = [
    'Chay', 'Vegetarian',
    'Coffee', 'Cafe', 'Cà phê', 'Kafe',
    'Bar', 'Pub', 'Lounge', 'Club',
    'Bakery', 'Cake', 'Bánh',
    'Tea', 'Trà',
    'Phở', 'Bún', 'Mì', 'Noodle',
    'Restaurant', 'Nhà hàng', 'Quán', 'Kitchen', 'Dining'
]

RESTAURANT_MAP = {
    'Coffee': 'Coffee Shop', 'Cafe': 'Coffee Shop', 'Cà phê': 'Coffee Shop', 'Kafe': 'Coffee Shop',
    'Restaurant': 'Restaurant', 'Nhà hàng': 'Restaurant', 'Quán': 'Restaurant', 'Kitchen': 'Restaurant', 'Dining': 'Restaurant',
    'Bar': 'Bar/Pub', 'Pub': 'Bar/Pub', 'Lounge': 'Bar/Pub', 'Club': 'Bar/Pub',
    'Bakery': 'Bakery', 'Cake': 'Bakery', 'Bánh': 'Bakery',
    'Tea': 'Tea Shop', 'Trà': 'Tea Shop',
    'Phở': 'Restaurant', 'Bún': 'Restaurant', 'Mì': 'Restaurant', 'Noodle': 'Restaurant', 'Chay': 'Vegetarian', 'Vegetarian': 'Vegetarian'
}

# --- PROCESSING FUNCTION ---

def clean_file(filename, keywords, type_map):
    filepath = os.path.join(os.path.dirname(__file__), f'../{filename}')
    print(f"Processing {filepath}...")
    
    rows = []
    updated_count = 0
    
    try:
        with open(filepath, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
            
            for row in reader:
                name = row.get('name', '')
                original_type = row.get('type', '')
                
                # Check for keywords
                for keyword in keywords:
                    # Case-insensitive check
                    if keyword.lower() in name.lower():
                        new_type = type_map[keyword]
                        # Only update if different to avoid unnecessary writes/logs
                        if original_type != new_type:
                            # print(f"  Updating '{name}': {original_type} -> {new_type}")
                            row['type'] = new_type
                            updated_count += 1
                        break # Stop after first match
                
                rows.append(row)
        
        # Write back
        with open(filepath, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
            
        print(f"  Updated {updated_count} records in {filename}.\n")
        
    except Exception as e:
        print(f"  Error processing {filename}: {e}\n")

def main():
    clean_file('attractions.csv', ATTRACTION_KEYWORDS, ATTRACTION_MAP)
    clean_file('hotels.csv', HOTEL_KEYWORDS, HOTEL_MAP)
    clean_file('restaurants.csv', RESTAURANT_KEYWORDS, RESTAURANT_MAP)

if __name__ == "__main__":
    main()
