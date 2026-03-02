from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

class CCPAIndex:
    def __init__(self, sections):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.section_keys = list(sections.keys())
        self.section_texts = list(sections.values())

        embeddings = self.model.encode(self.section_texts)
        self.index = faiss.IndexFlatL2(embeddings.shape[1])
        self.index.add(np.array(embeddings))

    def retrieve(self, query, k=3):
        query_embedding = self.model.encode([query])
        distances, indices = self.index.search(np.array(query_embedding), k)

        results = []
        for idx in indices[0]:
            results.append((self.section_keys[idx], self.section_texts[idx]))

        return results