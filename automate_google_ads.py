from google.ads.google_ads.client import GoogleAdsClient

CLIENT_ID = "YOUR_CLIENT"
DEVELOPER_TOKEN = "YOUR_DEVELOPER_TOKEN"
CUSTOMER_ID = "YOUR_CUSTOMER_ID"


def get_google_trends(keyword):
    """ 透過 Google Trends 找出低競爭、高潛力的關鍵字 """
    pytrends = TrendReq(hl="en-US", tz=360)
    pytrends.build_payload([keyword], timeframe="today 12-m")

    trend_data = pytrends.interest_over_time()
    if not trend_data.empty:
        print(f"\n📈 Google Trends - {keyword} 趨勢變化：")
        trend_data[keyword].plot(figsize=(10, 5))
        plt.title(f"Google Trends - {keyword}")
        plt.xlabel("日期")
        plt.ylabel("搜尋熱度")
        plt.show()
    return trend_data

# 🔍 查詢所有關鍵字趨勢
for kw in keywords:
    get_google_trends(kw)


def optimize_google_ads(client, customer_id, keyword):
    """ 自動調整 Google Ads 廣告出價，降低高 CPC 低轉換的關鍵字 """
    
    query = """
        SELECT
            keyword_view.keyword.text,
            metrics.average_cpc,
            metrics.conversions
        FROM
            keyword_view
        WHERE
            segments.date DURING LAST_30_DAYS
        AND
            keyword_view.keyword.text IN ('{}')
    """.format("','".join(keywords))

    search_request = client.service.google_ads.search(
        customer_id=customer_id, query=query
    )

    for row in search_request:
        keyword_text = row.keyword_view.keyword.text
        avg_cpc = row.metrics.average_cpc / 1e6  # 轉換為美元
        conversions = row.metrics.conversions

        print(f"🔹 關鍵字: {keyword_text} | CPC: ${avg_cpc:.2f} | 轉換數: {conversions}")
        
        # 若 CPC 過高且轉換率低，則降低出價
        if avg_cpc > 2.0 and conversions < 5:
            print(f"⚠️ {keyword_text} CPC 過高，建議降低出價！")

# ✅ 執行 Google Ads 自動優化
client = GoogleAdsClient.load_from_storage("google-ads.yaml")
optimize_google_ads(client, CUSTOMER_ID, keywords)

def generate_seo_content(keyword):
    """ 使用 OpenAI 生成 SEO 文章，提升網站排名 """
    prompt = f"寫一篇 SEO 友好的文章，主題是『{keyword}』，包含 3 個副標題，適合電商網站。"
    
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    
    seo_article = response["choices"][0]["message"]["content"]
    print(f"\n📖 生成的 SEO 文章（{keyword}）：\n{seo_article}\n")
    return seo_article


# ✅ 針對低競爭關鍵字生成 SEO 內容
for kw in ["cheap printing services", "best custom banner"]:
    generate_seo_content(kw)

print("\n🚀 廣告優化 + SEO 內容已完成！")