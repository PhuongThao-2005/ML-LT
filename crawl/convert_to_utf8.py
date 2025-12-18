import pandas as pd

# Read the CSV file
df = pd.read_csv('POI.csv', encoding='utf-8')

# Save the CSV file with UTF-8 encoding, ensuring proper encoding for name and address columns
df.to_csv('POI.csv', index=False, encoding='utf-8-sig')

print("Successfully converted hotels.csv to UTF-8 encoding")
print(f"Total rows: {len(df)}")
print(f"\nFirst few rows:")
print(df[['name', 'address']].head())
