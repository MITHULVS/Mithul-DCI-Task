import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import re
from collections import Counter

df = pd.read_csv("C:\\Users\\Mithul\\OneDrive\\Desktop\\DCI\\Day-1\\clean_review1.csv")

#Total Number of review
print("Total Number of Review:",len(df["Text"]))
#Top 10 Sold Products
print("\nTop 10 Sold Products:\n",df['ProductId'].value_counts().head(10))

#Monthly Graph
df['Time'] = pd.to_datetime(df['Time'], dayfirst=True, errors='coerce')
df['Month'] = df['Time'].dt.to_period('M')
monthly_trend = df.groupby('Month').size()
monthly_trend.index = monthly_trend.index.to_timestamp()
print(monthly_trend)
plt.figure(figsize=(12, 6))
sns.lineplot(x=monthly_trend.index, y=monthly_trend.values, marker='o')
plt.title("Monthly Review Trend")
plt.xlabel("Month")
plt.ylabel("Number of Reviews")
plt.grid(True, linestyle='--', alpha=0.4)
plt.tight_layout()
plt.show()


#Rating distribution
plt.figure(figsize=(8,5))
sns.histplot(data=df,x='Score',bins=5,kde=True,color='#4A90E2',edgecolor='black',linewidth=1)
plt.title("Rating Distribution Histogram")
plt.xlabel("Rating")
plt.ylabel("Count")
plt.grid(True, linestyle='--', alpha=0.4)
plt.xticks([1, 2, 3, 4, 5])
plt.tight_layout()
plt.show()

#Top 10 Common word used

# Combine all summaries into one big string
print("\nTop 10 Common Word:\n")
all_summary_text = " ".join(df['Summary'])
# Split into words
words = re.findall(r'\w+', all_summary_text)
# Count frequencies
word_counts = Counter(words)
# Top 10 most frequent words
for i in word_counts.most_common(10):
    print(i[0],":",i[1])
