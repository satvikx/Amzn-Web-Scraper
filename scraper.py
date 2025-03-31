import requests
from bs4 import BeautifulSoup
import pandas as pd
from fake_useragent import UserAgent
import json
import lxml
import time
import random


class AmazonScraper:
    def __init__(self, url):
        self.url = url
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Connection': 'keep-alive',
            'Referer': 'https://www.amazon.in/',
        }
        self.soup = None
        self.product_data = {
            'name': '',
            'rating': '',
            'num_ratings': '',
            'selling_price': '',
            'total_discount': '',
            'bank_offers': [],
            'about_item': '',
            'product_info': {},
            'images': [],
            'review_summary': ''
        }

    def fetch_page(self):
        try:
            # Sending request with a slight delay to avoid blocking
            time.sleep(random.uniform(1, 3))
            response = requests.get(self.url, headers=self.headers)
            print(f"Status Code: {response.status_code}")
            if response.status_code == 200:
                self.soup = BeautifulSoup(response.content, 'lxml')
            else:
                print(f"Failed to fetch page. Status code: {response.status_code}")
        except Exception as e:
            print(f"Error fetching page: {e}")

    def extract_product_name(self):
        try:
            self.product_data['name'] = self.soup.find('span', {'id': 'productTitle'}).get_text().strip().replace('\u200e', '')
        except Exception as e:
            print(f"Error extracting product name: {e}")

    def extract_rating_and_reviews(self):
        try:
            rating_element = self.soup.find('span', {'class': 'a-icon-alt'})
            if rating_element:
                self.product_data['rating'] = rating_element.get_text().split()[0]
        except:
            print("Error extracting rating")

        # Reviews
        try:
            num_ratings_element = self.soup.find('span', {'id': 'acrCustomerReviewText'})
            if num_ratings_element:
                self.product_data['num_ratings'] = num_ratings_element.get_text().split()[0]
        except:
            print("Error extracting number of ratings")

    def extract_price_and_discount(self):
        try:
            price_element = self.soup.find('span', {'class': 'a-price-whole'})
            if price_element:
                self.product_data['selling_price'] = price_element.get_text().replace(',', '').strip()
        except:
            print("Error extracting selling price")

        try:
            discount_element = self.soup.find('span', {'class': 'a-size-large a-color-price savingPriceOverride aok-align-center reinventPriceSavingsPercentageMargin savingsPercentage'})
            if discount_element:
                self.product_data['total_discount'] = discount_element.get_text().strip()
        except:
            print("Error extracting discount")

    def extract_bank_offers(self):
        try:
            bank_offers = []
            offer_sections = [
                'itembox-InstantBankDiscount',
                'instantBankDiscount',
                'creditPromoBadge',
                'IBDB-announce'
            ]
            for section_id in offer_sections:
                section = self.soup.find('div', {'id': section_id})
                if section:
                    offers = section.find_all(['span', 'div'], class_=lambda x: x and 'a-size-base' in x)
                    for offer in offers:
                        text = offer.get_text().strip()
                        if text and any(keyword in text.lower() for keyword in ['bank', 'offer', 'discount']):
                            bank_offers.append(text)
            self.product_data['bank_offers'] = bank_offers
        except Exception as e:
            print(f"Error extracting bank offers: {e}")

    def extract_about_item(self):
        try:
            about_item = self.soup.find('div', {'id': 'feature-bullets'})
            if about_item:
                bullets = about_item.find_all('span', {'class': 'a-list-item'})
                about_text = [bullet.get_text().strip() for bullet in bullets]
                self.product_data['about_item'] = '\n'.join(about_text)
        except:
            print("Error extracting about item")

    def extract_product_info(self):
        try:
            product_info = {}
            info_table = self.soup.find('table', {'id': 'productDetails_techSpec_section_1'})
            if info_table:
                rows = info_table.find_all('tr')
                for row in rows:
                    th = row.find('th')
                    td = row.find('td')
                    if th and td:
                        product_info[th.get_text().strip()] = td.get_text().replace('\u200e', '').strip()
            self.product_data['product_info'] = product_info
        except:
            print("Error extracting product information")

    def extract_images(self):
        try:
            images = []
            # Main Image
            img_wrapper = self.soup.find('div', {'id': 'imgTagWrapperId'})
            if img_wrapper:
                img = img_wrapper.find('img')
                if img:
                    src = img.get('src') or img.get('data-old-hires') or img.get('data-a-dynamic-image')
                    if src:
                        if isinstance(src, dict):  # Handle data-a-dynamic-image JSON
                            src = list(src.keys())[0] if src else None
                        if src and 'http' in src:
                            high_res = src.replace('._SL1500_', '._SL5000_').replace('._SY550_', '._SX5000_')
                            images.append(high_res)                          

            # Images from the manufacturer
            product_description = self.soup.select('#productDescription img, #aplus img, .a-expander-content img')
            for img in product_description:
                if 'src' in img.attrs and img['src'].startswith('http'):
                    images.append(img['src'])
            
            # Method 4: Find additional images in A+ content
            aplus_images = self.soup.select('.aplus-v2 img')
            for img in aplus_images:
                if 'src' in img.attrs and img['src'].startswith('http'):
                    if img['src'] not in images:
                        images.append(img['src'])
            
            # Deduplicate the lists
            images = list(set(images))
            images = [url for url in images if not (url.endswith('.png') or url.endswith('.gif'))]
            self.product_data['images'].extend(images)
            

        except Exception as e:
            print(f"Error extracting images: {e}")

    def extract_review_summary(self):
        try:
            review_summary = self.soup.find('p', {'class': 'a-spacing-small'})
            if review_summary:
                self.product_data['review_summary'] = review_summary.get_text().strip()
        except:
            print("Error extracting review summary.")

    def save_data(self):
        try:
            with open('amazon_product.json', 'w') as f:
                json.dump(self.product_data, f, indent=4)

            csv_data = self.product_data.copy()
            csv_data['product_info'] = str(csv_data['product_info'])
            csv_data['bank_offers'] = ' | '.join(csv_data['bank_offers'])
            csv_data['images'] = ' | '.join(csv_data['images'])

            df = pd.DataFrame([csv_data])
            df.to_csv('amazon_product.csv', index=False)

            print("Scraping completed successfully. Data saved to amazon_product.json and amazon_product.csv")
        except Exception as e:
            print(f"Error saving data: {e}")

    def scrape(self):
        print("Scraping Data, please wait...")
        self.fetch_page()
        if self.soup:
            self.extract_product_name()
            self.extract_rating_and_reviews()
            self.extract_price_and_discount()
            self.extract_bank_offers()
            self.extract_about_item()
            self.extract_product_info()
            self.extract_images()
            self.extract_review_summary()
            self.save_data()
        else:
            print("Scraping failed.")
