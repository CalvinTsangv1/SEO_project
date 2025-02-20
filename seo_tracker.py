import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import requests
import time
import pandas as pd
from pymongo import MongoClient
import shopifyapi as shopify


class SEOTracker:
    def __init__(self, competitors_site, keyword_list, target_site, database_connection_string):
        """Initialize search engine optimization tracker"""
        self.keyword_list = keyword_list
        self.target_site = target_site
        self.competitors_site = competitors_site

        """Initialize MongoDB connection"""
        self.database_connection_string = database_connection_string
        self.database_name = database_name
        self.collection_name = collection_name
        self.client = MongoClient(database_connection_string)
        self.db = self.client["seo_database"]
        self.rankings_collection = self.db["google_rankings"]
        self.backlinks_collection = self.db["backlinks"]
        self.shopify_seo_collection = self.db["shopify_seo"]

        """Initialize Shopify API connection"""
        self.shop_url = "https://tigerprint.ca"
        self.api_key = "shpat_1234567890abcdefghijklmnopqrstuvwxyz"
        self.password = "shppa_1234567890abcdefghijklmnopqrstuvwxyz"

        """Initialize Selenium WebDriver"""
        ChromeOptions = uc.ChromeOptions()
        ChromeOptions.headless = False



    def get_google_ranksing(self, max_pages= 20):
        """Scrape Google search results to get rankings"""
        driver = uc.Chrome(options=ChromeOptions)
        results =[]
        rank = None
        page = 0

        for keyword in self.keyword_list:
            while page < max_pages:
                search_url = f"https://www.google.com/search?q={keyword.replace(' ', '+')}&start={page * 10}"
                driver.get(search_url)
                time.sleep(7)

                soup = BeautifulSoup(driver.page_source, "html.parser")
                search_results = soup.find_all("div", class_="tF2Cxc")  # Google search result containers
                print(f"Page {page + 1} - Found {len(search_results)} search results")

                for index, result in enumerate(search_results, start=(page * 10) + 1):
                    title = result.find("h3").text if result.find("h3") else "No Title"
                    link = result.find("a")["href"]
                    results.append({"Rank": index, "Title": title, "URL": link})

                    if self.target_site in link and rank is None:
                        rank = index
                page += 1
            self.rankings_collection.insert_many(results)
            results = []
            print(f"✅ Google Rankings stored in MongoDB for {self.keyword}.")
        driver.quit()

    def get_backlinks(self):
        """Find backlinks pointing to a competitor's site"""
        search_url = f"https://www.google.com/search?q=link:{self.competitor_site}"
        headers = {"User-Agent": "Mozilla/5.0"}

        response = requests.get(search_url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")

        results = []
        for link in soup.find_all("a"):
            href = link.get("href")
            if href and "http" in href:
                results.append({"Competitor": self.competitor_site, "Backlink": href})

        self.backlinks_collection.insert_many(results)
        print(f"✅ Backlinks stored in MongoDB for {self.competitor_site}.")
        
    def update_shopify_seo(self):
        """Update Shopify SEO metadata for all products"""
        shopify.ShopifyResource.set_site(f"https://{self.api_key}:{self.password}@{self.shop_url}/admin")
        products = shopify.Product.find()

        shopify_seo_data = []
        for product in products:
            seo_entry = {
                "Product": product.title,
                "SEO_Title": f"{product.title} | High-Quality Printing Services",
                "SEO_Description": f"Premium {product.title} with custom printing. Fast shipping!"
            }
            shopify_seo_data.append(seo_entry)

        self.shopify_seo_collection.insert_many(shopify_seo_data)
        print("✅ Shopify product SEO data updated and stored in MongoDB.")

    def execute(self):
        """Run the SEO tracker"""
        self.get_google_ranksing()
        self.get_backlinks()
        self.update_shopify_seo()
        print("✅ SEO Tracker execution!")

seo_tracker = SEOTracker(competitors_site="tigerprint.ca", 
                         keyword_list=["tiger", "printing", "cards", "banner", "tiger print", "tiger printing"],
                         target_site="tigerprint.ca",
                         database_connection_string="mongodb://localhost:27017/")
seo_tracker.execute()




keyword_list = ["tiger", "printing", "cards", "banner", "tiger print", "tiger printing"]
database_connection_string = "mongodb://localhost:27017/"
database_name = "SEO_Project"
collection_name = "Google_Search_Rankings"
target_site = "tigerprint.ca"

ChromeOptions = uc.ChromeOptions()
ChromeOptions.headless = False
driver = uc.Chrome(options=ChromeOptions)



# Function to get Google Search Rankings
def get_google_rankings(keyword, target_site, max_pages=3):

    results = []
    rank = None
    page = 0

    while page < max_pages:
        time.sleep(1)
        search_url = f"https://www.google.com/search?q={keyword.replace(' ', '+')}&start={page * 10}"
        driver.get(search_url)
        time.sleep(3)  # Allow time for JavaScript to load

        soup = BeautifulSoup(driver.page_source, "html.parser")
        search_results = soup.find_all("div", class_="tF2Cxc")  # Google search result containers
        print(f"Page {page + 1} - Found {len(search_results)} search results")

        for index, result in enumerate(search_results, start=(page * 10) + 1):
            title = result.find("h3").text if result.find("h3") else "No Title"
            link = result.find("a")["href"]
            results.append({"Rank": index, "Title": title, "URL": link})

            if target_site in link and rank is None:
                rank = index

        page += 1
    return results, rank

# Function to analyze competitor SEO tags
def analyze_website(url, keyword):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(response.text, "html.parser")

        title = soup.find("title").text if soup.find("title") else "No Title"
        meta_desc = soup.find("meta", attrs={"name": "description"})
        meta_desc = meta_desc["content"] if meta_desc else "No Description"

        h1 = soup.find("h1").text.strip() if soup.find("h1") else "No H1"

        text = soup.get_text().lower()
        keyword_count = text.count(keyword.lower())
        total_words = len(text.split())
        keyword_density = round((keyword_count / total_words) * 100, 2) if total_words > 0 else 0

        return {"URL": url, "Title": title, "Meta Description": meta_desc, "H1 Tag": h1, "Keyword Density (%)": keyword_density}

    except Exception as e:
        return {"URL": url, "Error": str(e)}


# Get rankings
for keyword_to_search in keyword_list:
    rankings, website_rank = get_google_rankings(keyword_to_search, your_website, 10)

    # Save results
    df = pd.DataFrame(rankings)
    df.to_csv("google_search_rankings_"+ keyword_to_search + ".csv", index=False)
    print(f"Google Search ({keyword_to_search}) Rankings saved as 'google_search_rankings.csv'.")

    # Print ranking position
    if website_rank:
        print(f"Your website ({your_website}) ranks at position: {website_rank}")
    else:
        print(f"Your website ({your_website}) is not in the top {len(df)} results.")

    seo_data = []
    for result in rankings[:5]:  
        seo_data.append(analyze_website(result["URL"], keyword_to_search))

    df_seo = pd.DataFrame(seo_data)
    df_seo.to_csv("competitor_seo_analysis.csv", index=False)
    print("Competitor SEO Analysis saved as 'competitor_seo_analysis.csv'.")
