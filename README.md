
# Amazon Products Scraper (using BeautifulSoup)
**This project is a web scraper designed to extract product details from Amazon product pages using Python and the BeautifulSoup library. The scraper fetches information such as product name, price, ratings, reviews, images, and other relevant details. The extracted data is saved in both JSON and CSV formats for further analysis or use.**

## Features
- Extracts product details such as:
  - Product name
  - Price and discounts
  - Ratings and number of reviews
  - Product description and specifications
  - Images 
  - Bank offers and promotional details
- Saves the extracted data in:
  - `amazon_product.json` (structured JSON format)
  - `amazon_product.csv` (tabular format for easy analysis)
- Handles dynamic user-agent headers to avoid detection.
- Modular and object-oriented design for better maintainability.


## Setup

[**Note** - I use uv as python package manager and Git Bash as default terminal]
1. Create Virtual Environment `uv venv venv`.
2. Activate Environment `source venv/Scripts/activate`.
3. Install Dependencies `uv pip install -r requirements.txt`.
4. Insert the product url in `main.py` file.
5. Run using `python main.py`.
6. Results are saved in [amazon_product.csv](amazon_product.csv) and [amazon_product.json](amazon_product.json). 