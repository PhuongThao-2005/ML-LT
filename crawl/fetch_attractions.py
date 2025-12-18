"""
Google Maps Attraction Scraper
Extracts attraction name, rating, address, and price information from Google Maps search results
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
    """Convert price string to numeric value"""
    if not price_str:
        return None
    
    try:
        # Remove currency symbols
        price_str = re.sub(r'[đ$₫,\s]', '', price_str)
        
        # Handle K (thousands) and M (millions)
        if 'K' in price_str.upper():
            price_str = price_str.upper().replace('K', '')
            multiplier = 1000
        elif 'M' in price_str.upper():
            price_str = price_str.upper().replace('M', '')
            multiplier = 1000000
        else:
            multiplier = 1
        
        # Convert to float and apply multiplier
        price_num = float(price_str) * multiplier
        return int(price_num)
    except:
        return None

class GoogleMapsAttractionScraper:
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
                        
                        # Try to extract rating
                        if '★' in aria_label or 'stars' in aria_label.lower():
                            parts = aria_label.split('·')
                            for part in parts:
                                if '★' in part or 'stars' in part.lower():
                                    location_data['rating'] = part.strip()
                                    break
                    
                    # Try to find address
                    try:
                        # Address is usually in specific div elements
                        address_elements = result.find_elements(
                            By.CSS_SELECTOR, 
                            'div.fontBodyMedium span'
                        )
                        for elem in address_elements:
                            text = elem.text
                            if text and len(text) > 10:  # Address usually longer
                                location_data['address'] = text
                                break
                    except:
                        location_data['address'] = None
                    
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
                        if location_data.get('rating'):
                            print(f"   Rating: {location_data['rating']}")
                        if location_data.get('address'):
                            print(f"   Address: {location_data['address']}")
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
            
            # Initialize price_found flag
            price_found = False
            
            # First, try to get price from the Tickets tab
            try:
                # Click on Tickets tab
                tickets_tab = self.driver.find_element(
                    By.XPATH, 
                    "//button[@role='tab' and contains(., 'Tickets')]"
                )
                tickets_tab.click()
                time.sleep(2)
                print("   Switched to Tickets tab")
                
                # Try to get content from div with class "drwWxc" and "NFP9ae"
                try:
                    price_divs = self.driver.find_elements(By.CLASS_NAME, "drwWxc")
                    if price_divs:
                        print(f"   Found {len(price_divs)} div(s) with class 'drwWxc':")
                        for idx, div in enumerate(price_divs):
                            content = div.text.strip()
                            print(f"   drwWxc[{idx}]: {content}")
                        
                        # Get the first price
                        if len(price_divs) > 0:
                            first_price_text = price_divs[0].text.strip()
                            print(f"   First price text: {first_price_text}")
                            
                            # Extract price value and currency
                            # Match $ followed by numbers
                            dollar_match = re.search(r'\$\s*([\d,\.]+)', first_price_text)
                            # Match ₫ before or after numbers (₫100,000 or 100,000₫)
                            dong_match = re.search(r'₫\s*([\d,\.]+)|([\d,\.]+)\s*₫', first_price_text)
                            
                            if dollar_match:
                                # Extract dollar amount and convert to VND
                                price_str = dollar_match.group(1).replace(',', '')
                                price_value = float(price_str)
                                converted_price = price_value * 25000
                                # Store both text and numeric value
                                detailed_info['price_text'] = f"${price_value:,.0f}"
                                detailed_info['price'] = int(converted_price)
                                print(f"   Price converted: ${price_value} → {converted_price:,.0f} VND")
                                price_found = True
                                print(f"   DEBUG: price_found set to {price_found} from drwWxc")
                            elif dong_match:
                                # Keep original dong price - check both groups
                                price_str = (dong_match.group(1) or dong_match.group(2)).replace(',', '')
                                # Store both text and numeric value
                                detailed_info['price_text'] = f"₫{price_str}"
                                detailed_info['price'] = convert_price_to_number(price_str)
                                print(f"   Price kept: {detailed_info['price_text']} (numeric: {detailed_info['price']})")
                                price_found = True
                                print(f"   DEBUG: price_found set to {price_found} from drwWxc")
                    
                    # Also check for class "NFP9ae"
                    nfp9ae_divs = self.driver.find_elements(By.CLASS_NAME, "NFP9ae")
                    if nfp9ae_divs:
                        print(f"   Found {len(nfp9ae_divs)} div(s) with class 'NFP9ae':")
                        for idx, div in enumerate(nfp9ae_divs):
                            content = div.text.strip()
                            print(f"   NFP9ae[{idx}]: {content}")
                        
                        # If price not found yet, try to extract from NFP9ae
                        if not price_found and len(nfp9ae_divs) > 0:
                            first_nfp9ae_text = nfp9ae_divs[0].text.strip()
                            print(f"   First NFP9ae text: {first_nfp9ae_text}")
                            
                            # Extract price value and currency - match ₫ before numbers too
                            dollar_match = re.search(r'\$\s*([\d,\.]+)', first_nfp9ae_text)
                            dong_match = re.search(r'₫\s*([\d,\.]+)|([\d,\.]+)\s*₫', first_nfp9ae_text)
                            
                            if dollar_match:
                                price_str = dollar_match.group(1).replace(',', '')
                                price_value = float(price_str)
                                converted_price = price_value * 25000
                                # Store both text and numeric value
                                detailed_info['price_text'] = f"${price_value:,.0f}"
                                detailed_info['price'] = int(converted_price)
                                print(f"   Price converted from NFP9ae: ${price_value} → {converted_price:,.0f} VND")
                                price_found = True
                                print(f"   DEBUG: price_found set to {price_found}")
                            elif dong_match and (dong_match.group(1) or dong_match.group(2)):
                                price_str = (dong_match.group(1) or dong_match.group(2)).replace(',', '')
                                # Store both text and numeric value
                                detailed_info['price_text'] = f"₫{price_str}"
                                detailed_info['price'] = convert_price_to_number(price_str)
                                print(f"   Price kept from NFP9ae: {detailed_info['price_text']} (numeric: {detailed_info['price']})")
                                price_found = True
                                print(f"   DEBUG: price_found set to {price_found}")
                except Exception as e:
                    print(f"   Could not find div with class 'drwWxc' or 'NFP9ae': {e}")
                    print(f"   DEBUG: price_found status after exception: {price_found}")
                        
            except Exception as e:
                print(f"   Could not access Tickets tab: {e}")
            
            # Click on Reviews tab to get rating
            try:
                # Find and click the Reviews tab
                reviews_tab = self.driver.find_element(
                    By.XPATH, 
                    "//button[@role='tab' and contains(., 'Reviews')]"
                )
                reviews_tab.click()
                time.sleep(2)
                print("   Switched to Reviews tab")
                
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
                
            except Exception as e:
                print(f"   Could not get rating: {e}")
            
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
            
            # Check if price was found and report
            print(f"   DEBUG: Final price_found value: {price_found}")
            print(f"   DEBUG: Price_text in detailed_info: {detailed_info.get('price_text', 'N/A')}")
            print(f"   DEBUG: Price (numeric) in detailed_info: {detailed_info.get('price', 'N/A')}")
            if price_found:
                print(f"   ✓ Price successfully saved: {detailed_info.get('price_text', 'N/A')} (numeric: {detailed_info.get('price', 'N/A')})")
            else:
                print("   ⚠ Price not found for this location")
            
            return detailed_info
            
        except Exception as e:
            print(f"Error getting detailed info: {e}")
            return {}
    
    def save_to_csv(self, data, filename='attractions.csv'):
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
    scraper = GoogleMapsAttractionScraper(headless=False)  # Set to True to hide browser
    
    try:
        # Input location query
        query = input("Enter attraction search query (e.g., 'Attractions in Da Lat' or 'Tourist spots in Hanoi'): ")
        
        # Input attraction type
        attraction_type = input("Enter attraction type (e.g., 'Natural', 'Historical', 'Cultural', 'Entertainment'): ")
        
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
            loc['type'] = attraction_type
        
        # Get detailed info for all locations
        print("\nFetching detailed information...")
        for i, loc in enumerate(locations):
            print(f"\nProcessing {i+1}/{len(locations)}: {loc.get('name', 'Unknown')}")
            if loc.get('url'):
                detailed = scraper.get_detailed_info(loc['url'])
                loc.update(detailed)
                print(f"Location data: {loc.keys()}")  # Debug: show what fields we have
            time.sleep(2)  # Be respectful with requests
        
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