import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import pymongo
import time

class ShopifyCompetitorFinder:
    def __init__(self):
        """Initialize MongoDB connection and Google search settings"""
        self.client = pymongo.MongoClient("mongodb://localhost:27017/")
        self.db = self.client["shopify_seo"]
        self.product_keyword_collection = self.db["products"]
        self.collection_keyword_collection = self.db["collections"]
        self.competitor_collection = self.db["competitors"]
        self.headers = {"User-Agent": "Mozilla/5.0"}

    def get_top_keywords(self, limit=10):
        """Retrieve top keywords from MongoDB"""
        pipeline = [
            {"$unwind": "$Keywords"},
            {"$group": {"_id": "$Keywords", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": limit}
        ]
        results = self.product_keyword_collection.aggregate(pipeline)
        return [doc["_id"] for doc in results]
    
    def get_top_Alt_texts(self, limit=10):
        """Retrieve top keywords from MongoDB"""
        pipeline = [
            {"$unwind": "$Alt Text"},
            {"$group": {"_id": "$Alt Text", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": limit}
        ]
        results = self.product_keyword_collection.aggregate(pipeline)
        return [doc["_id"] for doc in results]
    

    def search_competitors(self, keyword):
        """Perform Google search for competitors using a keyword"""
        options = uc.ChromeOptions()
        options.headless = False  # Runs in the background

        driver = uc.Chrome(options=options)
        search_url = f"https://www.google.com/search?q={keyword.replace(' ', '+')}+shopify"
        driver.get(search_url)
        time.sleep(3)  # Allow page to load

        soup = BeautifulSoup(driver.page_source, "html.parser")
        driver.quit()

        competitors = []
        for result in soup.find_all("div", class_="tF2Cxc"):
            title = result.find("h3").text if result.find("h3") else "No Title"
            link = result.find("a")["href"]
            if "shopify" in link:  # Ensure it's a Shopify-based store
                competitors.append({"Keyword": keyword, "Title": title, "URL": link})

        return competitors

    def find_competitors(self):
        """Find competitors based on top keywords"""
        keywords = self.get_top_keywords()
        AltTexts = self.get_top_Alt_texts()
        all_competitors = []

        for keyword in keywords:
            print(f"🔍 Searching for competitors using keyword: {keyword}")
            competitors = self.search_competitors(keyword)
            print(competitors)
            all_competitors.extend(competitors)

        for AltText in AltTexts:
            print(f"🔍 Searching for competitors using Alt Text: {AltText}")
            competitors = self.search_competitors(AltText)
            print(competitors)
            all_competitors.extend(competitors)

        if all_competitors:
            self.competitor_collection.insert_many(all_competitors)
            print(f"✅ Competitor data stored in MongoDB: {len(all_competitors)} entries")

    def execute(self):
        """Run the full competitor search"""
        print("🚀 Finding Shopify competitors based on top keywords...")
        self.find_competitors()
        print("✅ Competitor search complete!")

# Run the competitor finder
competitor_finder = ShopifyCompetitorFinder()
competitor_finder.execute()
