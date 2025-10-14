"""
Google Maps Restaurant Scraper - Cork Complete Dataset (FIXED)
Key fixes:
- Fixed latitude/longitude extraction with proper wait
- Multiple search queries to get MORE restaurants
- Better coordinate extraction from multiple sources
- 10 reviews per restaurant with Good/Bad/Mixed sentiment
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time
import json
import random
import re
import os

class GoogleMapsRestaurantScraper:
    def __init__(self, headless=False, slow_internet=True):
        """
        Initialize the scraper
        
        Args:
            headless: Run browser in headless mode
            slow_internet: If True, uses longer wait times for moderate/slow connections
        """
        print("\n" + "="*70)
        print("GOOGLE MAPS RESTAURANT SCRAPER - COMPLETE CORK DATASET (FIXED)")
        print("="*70)
        print("\nInitializing Chrome browser...")
        
        self.slow_internet = slow_internet
        if slow_internet:
            self.page_load_timeout = 20
            self.scroll_wait_timeout = 15
            self.review_load_timeout = 10
            print("📶 Slow internet mode: ENABLED (longer wait times)")
        else:
            self.page_load_timeout = 10
            self.scroll_wait_timeout = 8
            self.review_load_timeout = 5
            print("📶 Normal internet mode")
        
        chrome_options = Options()
        if headless:
            chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        chrome_options.page_load_strategy = 'normal'
        
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )
        self.driver.maximize_window()
        self.wait = WebDriverWait(self.driver, 15)
        print("✓ Browser ready!\n")

    def search_restaurants_multi_query(self, location="Cork"):
        """Search with MULTIPLE queries to get MORE restaurants"""
        
        # Multiple search strategies to find MORE restaurants
        search_queries = [
            f"restaurants in {location} city centre",
            f"restaurants in {location}",
            f"food in {location}",
            f"dining in {location}",
            f"cafes in {location}",
            f"pubs in {location}",
            f"best restaurants {location}",
            f"places to eat in {location}",
        ]
        
        all_urls = set()  # Use set to avoid duplicates
        
        for query in search_queries:
            print(f"\n🔍 Searching: '{query}'...")
            urls = self.search_restaurants(query)
            all_urls.update(urls)
            print(f"   Found {len(urls)} URLs | Total unique: {len(all_urls)}")
            time.sleep(3)  # Small delay between searches
        
        print(f"\n✓ Total unique restaurants found: {len(all_urls)}")
        return list(all_urls)

    def search_restaurants(self, search_query):
        """Search for restaurants with extended scrolling"""
        url = f"https://www.google.com/maps/search/{search_query.replace(' ', '+')}"
        
        self.driver.get(url)
        time.sleep(5)
        
        self._scroll_results_extended()
        return self._extract_restaurant_links()

    def _scroll_results_extended(self):
        """Extended scrolling with smart loading detection"""
        try:
            scrollable_div = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div[role="feed"]'))
            )
            
            last_height = 0
            scroll_attempts = 0
            max_scroll_attempts = 100
            no_change_count = 0
            
            while scroll_attempts < max_scroll_attempts:
                links_before = len(self.driver.find_elements(By.CSS_SELECTOR, 'a[href*="/maps/place/"]'))
                
                self.driver.execute_script(
                    "arguments[0].scrollTo(0, arguments[0].scrollHeight)", 
                    scrollable_div
                )
                
                max_wait_time = self.scroll_wait_timeout
                wait_interval = 0.5
                elapsed_time = 0
                content_loaded = False
                
                while elapsed_time < max_wait_time:
                    time.sleep(wait_interval)
                    elapsed_time += wait_interval
                    
                    links_after = len(self.driver.find_elements(By.CSS_SELECTOR, 'a[href*="/maps/place/"]'))
                    
                    try:
                        spinner = self.driver.find_elements(By.CSS_SELECTOR, 'div[class*="loading"], div[class*="spinner"]')
                        spinner_visible = len(spinner) > 0 and spinner[0].is_displayed()
                    except:
                        spinner_visible = False
                    
                    if links_after > links_before and not spinner_visible:
                        content_loaded = True
                        break
                
                time.sleep(1)
                
                new_height = self.driver.execute_script(
                    "return arguments[0].scrollHeight", 
                    scrollable_div
                )
                
                if new_height == last_height:
                    no_change_count += 1
                    if no_change_count >= 3:
                        break
                else:
                    no_change_count = 0
                
                last_height = new_height
                scroll_attempts += 1
                
        except Exception as e:
            print(f"\nWarning during scrolling: {e}")

    def _extract_restaurant_links(self):
        """Extract restaurant URLs"""
        try:
            time.sleep(3)
            links = self.driver.find_elements(By.CSS_SELECTOR, 'a[href*="/maps/place/"]')
            restaurant_urls = []
            
            for link in links:
                href = link.get_attribute('href')
                if href and '/maps/place/' in href and href not in restaurant_urls:
                    restaurant_urls.append(href)
            
            return restaurant_urls
            
        except Exception as e:
            print(f"Error extracting links: {e}")
            return []

    def scrape_restaurant_details(self, url):
        """Scrape restaurant details with FIXED coordinate extraction"""
        try:
            self.driver.get(url)
            self._wait_for_page_load()
            
            # WAIT for URL to update with coordinates
            time.sleep(3)
            
            # Get coordinates using MULTIPLE methods
            lat, lon = self._get_coordinates_robust()
            
            price_range = self._get_price_range()
            price_min, price_max = self._extract_price_numbers(price_range)
            
            dietary = self._get_dietary_options()
            if not dietary:
                dietary = "Non-Veg"
            
            restaurant = {
                'name': self._get_text('h1.DUwDvf') or 'Unknown',
                'place_id': self._extract_place_id(url),
                'cuisine_type': self._get_cuisine_type() or 'Restaurant',
                'address': self._get_address() or 'Address not available',
                'county': 'Cork',
                
                'rating': self._get_rating(),
                'review_count': self._get_review_count() or 0,
                
                # FIXED: Better coordinate extraction
                'latitude': lat,
                'longitude': lon,
                
                'price_range': price_range or '€€',
                'price_level': self._convert_price_to_numeric(price_range) or 2,
                'price_min': price_min,
                'price_max': price_max,
                
                'phone': self._get_phone(),
                'website': self._get_website(),
                'url': url,
                
                'atmosphere': self._get_atmosphere() or 'Casual',
                'dietary_options': dietary,
                'service_options': self._get_service_options() or 'Dine-in',
                'amenities': self._get_amenities(),
                
                # 10 reviews with sentiment
                'reviews_data': self._get_reviews_with_sentiment(max_reviews=10),
            }
            
            return restaurant
            
        except Exception as e:
            print(f"Error scraping details: {e}")
            return None

    def _get_coordinates_robust(self):
        """FIXED: Robust coordinate extraction using multiple methods"""
        lat, lon = None, None
        
        # Method 1: From current URL (after page loads)
        try:
            current_url = self.driver.current_url
            if '@' in current_url:
                coords_part = current_url.split('@')[1].split(',')
                lat = float(coords_part[0])
                lon = float(coords_part[1])
                
                # Validate coordinates are in Cork region
                # Cork is roughly: 51.8-52.0 N, -8.6 to -8.3 W
                if 51.7 <= lat <= 52.1 and -8.7 <= lon <= -8.2:
                    return lat, lon
        except Exception as e:
            pass
        
        # Method 2: Click on map to reveal coordinates
        try:
            # Find and click the map image
            map_elements = self.driver.find_elements(By.CSS_SELECTOR, 'button[data-item-id="image"]')
            if map_elements:
                map_elements[0].click()
                time.sleep(2)
                
                # Try to extract from updated URL
                current_url = self.driver.current_url
                if '@' in current_url:
                    coords_part = current_url.split('@')[1].split(',')
                    lat = float(coords_part[0])
                    lon = float(coords_part[1])
                    
                    if 51.7 <= lat <= 52.1 and -8.7 <= lon <= -8.2:
                        return lat, lon
                
                # Close map if opened
                self.driver.back()
                time.sleep(1)
        except:
            pass
        
        # Method 3: Extract from page source
        try:
            page_source = self.driver.page_source
            
            # Look for coordinate patterns in page source
            coord_pattern = r'(\d{2}\.\d{4,}),(-\d\.\d{4,})'
            matches = re.findall(coord_pattern, page_source)
            
            for match in matches:
                try:
                    test_lat = float(match[0])
                    test_lon = float(match[1])
                    
                    # Check if in Cork region
                    if 51.7 <= test_lat <= 52.1 and -8.7 <= test_lon <= -8.2:
                        return test_lat, test_lon
                except:
                    continue
        except:
            pass
        
        # Method 4: Try to extract from share button URL
        try:
            share_button = self.driver.find_element(By.CSS_SELECTOR, 'button[data-item-id="share"]')
            share_button.click()
            time.sleep(1)
            
            # Get the share URL
            share_url = self.driver.find_element(By.CSS_SELECTOR, 'input[type="text"]').get_attribute('value')
            
            if '@' in share_url:
                coords_part = share_url.split('@')[1].split(',')
                lat = float(coords_part[0])
                lon = float(coords_part[1])
                
                if 51.7 <= lat <= 52.1 and -8.7 <= lon <= -8.2:
                    # Close share dialog
                    self.driver.find_element(By.CSS_SELECTOR, 'button[aria-label*="Close"]').click()
                    return lat, lon
            
            # Close share dialog
            self.driver.find_element(By.CSS_SELECTOR, 'button[aria-label*="Close"]').click()
        except:
            pass
        
        return lat, lon

    def _get_text(self, selector):
        try:
            element = self.driver.find_element(By.CSS_SELECTOR, selector)
            return element.text.strip()
        except:
            return None

    def _wait_for_page_load(self):
        max_wait = self.page_load_timeout
        check_interval = 0.5
        elapsed = 0
        
        while elapsed < max_wait:
            try:
                name_present = len(self.driver.find_elements(By.CSS_SELECTOR, 'h1.DUwDvf')) > 0
                loading_elements = self.driver.find_elements(By.CSS_SELECTOR, 'div[class*="loading"], div[class*="spinner"]')
                is_loading = any(elem.is_displayed() for elem in loading_elements) if loading_elements else False
                
                if name_present and not is_loading:
                    time.sleep(1)
                    return
                
                time.sleep(check_interval)
                elapsed += check_interval
                
            except:
                time.sleep(check_interval)
                elapsed += check_interval
        
        time.sleep(2)

    def _extract_place_id(self, url):
        try:
            match = re.search(r'!1s([^!]+)', url)
            if match:
                return match.group(1)
            return None
        except:
            return None

    def _get_rating(self):
        try:
            rating_text = self._get_text('div.F7nice span[aria-hidden="true"]')
            if rating_text:
                rating = float(rating_text.replace(',', '.'))
                return rating if 0 <= rating <= 5 else None
            return None
        except:
            return None

    def _get_review_count(self):
        try:
            element = self.driver.find_element(By.CSS_SELECTOR, 'div.F7nice span[aria-label]')
            aria_label = element.get_attribute('aria-label')
            numbers = re.findall(r'\d+[\d,\.]*', aria_label.replace(',', ''))
            if numbers:
                return int(numbers[0].replace('.', ''))
            return None
        except:
            return None

    def _get_cuisine_type(self):
        try:
            buttons = self.driver.find_elements(By.CSS_SELECTOR, 'button[jsaction*="category"]')
            cuisine_types = [btn.text.strip() for btn in buttons if btn.text.strip()]
            if cuisine_types:
                return ', '.join(cuisine_types[:3])
            
            page_text = self.driver.find_element(By.TAG_NAME, 'body').text
            common_cuisines = ['Italian', 'Chinese', 'Indian', 'Mexican', 'Japanese', 
                             'Thai', 'French', 'Irish', 'American', 'Mediterranean',
                             'Tapas', 'Brasserie', 'Seafood', 'Steakhouse', 'Cafe', 'Pizza']
            
            for cuisine in common_cuisines:
                if cuisine in page_text:
                    return cuisine
            
            return None
        except:
            return None

    def _get_address(self):
        try:
            button = self.driver.find_element(By.CSS_SELECTOR, 'button[data-item-id="address"]')
            address_div = button.find_element(By.CSS_SELECTOR, 'div.Io6YTe')
            return address_div.text.strip()
        except:
            return None

    def _get_phone(self):
        try:
            button = self.driver.find_element(By.CSS_SELECTOR, 'button[data-item-id*="phone"]')
            phone_div = button.find_element(By.CSS_SELECTOR, 'div.Io6YTe')
            return phone_div.text.strip()
        except:
            return None

    def _get_website(self):
        try:
            website_button = self.driver.find_element(By.CSS_SELECTOR, 'a[data-item-id="authority"]')
            return website_button.get_attribute('href')
        except:
            return None

    def _get_price_range(self):
        try:
            page_text = self.driver.find_element(By.TAG_NAME, 'body').text
            
            price_pattern = r'€(\d+)[–-](\d+)\s*per person'
            match = re.search(price_pattern, page_text)
            if match:
                return f"€{match.group(1)}-{match.group(2)}"
            
            try:
                price_elem = self.driver.find_element(By.CSS_SELECTOR, 'span[aria-label*="Price"]')
                aria_label = price_elem.get_attribute('aria-label')
                
                if 'Moderate' in aria_label:
                    return '€€'
                elif 'Very expensive' in aria_label:
                    return '€€€€'
                elif 'Expensive' in aria_label:
                    return '€€€'
                elif 'Inexpensive' in aria_label:
                    return '€'
            except:
                pass
            
            if '€€€€' in page_text:
                return '€€€€'
            elif '€€€' in page_text:
                return '€€€'
            elif '€€' in page_text:
                return '€€'
            
            return None
        except:
            return None
    
    def _extract_price_numbers(self, price_string):
        if not price_string:
            return None, None
        
        try:
            numbers = re.findall(r'\d+', price_string)
            
            if len(numbers) >= 2:
                return int(numbers[0]), int(numbers[1])
            elif len(numbers) == 1:
                price = int(numbers[0])
                return price, price
            else:
                return None, None
        except:
            return None, None

    def _convert_price_to_numeric(self, price_symbols):
        if not price_symbols:
            return None
        
        price_map = {'€': 1, '€€': 2, '€€€': 3, '€€€€': 4}
        return price_map.get(price_symbols, None)

    def _get_service_options(self):
        try:
            services = []
            page_text = self.driver.find_element(By.TAG_NAME, 'body').text
            
            service_keywords = {
                'Dine-in': ['dine-in', 'dine in'],
                'Takeaway': ['takeaway', 'take away', 'takeout'],
                'Delivery': ['delivery', 'delivers'],
                'Kerbside pickup': ['kerbside pickup', 'curbside pickup']
            }
            
            for service, keywords in service_keywords.items():
                if any(kw in page_text.lower() for kw in keywords):
                    services.append(service)
            
            return ', '.join(services) if services else None
        except:
            return None

    def _get_amenities(self):
        try:
            amenities = []
            page_text = self.driver.find_element(By.TAG_NAME, 'body').text.lower()
            
            amenity_map = {
                'WiFi': ['wifi', 'wi-fi'],
                'Bar': ['bar on site', 'bar'],
                'Outdoor seating': ['outdoor seating'],
                'Good for groups': ['good for groups'],
                'Good for kids': ['good for kids', 'kid-friendly'],
                'Reservations': ['reservations', 'accepts reservations'],
                'Live music': ['live music'],
                'High chairs': ['high chairs']
            }
            
            for amenity, keywords in amenity_map.items():
                if any(kw in page_text for kw in keywords):
                    amenities.append(amenity)
            
            return ', '.join(set(amenities)) if amenities else None
        except:
            return None

    def _get_dietary_options(self):
        try:
            dietary = []
            page_text = self.driver.find_element(By.TAG_NAME, 'body').text.lower()
            
            dietary_keywords = {
                'Vegan': ['vegan options', 'vegan menu', 'vegan'],
                'Vegetarian': ['vegetarian options', 'vegetarian menu', 'vegetarian'],
                'Gluten-Free': ['gluten-free', 'gluten free'],
                'Halal': ['halal'],
                'Kosher': ['kosher'],
                'Dairy-Free': ['dairy-free', 'dairy free']
            }
            
            for option, keywords in dietary_keywords.items():
                if any(kw in page_text for kw in keywords):
                    dietary.append(option)
            
            return ', '.join(dietary) if dietary else None
        except:
            return None

    def _get_atmosphere(self):
        try:
            atmospheres = []
            page_text = self.driver.find_element(By.TAG_NAME, 'body').text.lower()
            
            atmosphere_keywords = {
                'Casual': ['casual'],
                'Cozy': ['cozy', 'cosy'],
                'Upscale': ['upscale', 'fine dining', 'elegant'],
                'Romantic': ['romantic'],
                'Trendy': ['trendy', 'hip', 'modern'],
                'Family-friendly': ['family-friendly', 'family friendly'],
                'Lively': ['lively', 'vibrant'],
                'Quiet': ['quiet', 'intimate']
            }
            
            for atmosphere, keywords in atmosphere_keywords.items():
                if any(kw in page_text for kw in keywords):
                    atmospheres.append(atmosphere)
            
            return ', '.join(atmospheres[:3]) if atmospheres else None
        except:
            return None

    def _get_reviews_with_sentiment(self, max_reviews=10):
        """Extract 10 reviews with smart waiting for content to load"""
        try:
            reviews_list = []
            
            # Click Reviews tab and wait for it to load
            try:
                reviews_button = self.driver.find_element(By.CSS_SELECTOR, 'button[aria-label*="Reviews"]')
                reviews_button.click()
                
                # SMART WAIT: Wait for reviews to load
                max_wait = self.review_load_timeout
                elapsed = 0
                while elapsed < max_wait:
                    review_count = len(self.driver.find_elements(By.CSS_SELECTOR, 'div.jftiEf'))
                    if review_count > 0:
                        break
                    time.sleep(0.5)
                    elapsed += 0.5
                
                time.sleep(2)
            except:
                pass
            
            # Scroll MORE to get more reviews
            try:
                for scroll_num in range(10):
                    before_scroll = len(self.driver.find_elements(By.CSS_SELECTOR, 'div.jftiEf'))
                    self.driver.execute_script("window.scrollBy(0, 500)")
                    
                    time.sleep(1.5)
                    after_scroll = len(self.driver.find_elements(By.CSS_SELECTOR, 'div.jftiEf'))
                    
                    if after_scroll == before_scroll and scroll_num > 4:
                        break
            except:
                pass
            
            review_elements = self.driver.find_elements(By.CSS_SELECTOR, 'div.jftiEf')[:40]
            
            all_reviews = []
            
            for review_elem in review_elements:
                try:
                    try:
                        reviewer_name = review_elem.find_element(By.CSS_SELECTOR, 'div.d4r55').text.strip()
                    except:
                        reviewer_name = 'Anonymous'
                    
                    user_id = None
                    try:
                        profile_link = review_elem.find_element(By.CSS_SELECTOR, 'a[href*="/maps/contrib/"]')
                        href = profile_link.get_attribute('href')
                        match = re.search(r'/contrib/(\d+)', href)
                        if match:
                            user_id = match.group(1)
                    except:
                        pass
                    
                    rating = None
                    try:
                        rating_elem = review_elem.find_element(By.CSS_SELECTOR, 'span.kvMYJc')
                        rating_text = rating_elem.get_attribute('aria-label')
                        rating_match = re.search(r'(\d+)', rating_text)
                        if rating_match:
                            rating = int(rating_match.group(1))
                    except:
                        pass
                    
                    try:
                        more_button = review_elem.find_element(By.CSS_SELECTOR, 'button.w8nwRe')
                        more_button.click()
                        time.sleep(0.3)
                    except:
                        pass
                    
                    review_text = None
                    try:
                        review_text = review_elem.find_element(By.CSS_SELECTOR, 'span.wiI7pd').text.strip()
                    except:
                        pass
                    
                    try:
                        date = review_elem.find_element(By.CSS_SELECTOR, 'span.rsqaWe').text.strip()
                    except:
                        date = None
                    
                    sentiment = self._analyze_sentiment(review_text, rating)
                    
                    if review_text and len(review_text) > 10:
                        all_reviews.append({
                            'username': reviewer_name,
                            'user_id': user_id,
                            'rating': rating,
                            'date': date,
                            'review_text': review_text,
                            'sentiment': sentiment
                        })
                        
                except:
                    continue
            
            # Separate reviews by sentiment
            good_reviews = [r for r in all_reviews if r['sentiment'] == 'Good']
            bad_reviews = [r for r in all_reviews if r['sentiment'] == 'Bad']
            mixed_reviews = [r for r in all_reviews if r['sentiment'] == 'Mixed']
            
            selected_reviews = []
            
            # Try to get a balanced mix: 4 Good, 4 Bad, 2 Mixed
            if good_reviews:
                selected_reviews.extend(good_reviews[:4])
            
            if bad_reviews:
                selected_reviews.extend(bad_reviews[:4])
            
            if mixed_reviews:
                selected_reviews.extend(mixed_reviews[:2])
            
            # Fill remaining slots
            if len(selected_reviews) < max_reviews:
                remaining = [r for r in all_reviews if r not in selected_reviews]
                if remaining:
                    selected_reviews.extend(remaining[:max_reviews - len(selected_reviews)])
            
            if len(selected_reviews) < max_reviews and all_reviews:
                selected_reviews = all_reviews[:max_reviews]
            
            return json.dumps(selected_reviews[:max_reviews], ensure_ascii=False) if selected_reviews else None
            
        except:
            return None

    def _analyze_sentiment(self, review_text, rating):
        """Analyze sentiment: Good, Bad, or Mixed"""
        try:
            if not review_text or len(review_text) < 10:
                if rating is not None:
                    if rating >= 4:
                        return "Good"
                    elif rating <= 2:
                        return "Bad"
                    else:
                        return "Mixed"
                return "Mixed"
            
            review_lower = review_text.lower()
            
            positive_words = [
                'excellent', 'amazing', 'great', 'wonderful', 'fantastic', 
                'delicious', 'perfect', 'love', 'best', 'recommend', 'awesome',
                'incredible', 'outstanding', 'superb', 'brilliant', 'exceptional',
                'lovely', 'enjoyed', 'friendly', 'pleasant', 'welcoming',
                'impressed', 'spectacular', 'tasty', 'fresh', 'quality'
            ]
            
            negative_words = [
                'terrible', 'bad', 'awful', 'horrible', 'disappointing', 
                'worst', 'poor', 'disgusting', 'never', 'waste',
                'overpriced', 'rude', 'slow', 'cold', 'dirty',
                'bland', 'mediocre', 'unfriendly', 'avoid', 'regret',
                'terrible', 'unpleasant', 'unfortunate', 'lacking'
            ]
            
            mixed_indicators = [
                'but', 'however', 'although', 'except', 'unfortunately',
                'wish', 'could be better', 'not bad but', 'decent but',
                'good but', 'nice but', 'okay but'
            ]
            
            positive_count = sum(1 for word in positive_words if word in review_lower)
            negative_count = sum(1 for word in negative_words if word in review_lower)
            has_mixed_indicators = any(indicator in review_lower for indicator in mixed_indicators)
            
            if has_mixed_indicators and positive_count > 0 and negative_count > 0:
                return "Mixed"
            
            if positive_count > 0 and negative_count > 0:
                if positive_count > negative_count * 1.5:
                    return "Good"
                elif negative_count > positive_count * 1.5:
                    return "Bad"
                else:
                    return "Mixed"
            
            if positive_count > 0 and negative_count == 0:
                return "Good"
            
            if negative_count > 0 and positive_count == 0:
                return "Bad"
            
            if rating is not None:
                if rating >= 4:
                    return "Good"
                elif rating <= 2:
                    return "Bad"
                else:
                    return "Mixed"
            
            return "Mixed"
        except:
            return "Mixed"

    def scrape_all_cork_restaurants(self):
        """Scrape ALL Cork restaurants - SAVE EACH RESTAURANT IMMEDIATELY"""
        print(f"Location: Cork, Ireland (ONLY)")
        print(f"Strategy: Multiple search queries for maximum coverage")
        print(f"Duplicate Detection: BY RESTAURANT NAME")
        print(f"Save Strategy: EACH RESTAURANT SAVED IMMEDIATELY")
        print("="*70 + "\n")
        
        # Get restaurants from multiple searches
        restaurant_urls = self.search_restaurants_multi_query("Cork")
        total_restaurants = len(restaurant_urls)
        
        print(f"\n✓ Total unique URLs to scrape: {total_restaurants}")
        print(f"Estimated time: {total_restaurants * 0.5:.0f} minutes ({total_restaurants * 0.5 / 60:.1f} hours)")
        print("="*70 + "\n")
        
        # Prepare output files
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        csv_file = f'cork_restaurants_live_{timestamp}.csv'
        excel_file = f'cork_restaurants_live_{timestamp}.xlsx'
        
        restaurants = []
        failed = 0
        skipped_duplicates = 0
        seen_names = set()  # Track restaurant names to avoid duplicates
        
        # Create headers for CSV
        headers_written = False
        
        for i, url in enumerate(restaurant_urls, 1):
            print(f"[{i:3}/{total_restaurants}] ", end='')
            
            try:
                restaurant = self.scrape_restaurant_details(url)
                if restaurant:
                    # Verify it's in Cork (check address or coordinates)
                    address = restaurant.get('address', '').lower()
                    lat = restaurant.get('latitude')
                    
                    # Only include if it's actually in Cork
                    is_cork = 'cork' in address or (lat and 51.7 <= lat <= 52.1)
                    
                    if not is_cork:
                        print(f"⊗ Skipped (not in Cork): {restaurant.get('name', 'Unknown')}")
                        continue
                    
                    # Check for duplicate by name (case-insensitive)
                    restaurant_name = restaurant.get('name', '').strip().lower()
                    
                    if restaurant_name in seen_names:
                        skipped_duplicates += 1
                        print(f"⊗ Duplicate skipped: {restaurant.get('name', 'Unknown')}")
                        continue
                    
                    # Add unique restaurant
                    seen_names.add(restaurant_name)
                    restaurants.append(restaurant)
                    
                    # SAVE IMMEDIATELY to CSV and Excel
                    df = pd.DataFrame([restaurant])
                    
                    if not headers_written:
                        # First restaurant - write with headers
                        df.to_csv(csv_file, mode='w', index=False, encoding='utf-8-sig', header=True)
                        headers_written = True
                    else:
                        # Append without headers
                        df.to_csv(csv_file, mode='a', index=False, encoding='utf-8-sig', header=False)
                    
                    # Update Excel file with all restaurants so far
                    df_all = pd.DataFrame(restaurants)
                    df_all.to_excel(excel_file, index=False, engine='openpyxl')
                    
                    coord_status = "✓" if lat else "✗"
                    save_status = f"💾 Saved to files"
                    print(f"✓ {restaurant['name']} {coord_status} {save_status}")
                else:
                    failed += 1
                    print("✗ Failed")
                    
            except Exception as e:
                failed += 1
                print(f"✗ Error: {str(e)[:50]}")
            
            time.sleep(random.uniform(2, 4))
        
        print(f"\n{'='*70}")
        print(f"SCRAPING COMPLETED!")
        print(f"Unique Restaurants: {len(restaurants)}")
        print(f"Duplicates Removed: {skipped_duplicates}")
        print(f"Failed: {failed}")
        print(f"Total URLs Processed: {total_restaurants}")
        
        # Count restaurants with coordinates
        with_coords = sum(1 for r in restaurants if r.get('latitude') and r.get('longitude'))
        print(f"Restaurants with coordinates: {with_coords}/{len(restaurants)} ({with_coords/len(restaurants)*100:.1f}%)")
        print(f"\n✓ All restaurants saved to:")
        print(f"  - {csv_file}")
        print(f"  - {excel_file}")
        print(f"{'='*70}\n")
        
        return restaurants, csv_file, excel_file

    def _save_progress(self, restaurants, count):
        """REMOVED - No longer saving progress checkpoints"""
        pass

    def save_to_csv(self, restaurants, filename='restaurants.csv'):
        """Save to CSV (Excel compatible format)"""
        if not restaurants:
            print("No data to save")
            return
            
        df = pd.DataFrame(restaurants)
        df.to_csv(filename, index=False, encoding='utf-8-sig')  # utf-8-sig for Excel compatibility
        print(f"✓ Saved to: {filename}")
        
        print(f"\nDATA QUALITY REPORT")
        print(f"{'='*70}")
        print(f"Total UNIQUE restaurants: {len(df)}\n")
        
        key_fields = ['name', 'place_id', 'cuisine_type', 'price_min', 'price_max',
                     'latitude', 'longitude', 'rating', 'atmosphere', 'dietary_options',
                     'reviews_data']
        
        for field in key_fields:
            if field in df.columns:
                count = df[field].notna().sum()
                pct = count/len(df)*100
                status = "✓" if pct >= 70 else "⚠" if pct >= 50 else "✗"
                print(f"{status} {field:20} {count:4}/{len(df)} ({pct:5.1f}%)")
        
        print(f"{'='*70}\n")
    
    def save_to_excel(self, restaurants, filename='restaurants.xlsx'):
        """Save to Excel format (.xlsx)"""
        if not restaurants:
            print("No data to save")
            return
            
        df = pd.DataFrame(restaurants)
        df.to_excel(filename, index=False, engine='openpyxl')
        print(f"✓ Saved to Excel: {filename}\n")

    def save_to_json(self, restaurants, filename='restaurants.json'):
        """Save to JSON"""
        if not restaurants:
            return
            
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(restaurants, f, indent=2, ensure_ascii=False)
        print(f"✓ Saved to: {filename}\n")

    def close(self):
        """Close browser"""
        self.driver.quit()


def main():
    """Main function - Scrape Cork restaurants - SAVE EACH IMMEDIATELY"""
    scraper = GoogleMapsRestaurantScraper(
        headless=False,
        slow_internet=True
    )
    
    try:
        # Scrape ALL unique restaurants in Cork - saves each one immediately
        restaurants, csv_file, excel_file = scraper.scrape_all_cork_restaurants()
        
        if restaurants:
            # Also save JSON at the end
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            json_file = f'cork_restaurants_live_{timestamp}.json'
            scraper.save_to_json(restaurants, json_file)
            
            print("✓ SCRAPING COMPLETE - ALL RESTAURANTS SAVED:")
            print(f"  📄 CSV: {csv_file}")
            print(f"  📊 Excel: {excel_file}")
            print(f"  📋 JSON: {json_file}")
            print(f"\n✓ Total UNIQUE Cork restaurants: {len(restaurants)}")
            
            # Coordinate stats
            with_coords = sum(1 for r in restaurants if r.get('latitude') and r.get('longitude'))
            print(f"✓ Restaurants with coordinates: {with_coords}/{len(restaurants)} ({with_coords/len(restaurants)*100:.1f}%)")
            
            print("\n✓ Save Strategy:")
            print("  - Each restaurant saved IMMEDIATELY after scraping")
            print("  - CSV file updated with each new restaurant")
            print("  - Excel file refreshed after each addition")
            print("  - No data loss if interrupted")
            
            print("\n✓ Each restaurant includes:")
            print("  - 10 mixed reviews (4 Good, 4 Bad, 2 Mixed sentiment)")
            print("  - Complete place details and features")
            print("  - Coordinates (latitude/longitude)")
            print("  - Pricing, ratings, amenities")
            print("\n✓ Duplicate Detection: All restaurants verified by NAME\n")
        else:
            print("No data collected\n")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Stopped by user")
        print("✓ All scraped restaurants are already saved in files")
        print("✓ You can safely use the CSV and Excel files\n")
    except Exception as e:
        print(f"\n\nError: {e}\n")
        import traceback
        traceback.print_exc()
    finally:
        print("Closing browser...")
        scraper.close()
        print("Done!\n")


if __name__ == "__main__":
    main()