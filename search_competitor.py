import requests
from bs4 import BeautifulSoup

class ShopifyCompetitorFinder:
    def __init__(self, keyword):
        """Initialize search settings for competitor analysis"""
        self.keyword = keyword
        self.headers = {"User-Agent": "Mozilla/5.0"}

    def search_competitors(self):
        """Perform Google search for Shopify competitors using a keyword"""
        search_url = f"https://www.google.com/search?q={self.keyword.replace(' ', '+')}+shopify"
        response = requests.get(search_url, headers=self.headers)
        soup = BeautifulSoup(response.text, "html.parser")

        competitors = []
        for result in soup.find_all("div", class_="tF2Cxc"):
            title = result.find("h3").text if result.find("h3") else "No Title"
            link = result.find("a")["href"]
            if "shopify" in link:  # Ensure it's a Shopify-based store
                competitors.append({"Keyword": self.keyword, "Title": title, "URL": link})

        return competitors

    def execute(self):
        """Run the competitor search and display results"""
        print(f"🚀 Searching for Shopify competitors using keyword: {self.keyword}")
        competitors = self.search_competitors()

        if competitors:
            for comp in competitors:
                print(f"🔹 {comp['Title']} - {comp['URL']}")
        else:
            print("❌ No competitors found.")

# Define the keyword to search for
keyword_to_search = "custom printing services"

# Run the competitor finder
competitor_finder = ShopifyCompetitorFinder(keyword_to_search)
competitor_finder.execute()
