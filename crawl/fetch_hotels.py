"""
Google Maps Location Scraper
Extracts location name, price, and address information from Google Maps search results
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

class GoogleMapsScraper:
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
                    
                    # Try to find price range ($ symbols)
                    try:
                        price_element = result.find_element(
                            By.CSS_SELECTOR, 
                            'span[aria-label*="Price"]'
                        )
                        location_data['price'] = price_element.get_attribute('aria-label')
                    except:
                        location_data['price'] = None
                    
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
                        if location_data.get('price'):
                            print(f"   Price: {location_data['price']}")
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
            
            # Get price from the overview tab first
            try:
                # Look for price displayed with various selectors
                price_selectors = [
                    'span.fontTitleLarge.Cbys4b',
                    'div.HgKUEe',
                    'span.fontHeadlineSmall',
                    'div.fontLabelMedium.pUBf3e'
                ]
                for selector in price_selectors:
                    try:
                        price_elem = self.driver.find_element(By.CSS_SELECTOR, selector)
                        text = price_elem.text.strip()
                        if text and any(char.isdigit() for char in text) and any(c in text for c in ['đ', '$', '₫']):
                            detailed_info['price_text'] = text  # Store original text
                            detailed_info['price'] = convert_price_to_number(text)  # Store numeric value
                            break
                    except:
                        continue
            except:
                pass
            
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
            except Exception as e:
                print(f"   Could not switch to Reviews tab: {e}")
            
            # Get rating from Reviews tab or overview
            try:
                # Try multiple selectors for rating
                rating_selectors = [
                    'div.fontDisplayLarge',
                    'span.ceNzKf',
                    'div.jANrlb div.fontDisplayLarge'
                ]
                for selector in rating_selectors:
                    try:
                        rating_elem = self.driver.find_element(By.CSS_SELECTOR, selector)
                        rating_text = rating_elem.text.strip()
                        if rating_text and rating_text.replace('.', '').isdigit():
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
    
    def save_to_csv(self, data, filename='locations.csv'):
        """Save scraped data to CSV file (append mode)"""
        if not data:
            print("No data to save")
            return
        
        # Get all unique keys from all dictionaries
        fieldnames = set()
        for item in data:
            fieldnames.update(item.keys())
        fieldnames = sorted(list(fieldnames))
        
        # Check if file exists to determine if we need to write headers
        file_exists = os.path.isfile(filename)
        
        with open(filename, 'a', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            
            # Write header only if file doesn't exist or is empty
            if not file_exists or os.path.getsize(filename) == 0:
                writer.writeheader()
            
            writer.writerows(data)
        
        print(f"\nData appended to {filename}")
    
    def close(self):
        """Close the browser"""
        self.driver.quit()


def main():
    """Main function to run the scraper"""
    # Initialize scraper
    scraper = GoogleMapsScraper(headless=False)  # Set to True to hide browser
    
    try:
        # Input location query
        query = input("Enter location to search (e.g., 'Điểm tham quan' or 'restaurants near me'): ")
        
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
        
        # Add default type to all locations
        for loc in locations:
            loc['type'] = 'Hotel'
        
        # Get detailed info for all locations
        print("\nFetching detailed information...")
        for i, loc in enumerate(locations):
            print(f"\nProcessing {i+1}/{len(locations)}: {loc.get('name', 'Unknown')}")
            if loc.get('url'):
                detailed = scraper.get_detailed_info(loc['url'])
                loc.update(detailed)
            time.sleep(2)  # Be respectful with requests
        
        # Save to CSV
        scraper.save_to_csv(locations, filename='hotels.csv')
        
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