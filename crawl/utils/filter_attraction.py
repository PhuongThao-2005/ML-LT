import csv
import os

# Define the keywords to look for
KEYWORDS = [
    'Museum', 'Beach', 'Mountain', 'Pagoda', 'Church', 
    'Temple', 'Market', 'Park', 'Cathedral', 'Sanctuary',
    'Waterfall', 'Lake', 'River', 'Island', 'Cave'
]

# Define the mapping from keyword to type
TYPE_MAP = {
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
    'Cave': 'Natural'
}

def filter_attractions():
    # Path to attractions.csv (assuming this script is in data/utils/)
    input_file = os.path.join(os.path.dirname(__file__), '../attractions.csv')
    
    print(f"Reading from: {input_file}")
    
    rows = []
    updated_count = 0
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
            
            for row in reader:
                name = row.get('name', '')
                original_type = row.get('type', '')
                
                # Check for keywords
                for keyword in KEYWORDS:
                    # Case-insensitive check
                    if keyword.lower() in name.lower():
                        new_type = TYPE_MAP[keyword]
                        if original_type != new_type:
                            print(f"Updating '{name}': {original_type} -> {new_type}")
                            row['type'] = new_type
                            updated_count += 1
                        break # Stop after first match
                
                rows.append(row)
        
        # Write back to the same file
        with open(input_file, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
            
        print(f"\nSuccessfully updated {updated_count} attractions.")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    filter_attractions()
