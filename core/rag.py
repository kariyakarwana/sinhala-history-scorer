import re
from collections import Counter

class RAGRetriever:
    def __init__(self, knowledge_path):
        with open(knowledge_path, "r", encoding="utf-8") as file:
            text = file.read()

        self.chunks = [chunk.strip() for chunk in text.split("\n\n") if chunk.strip()]

    def tokenize(self, text):
        text = re.sub(r"[^\u0D80-\u0DFFa-zA-Z0-9\s]", " ", text)
        return [w.strip() for w in text.split() if len(w.strip()) > 1]

    def score_chunk(self, query, chunk):
        query_words = self.tokenize(query)
        chunk_words = self.tokenize(chunk)

        query_counter = Counter(query_words)
        chunk_counter = Counter(chunk_words)

        score = 0
        for word in query_counter:
            if word in chunk_counter:
                score += query_counter[word] * chunk_counter[word]

        return score

    def retrieve(self, query, top_k=2):
        scored_chunks = []

        for chunk in self.chunks:
            score = self.score_chunk(query, chunk)
            scored_chunks.append((score, chunk))

        scored_chunks.sort(reverse=True, key=lambda x: x[0])

        results = [chunk for score, chunk in scored_chunks[:top_k] if score > 0]

        if not results:
            results = self.chunks[:top_k]

        return results