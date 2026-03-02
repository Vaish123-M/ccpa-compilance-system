import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


class CCPASectionRetriever:
    def __init__(self, sections: list[dict[str, str]], embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"):
        if not sections:
            raise ValueError("Sections cannot be empty")

        self.sections = sections
        self.embedding_model = SentenceTransformer(embedding_model)
        self.section_texts = [f"{item['section']}\n{item['text']}" for item in sections]

        embeddings = self.embedding_model.encode(
            self.section_texts,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False,
        ).astype(np.float32)

        self.index = faiss.IndexFlatIP(embeddings.shape[1])
        self.index.add(embeddings)

    def retrieve(self, query: str, k: int = 3) -> list[dict[str, str]]:
        top_k = max(1, min(k, len(self.sections)))
        query_embedding = self.embedding_model.encode(
            [query],
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False,
        ).astype(np.float32)

        scores, indices = self.index.search(query_embedding, top_k)

        output: list[dict[str, str]] = []
        for rank, index in enumerate(indices[0].tolist()):
            item = dict(self.sections[index])
            item["score"] = float(scores[0][rank])
            output.append(item)
        return output