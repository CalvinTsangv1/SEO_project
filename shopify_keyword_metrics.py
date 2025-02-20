import pymongo
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter

# Connect to MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["shopify_seo"]
product_collection = db["products"]
collection_collection = db["collections"]

def get_data_from_mongodb(collection):
    """Extract title, H1 tags, and alt text from MongoDB collection"""
    titles = []
    h1_tags = []
    alt_texts = []
    
    for doc in collection.find({}, {"Title": 1, "H1 Tag": 1, "Alt Text": 1, "_id": 0}):
        if doc.get("Title"):
            titles.append(doc["Title"])
        if doc.get("H1 Tag"):
            h1_tags.append(doc["H1 Tag"])
        if doc.get("Alt Text"):
            alt_texts.extend(doc["Alt Text"])  # Alt texts may be a list, so extend instead of append
    
    return titles, h1_tags, alt_texts

# Retrieve data from MongoDB
product_titles, product_h1_tags, product_alt_texts = get_data_from_mongodb(product_collection)
collection_titles, collection_h1_tags, collection_alt_texts = get_data_from_mongodb(collection_collection)

# Combine data
all_titles = product_titles + collection_titles
all_h1_tags = product_h1_tags + collection_h1_tags
all_alt_texts = product_alt_texts + collection_alt_texts

# Count occurrences
title_counts = Counter(all_titles)
h1_tag_counts = Counter(all_h1_tags)
alt_text_counts = Counter(all_alt_texts)

# Convert to DataFrame for visualization
df_titles = pd.DataFrame(title_counts.items(), columns=["Title", "Count"]).sort_values(by="Count", ascending=False).head(15)
df_h1_tags = pd.DataFrame(h1_tag_counts.items(), columns=["H1 Tag", "Count"]).sort_values(by="Count", ascending=False).head(15)
df_alt_texts = pd.DataFrame(alt_text_counts.items(), columns=["Alt Text", "Count"]).sort_values(by="Count", ascending=False).head(15)

# Create a single figure with three subplots
fig, axes = plt.subplots(1, 3, figsize=(18, 6))

# Plot Title Frequency Chart
axes[0].barh(df_titles["Title"], df_titles["Count"], color="blue")
axes[0].set_xlabel("Frequency")
axes[0].set_ylabel("Title")
axes[0].set_title("Top 15 Titles in Store")
axes[0].invert_yaxis()

# Plot H1 Tag Frequency Chart
axes[1].barh(df_h1_tags["H1 Tag"], df_h1_tags["Count"], color="green")
axes[1].set_xlabel("Frequency")
axes[1].set_ylabel("H1 Tag")
axes[1].set_title("Top 15 H1 Tags in Store")
axes[1].invert_yaxis()

# Plot Alt Text Frequency Chart
axes[2].barh(df_alt_texts["Alt Text"], df_alt_texts["Count"], color="purple")
axes[2].set_xlabel("Frequency")
axes[2].set_ylabel("Alt Text")
axes[2].set_title("Top 15 Alt Texts in Store")
axes[2].invert_yaxis()

# Adjust layout
plt.tight_layout()
plt.show()
