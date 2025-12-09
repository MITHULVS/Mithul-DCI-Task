import requests
import numpy as np
from openai import OpenAI

client = OpenAI(api_key=("sk-proj-we7eary91m2D9uo32GDn4tTNXCWQJBFGMI02_2HevpHn4mPgLokvGQAFH5tZPlpfz_g-dZsM0-"))

WIKI_API = "https://simple.wikipedia.org/w/api.php"
titles = [
    "Python (programming language)",
    "Django (web framework)",
    "Artificial intelligence"
]


def get_page(title):
    params = {
        "action": "query",
        "prop": "extracts",
        "explaintext": 1,
        "titles": title,
        "format": "json"
    }
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(WIKI_API, params=params, headers=headers)
    data = r.json()
    page = list(data["query"]["pages"].values())[0]
    return page.get("extract", "")


def split_text(text, size=500):
    text = text.replace("\n", " ")
    parts = []
    i = 0
    while i < len(text):
        chunk = text[i:i + size].strip()
        if chunk:
            parts.append(chunk)
        i += size
    return parts


def embed(text_list):
    r = client.embeddings.create(
        model="text-embedding-3-small",
        input=text_list
    )
    return np.array([d.embedding for d in r.data])


def build_docs():
    docs = []
    texts = []
    for title in titles:
        print("Downloading:", title)
        txt = get_page(title)
        parts = split_text(txt)
        n = 1
        for p in parts:
            docs.append({"title": title, "part": n, "text": p})
            texts.append(p)
            n += 1
    return docs, texts


def ask(q, docs, emb):
    q_emb = embed([q])[0]
    sims = emb @ q_emb / (np.linalg.norm(emb, axis=1) * np.linalg.norm(q_emb))
    idx = sims.argsort()[::-1][:3]

    ctx = ""
    used = []
    k = 1
    for i in idx:
        d = docs[i]
        ctx += f"[Source {k} - {d['title']} - part {d['part']}]\n{d['text']}\n\n"
        used.append(d)
        k += 1

    prompt = "Use only this context:\n" + ctx + "\nAnswer the question: " + q

    r = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=200
    )

    print("\nAnswer:", r.choices[0].message.content)
    print("\nSources:")
    for s in used:
        print(f"{s['title']} (part {s['part']})")


def main():
    print("Building knowledge...")
    docs, texts = build_docs()
    print("Embedding docs...")
    emb = embed(texts)
    print("Ready!\n")

    while True:
        q = input("Ask (Enter = exit): ").strip()
        if q == "":
            break
        ask(q, docs, emb)


if __name__ == "__main__":
    main()




