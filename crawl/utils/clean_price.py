import csv
import os

def clean_price(filename, default_value):
    filepath = os.path.join(os.path.dirname(__file__), f'../{filename}')
    print(f"Processing {filepath}...")
    
    rows = []
    updated_count = 0
    
    try:
        with open(filepath, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
            
            for row in reader:
                price = row.get('price', '')
                
                if not price or price.strip() == '':
                    row['price'] = default_value
                    updated_count += 1
                
                rows.append(row)
        
        with open(filepath, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
            
        print(f"  Updated {updated_count} records in {filename} (set to '{default_value}').\n")
        
    except Exception as e:
        print(f"  Error processing {filename}: {e}\n")

def main():
    # Attractions: empty -> 0
    clean_price('attractions.csv', '0')
    
    # Hotels: empty -> null
    clean_price('hotels.csv', 'null')
    
    # Restaurants: empty -> null
    clean_price('restaurants.csv', 'null')

if __name__ == "__main__":
    main()
