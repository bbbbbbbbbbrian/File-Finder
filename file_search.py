import pymongo
import re
from sentence_transformers import (SentenceTransformer)
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS

class file_searcher():
    def __init__(self, db_name, collection_name):
            self.model = SentenceTransformer("all-MiniLM-L6-v2")
            self.client = pymongo.MongoClient("mongodb://localhost:27017/")
            self.collection = self.client[db_name][collection_name]

    def semantic_search(self, query, snippets=5):
        query_vector = self.model.encode([query])

        all_docs = list(self.collection.find({}))

        if not all_docs:
            return []

        embeddings = [doc["embedding"] for doc in all_docs]

        similarities = cosine_similarity(query_vector, embeddings)[0]

        results = []

        for doc, score in zip(all_docs, similarities):
            results.append({
                "file_name": doc["file_name"],
                "chunk_id": doc["chunk_id"],
                "text": doc["text"],
                "score": float(score)
            })

        results.sort(
            key=lambda x: x["score"],
            reverse=True
        )

        return results[:snippets]

    def inverted_search(self, query, inverted_index, snippets=5):
        if not inverted_index:
            return []

        query_words = re.findall(r"\b[a-zA-Z0-9]+\b", query.lower())

        query_words = [
            word for word in query_words
            if word not in ENGLISH_STOP_WORDS
        ]
        
        chunk_scores = {}

        for word in query_words:
            if word not in inverted_index:
                continue

            for chunk in inverted_index[word]:
                if chunk not in chunk_scores:
                    chunk_scores[chunk] = 0

                chunk_scores[chunk] += 1

        num_query_words = len(query_words)

        for chunk in chunk_scores:
            chunk_scores[chunk] /= num_query_words

        ranked_chunks = sorted(
            chunk_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )

        ranked_chunks = ranked_chunks[:snippets]

        results = []

        for (file_name, chunk_id), score in ranked_chunks:
            doc = self.collection.find_one({
                "file_name": file_name,
                "chunk_id": chunk_id
            })

            if doc:
                results.append({
                    "file_name": doc["file_name"],
                    "chunk_id": doc["chunk_id"],
                    "text": doc["text"],
                    "score": score
                })
        return results

    def hybrid_search(self, semantic_data, inverted_data, snippets=5):
        results = {}

        for doc in semantic_data:
            key = (doc["file_name"], doc["chunk_id"])

            results[key] = {
                "file_name": doc["file_name"],
                "chunk_id": doc["chunk_id"],
                "text": doc["text"],
                "semantic_score": doc["score"],
                "keyword_score": 0
            }

        for doc in inverted_data:
            key = (doc["file_name"], doc["chunk_id"])

            if key not in results:
                results[key] = {
                    "file_name": doc["file_name"],
                    "chunk_id": doc["chunk_id"],
                    "text": doc["text"],
                    "semantic_score": 0,
                    "keyword_score": doc["score"]
                }
            else:
                results[key]["keyword_score"] = doc["score"]

        for doc in results.values():
            doc["score"] = (
                doc["semantic_score"] * 0.7
                + doc["keyword_score"] * 0.3
            )

        ranked_results = sorted(
            results.values(),
            key=lambda x: x["score"],
            reverse=True
        )
        
        return ranked_results[:snippets]