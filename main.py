from scraper import AmazonScraper

if __name__ == "__main__":
    url = "https://www.amazon.in/Acer-inches-Ready-Google-AR32HDIGU2841AT/dp/B0D9BX9DMB/"
    scraper = AmazonScraper(url)
    scraper.scrape()