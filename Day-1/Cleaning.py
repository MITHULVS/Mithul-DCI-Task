#Successfully Downloaded Dataset
import pandas as pd
import numpy as np
import re
import nltk
from nltk.corpus import stopwords

def clean_text(text):
    text = text.lower()
    text = re.sub(r'\s+', ' ', text).strip()
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub(r'(.)\1{2,}', r'\1\1', text)

    words = text.split()
    stop_words = set(stopwords.words('english'))
    clean_words = [w for w in words if w not in stop_words]

    return " ".join(clean_words)

pd.set_option('display.max_columns', None)
df = pd.read_csv("C:\\Users\\Mithul\\OneDrive\\Desktop\\Reviews.csv", index_col=0)

key = {}
rows_to_delete = []

# Convert UNIX time to date
df['Time'] = pd.to_datetime(df['Time'], unit='s')

# Fix empty fields BEFORE cleaning
df[['Summary','ProfileName']] = df[['Summary','ProfileName']].replace(r'^\s*$', np.nan, regex=True)
df['ProfileName'] = df['ProfileName'].fillna('Unknown')

# Clean text + profile name
for index, row in df.iterrows():
    user = row["UserId"]
    product = row["ProductId"]

    df.loc[index, "ProfileName"] = clean_text(str(row["ProfileName"]))
    df.loc[index, "Text"] = clean_text(str(row["Text"]))

    # Score issues
    if row["Score"] > 5 or row["Score"] < 0:
        df.loc[index, "Score"] = 0

    # Helpfulness issues
    if row["HelpfulnessDenominator"] < row["HelpfulnessNumerator"] or \
       row["HelpfulnessDenominator"] < 0 or row["HelpfulnessNumerator"] < 0:
        df.loc[index, "HelpfulnessDenominator"] = 0
        df.loc[index, "HelpfulnessNumerator"] = 0

    # Duplicate user–product
    if user not in key:
        key[user] = {product}
    else:
        if product in key[user]:
            rows_to_delete.append(index)
        else:
            key[user].add(product)

# Fill missing summary using first 3 clean words
df['Summary'] = df['Summary'].fillna(df['Text'].str.split().apply(lambda x: " ".join(x[:3])))

# Clean summary
df['Summary'] = df['Summary'].apply(clean_text)

# Remove duplicates
df = df.drop(rows_to_delete).reset_index(drop=True)

# ---- FINAL FIX: Remove invisible chars & whitespace-only values ----
for col in ["Summary", "ProfileName", "Text"]:
    df[col] = df[col].astype(str).str.replace("\xa0", " ", regex=False).str.strip()

df[["Summary","ProfileName","Text"]] = df[["Summary","ProfileName","Text"]].replace(
    r'^\s*$', np.nan, regex=True
)

# Fill again after cleaning
df['Summary'] = df['Summary'].fillna(df['Text'].str.split().apply(lambda x: " ".join(x[:3])))
df['ProfileName'] = df['ProfileName'].fillna("unknown")

df.index = range(1, len(df) + 1)
df.to_csv("C:\\Users\\Mithul\\OneDrive\\Desktop\\DCI\\Day-1\\clean_review1.csv", index=False)
