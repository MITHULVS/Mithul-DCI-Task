# rag.py — Multi-PDF RAG support

import re
import faiss
import numpy as np
from PyPDF2 import PdfReader
from sentence_transformers import SentenceTransformer
import nltk
from django.conf import settings
import google.generativeai as genai

nltk.download("punkt", quiet=True)

def clean_text(t: str):
    t = re.sub(r"\n\s*\d+\s*\n", "\n", t)
    t = re.sub(r"\n{2,}", "\n\n", t)
    return t.strip()

class SimpleRAG:
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

        self.text_chunks = []
        self.pdf_names = []
        self.index = None

        self.gemini = genai.GenerativeModel("models/gemini-flash-latest")

    def add_pdf(self, file_obj, filename, skip_first_n_pages=5, chunk_size=5):
        reader = PdfReader(file_obj)
        text = ""

        for i, page in enumerate(reader.pages):
            if i < skip_first_n_pages:
                continue
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"

        text = clean_text(text)
        sentences = nltk.sent_tokenize(text)

        chunks = [
            " ".join(sentences[i:i + chunk_size])
            for i in range(0, len(sentences), chunk_size)
        ]

        self.pdf_names.append(filename)
        self.text_chunks.extend(chunks)

        embeddings = np.array(self.model.encode(self.text_chunks))
        dim = embeddings.shape[1]

        self.index = faiss.IndexFlatL2(dim)
        self.index.add(embeddings.astype(np.float32))

    def retrieve(self, query, k=3):
        q_emb = np.array(self.model.encode([query])).astype(np.float32)
        D, I = self.index.search(q_emb, k)
        return [self.text_chunks[i] for i in I[0] if i < len(self.text_chunks)]

    def answer(self, question):
        chunks = self.retrieve(question, k=3)
        context = "\n\n---\n\n".join(chunks)

        prompt = f"""
Answer the question using ONLY this document context:

QUESTION:
{question}

DOCUMENT EXCERPTS:
{context}

If answer is not found in any document, say:
"The documents do not contain this information."
"""

        result = self.gemini.generate_content(prompt)
        return result.text



def youtube_recommendation(query: str) -> str:
    """Return a YouTube search link based on the question."""
    q = query.strip().replace(" ", "+")
    return f"https://www.youtube.com/results?search_query={q}"
