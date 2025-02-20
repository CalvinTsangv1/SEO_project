import requests
from bs4 import BeautifulSoup
import pymongo

class ShopifyKeywordExtractor:
    def __init__(self, shopify_url):
        """Initialize parameters and MongoDB connection"""
        self.shopify_url = shopify_url.rstrip("/")
        self.client = pymongo.MongoClient("mongodb://localhost:27017/")
        self.db = self.client["shopify_seo"]
        self.collection_seo = self.db["collections"]
        self.product_seo = self.db["products"]

    def get_product_links(self):
        """Extract product links from the Shopify store homepage"""
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(self.shopify_url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")

        product_links = []
        for link in soup.find_all("a", href=True):
            if "/products/" in link["href"]:  # Filter only product pages
                product_links.append(self.shopify_url + link["href"])

        return list(set(product_links))  # Remove duplicates

    def get_collections_from_product(self, product_url):
        """Extract collection links from a product page"""
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(product_url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")

        collection_links = []
        for link in soup.find_all("a", href=True):
            if "/collections/" in link["href"] and "/products/" not in link["href"]:
                collection_links.append(self.shopify_url + link["href"])

        return list(set(collection_links))

    def extract_keywords(self, url):
        """Extract SEO metadata and keywords from a page"""
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")

        title = soup.find("title").text if soup.find("title") else "No Title"
        meta_desc = soup.find("meta", attrs={"name": "description"})
        meta_desc = meta_desc["content"] if meta_desc else "No Description"

        h1 = soup.find("h1").text.strip() if soup.find("h1") else "No H1"
        keywords = meta_desc.split()[:10]  # Extract first 10 words as keywords
        alt_texts = [img["alt"] for img in soup.find_all("img", alt=True) if img["alt"]]

        return {
            "URL": url,
            "Title": title,
            "Meta Description": meta_desc,
            "H1 Tag": h1,
            "Keywords": keywords,
            "Alt Text": alt_texts
        }

    def save_to_mongodb(self, data, collection):
        """Store extracted keyword data in MongoDB"""
        collection.insert_one(data)

    def execute(self):
        """Run the full Shopify keyword extraction"""
        print(f"🚀 Extracting products from {self.shopify_url}...")
        product_links = self.get_product_links()

        for product in product_links:
            print(f"🛒 Processing product: {product}")
            product_data = self.extract_keywords(product)
            self.save_to_mongodb(product_data, self.product_seo)

            # Find collections associated with this product
            collection_links = self.get_collections_from_product(product)
            for collection in collection_links:
                print(f"📂 Processing collection: {collection}")
                collection_data = self.extract_keywords(collection)
                self.save_to_mongodb(collection_data, self.collection_seo)

        print("🎯 Shopify keyword extraction complete!")

# Define your Shopify store URL
shopify_url = "https://www.tigerprint.ca"

# Run the keyword extractor
extractor = ShopifyKeywordExtractor(shopify_url)
extractor.execute()
