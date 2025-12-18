"""
Google Maps Restaurant Scraper - Fixed Price Extraction
Extracts restaurant name, price range (takes maximum value), rating, and address
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import csv
import os
import re

def convert_price_to_number(price_str):
    """Convert price string to numeric value, handling ranges and K/M suffixes"""
    if not price_str:
        return None
    
    try:
        # Remove currency symbols and commas
        cleaned = re.sub(r'[đ$₫,]', '', price_str)
        
        # Handle price ranges (e.g., "100-200K" or "100K-200K")
        if '-' in cleaned:
            # Split by dash and take the maximum (last) value
            parts = cleaned.split('-')
            cleaned = parts[-1].strip()
        
        # Handle K (thousands) suffix
        if 'K' in cleaned.upper():
            number_part = re.sub(r'[Kk\s]', '', cleaned)
            multiplier = 1000
        # Handle M (millions) suffix
        elif 'M' in cleaned.upper():
            number_part = re.sub(r'[Mm\s]', '', cleaned)
            multiplier = 1000000
        else:
            # No suffix - value is as-is
            number_part = cleaned.strip()
            multiplier = 1
        
        # Convert to float and apply multiplier
        price_num = float(number_part) * multiplier
        print(f"Converted '{price_str}' to {int(price_num)}")
        return int(price_num)
    except Exception as e:
        print(f"Error converting price '{price_str}': {e}")
        return None

class GoogleMapsRestaurantScraper:
    def __init__(self, headless=False):
        """Initialize the scraper with Chrome driver"""
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, 10)
        
    def search_location(self, query):
        """Search for a location on Google Maps"""
        print(f"Searching for: {query}")
        
        # Navigate to Google Maps
        self.driver.get("https://www.google.com/maps")
        time.sleep(2)
        
        # Find search box and enter query
        search_box = self.wait.until(
            EC.presence_of_element_located((By.ID, "searchboxinput"))
        )
        search_box.clear()
        search_box.send_keys(query)
        search_box.send_keys(Keys.RETURN)
        
        # Wait for results to load
        time.sleep(3)
        
    def scroll_results(self, scrolls=3):
        """Scroll through the results panel to load more locations"""
        try:
            # Find the scrollable results panel
            scrollable_div = self.driver.find_element(
                By.CSS_SELECTOR, 
                'div[role="feed"]'
            )
            
            for i in range(scrolls):
                self.driver.execute_script(
                    'arguments[0].scrollTop = arguments[0].scrollHeight', 
                    scrollable_div
                )
                time.sleep(2)
                print(f"Scrolled {i+1}/{scrolls}")
                
        except Exception as e:
            print(f"Error scrolling: {e}")
    
    def extract_locations(self):
        """Extract location information from search results"""
        locations = []
        
        try:
            # Wait for results to appear
            time.sleep(2)
            
            # Find all location result elements
            results = self.driver.find_elements(
                By.CSS_SELECTOR, 
                'div[role="feed"] > div > div > a'
            )
            
            print(f"Found {len(results)} results")
            
            for idx, result in enumerate(results):
                try:
                    location_data = {}
                    
                    # Get the aria-label which contains most info
                    aria_label = result.get_attribute('aria-label')
                    
                    if aria_label:
                        # Extract name (first part before ratings)
                        location_data['name'] = aria_label.split('.')[0].strip()
                    
                    # Get URL
                    location_data['url'] = result.get_attribute('href')
                    
                    # Extract coordinates from URL (multiple patterns)
                    try:
                        url = location_data.get('url', '')
                        # Pattern 1: @lat,lng format
                        coord_match = re.search(r'@(-?\d+\.\d+),(-?\d+\.\d+)', url)
                        if not coord_match:
                            # Pattern 2: 3d param format (3d<lat>!4d<lng>)
                            coord_match = re.search(r'!3d(-?\d+\.?\d*)!4d(-?\d+\.?\d*)', url)
                        if coord_match:
                            location_data['latitude'] = coord_match.group(1)
                            location_data['longitude'] = coord_match.group(2)
                    except Exception as e:
                        pass
                    
                    if location_data.get('name'):
                        locations.append(location_data)
                        print(f"\n{idx+1}. {location_data['name']}")
                        if location_data.get('latitude') and location_data.get('longitude'):
                            print(f"   Coordinates: {location_data['latitude']}, {location_data['longitude']}")
                    
                except Exception as e:
                    print(f"Error extracting location {idx}: {e}")
                    continue
            
        except Exception as e:
            print(f"Error finding results: {e}")
        
        return locations
    
    def get_detailed_info(self, location_url):
        """Get detailed information by visiting the location page"""
        try:
            self.driver.get(location_url)
            time.sleep(3)
            
            detailed_info = {}
            
            # Get name
            try:
                name = self.driver.find_element(
                    By.CSS_SELECTOR, 
                    'h1.fontHeadlineLarge'
                ).text
                detailed_info['name'] = name
            except:
                pass
            
            # Get price - IMPROVED STRATEGY
            try:
                price_text = None
                price_str = None
                
                print("   Looking for price...")
                
                # Strategy 1: Search entire page body text for price pattern
                try:
                    page_text = self.driver.find_element(By.TAG_NAME, 'body').text
                    # Look for "per person" with price nearby
                    lines = page_text.split('\n')
                    for line in lines:
                        if 'per person' in line.lower() and any(c in line for c in ['đ', '$', '₫']):
                            price_text = line.strip()
                            print(f"   Found price in page text: {price_text}")
                            break
                except Exception as e:
                    print(f"   Strategy 1 failed: {e}")
                
                # Strategy 2: Look for aria-labels with "per person"
                if not price_text:
                    try:
                        all_elements = self.driver.find_elements(By.XPATH, "//*[@aria-label]")
                        for elem in all_elements:
                            aria_label = elem.get_attribute('aria-label')
                            if aria_label and 'per person' in aria_label.lower():
                                if any(c in aria_label for c in ['đ', '$', '₫']):
                                    price_text = aria_label
                                    print(f"   Found price in aria-label: {price_text}")
                                    break
                    except Exception as e:
                        print(f"   Strategy 2 failed: {e}")
                
                # Extract and save price
                if price_text:
                    # Extract the second (maximum) value from range
                    # If there's a range, pick the second (max) price
                    if re.search(r'[-–—]', price_text):
                        # find all price-like tokens (with optional currency and K/M)
                        matches = re.findall(r'([đ$₫]?\s*\d[\d,\.]*\s*[KkMm]?)', price_text)
                        if matches:
                            # take the last match as the maximum value
                            price_str = matches[-1].strip()
                        else:
                            # fallback: split on any dash and search the last part
                            parts = re.split(r'[-–—]', price_text)
                            last_part = parts[-1] if parts else price_text
                            m = re.search(r'([đ$₫]?\s*\d[\d,\.]*\s*[KkMm]?)', last_part)
                            if m:
                                price_str = m.group(1).strip()
                    else:
                        # Single price, not a range
                        match = re.search(r'[đ$₫]\d[\d,\.]*[KkMm]?', price_text)
                        if match:
                            price_str = match.group(0)
                    
                    if price_str:
                        detailed_info['price_text'] = price_str
                        detailed_info['price'] = convert_price_to_number(price_str)
                        print(f"   ✓ Saved price: {price_str} = {detailed_info['price']}")
                    else:
                        print(f"   ✗ Could not extract price from: {price_text}")
                else:
                    print(f"   ✗ No price found on page")
                    
            except Exception as e:
                print(f"   Error in price extraction: {e}")
            
            # Click on Reviews tab to get rating
            try:
                # Find and click the Reviews tab
                reviews_tab = self.driver.find_element(
                    By.XPATH, 
                    "//button[@role='tab' and contains(., 'Reviews')]"
                )
                reviews_tab.click()
                time.sleep(2)
                
                # Get rating from Reviews tab
                rating_selectors = [
                    'div.fontDisplayLarge',
                    'span.ceNzKf',
                    'div.jANrlb div.fontDisplayLarge'
                ]
                for selector in rating_selectors:
                    try:
                        rating_elem = self.driver.find_element(By.CSS_SELECTOR, selector)
                        rating_text = rating_elem.text.strip()
                        if rating_text and rating_text.replace('.', '').replace(',', '').isdigit():
                            detailed_info['rating'] = rating_text
                            break
                    except:
                        continue
                
            except:
                pass
            
            # Go back to Overview tab for other info
            try:
                overview_tab = self.driver.find_element(
                    By.XPATH,
                    "//button[@role='tab' and contains(., 'Overview')]"
                )
                overview_tab.click()
                time.sleep(1)
            except:
                pass
            
            # Get address
            try:
                address = self.driver.find_element(
                    By.CSS_SELECTOR, 
                    'button[data-item-id="address"]'
                ).get_attribute('aria-label')
                detailed_info['address'] = address.replace('Address: ', '')
            except:
                pass
            
            # Get phone
            try:
                phone = self.driver.find_element(
                    By.CSS_SELECTOR, 
                    'button[data-item-id*="phone"]'
                ).get_attribute('aria-label')
                detailed_info['phone'] = phone.replace('Phone: ', '')
            except:
                pass
            
            # Get website
            try:
                website = self.driver.find_element(
                    By.CSS_SELECTOR, 
                    'a[data-item-id="authority"]'
                ).get_attribute('href')
                detailed_info['website'] = website
            except:
                pass
            
            # Extract coordinates from URL (multiple patterns)
            try:
                # Pattern 1: @lat,lng format
                coord_match = re.search(r'@(-?\d+\.\d+),(-?\d+\.\d+)', location_url)
                if not coord_match:
                    # Pattern 2: 3d param format (3d<lat>!4d<lng>)
                    coord_match = re.search(r'!3d(-?\d+\.?\d*)!4d(-?\d+\.?\d*)', location_url)
                if coord_match:
                    detailed_info['latitude'] = coord_match.group(1)
                    detailed_info['longitude'] = coord_match.group(2)
                    print(f"   Coordinates: {detailed_info['latitude']}, {detailed_info['longitude']}")
                else:
                    print(f"   Could not extract coordinates from URL")
            except Exception as e:
                print(f"   Error extracting coordinates: {e}")
            
            return detailed_info
            
        except Exception as e:
            print(f"Error getting detailed info: {e}")
            return {}
    
    def save_to_csv(self, data, filename='restaurants.csv'):
        """Save scraped data to CSV file (append mode)"""
        if not data:
            print("No data to save")
            return
        
        # Get all unique keys from all dictionaries
        new_fieldnames = set()
        for item in data:
            new_fieldnames.update(item.keys())
        
        # Check if file exists and read existing headers
        file_exists = os.path.isfile(filename) and os.path.getsize(filename) > 0
        
        if file_exists:
            # Read existing headers
            with open(filename, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                existing_fieldnames = set(reader.fieldnames or [])
            
            # Merge with new fields
            all_fieldnames = sorted(list(existing_fieldnames.union(new_fieldnames)))
            
            # If new fields were added, we need to rewrite the file
            if new_fieldnames - existing_fieldnames:
                print(f"Adding new columns: {', '.join(new_fieldnames - existing_fieldnames)}")
                # Read all existing data
                with open(filename, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    existing_data = list(reader)
                
                # Write everything back with new headers
                with open(filename, 'w', encoding='utf-8', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=all_fieldnames)
                    writer.writeheader()
                    writer.writerows(existing_data)
                    writer.writerows(data)
            else:
                # Just append with existing headers
                with open(filename, 'a', encoding='utf-8', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=all_fieldnames)
                    writer.writerows(data)
        else:
            # New file, write with headers
            fieldnames = sorted(list(new_fieldnames))
            with open(filename, 'w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)
        
        print(f"\nData saved to {filename}")
    
    def close(self):
        """Close the browser"""
        self.driver.quit()


def main():
    """Main function to run the scraper"""
    # Initialize scraper
    scraper = GoogleMapsRestaurantScraper(headless=False)  # Set to True to hide browser
    
    try:
        # Input restaurant type
        print("Select type:")
        print("1. Restaurant")
        print("2. Coffee Shop")
        type_choice = input("Enter your choice (1 or 2): ").strip()
        
        if type_choice == "2":
            restaurant_type = "Coffee Shop"
            default_query = "Coffee shops"
        else:
            restaurant_type = "Restaurant"
            default_query = "Restaurants"
        
        # Input location query
        query = input(f"Enter search query (e.g., '{default_query}'): ")
        
        # Search for location
        scraper.search_location(query)
        
        # Scroll to load more results
        scrolls = int(input("How many times to scroll? (recommended 2-5): ") or "3")
        scraper.scroll_results(scrolls)
        
        # Extract location data
        locations = scraper.extract_locations()
        
        print(f"\n{'='*60}")
        print(f"Total locations found: {len(locations)}")
        print(f"{'='*60}")
        
        # Add type to all locations
        for loc in locations:
            loc['type'] = restaurant_type
        
        # Get detailed info for all locations
        print("\nFetching detailed information...")
        for i, loc in enumerate(locations):
            print(f"\nProcessing {i+1}/{len(locations)}: {loc.get('name', 'Unknown')}")
            if loc.get('url'):
                detailed = scraper.get_detailed_info(loc['url'])
                loc.update(detailed)
                print(f"Location data: {loc.keys()}")  # Debug: show what fields we have
            time.sleep(2)  # Be respectful with requests
        
        # Debug: Show sample of what we're saving
        if locations:
            print(f"\nSample data to save (first location):")
            print(f"Keys: {locations[0].keys()}")
            print(f"Price: {locations[0].get('price')}")
            print(f"Price text: {locations[0].get('price_text')}")
        
        # Save to CSV
        scraper.save_to_csv(locations)
        
        print("\n" + "="*60)
        print("Scraping completed successfully!")
        print("="*60)
        
    except KeyboardInterrupt:
        print("\n\nScraping interrupted by user")
    except Exception as e:
        print(f"\nError: {e}")
    finally:
        scraper.close()


if __name__ == "__main__":
    main()