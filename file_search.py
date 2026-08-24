import pymongo
from sentence_transformers import (SentenceTransformer)
from sklearn.metrics.pairwise import cosine_similarity

class file_searcher():
    def __init__(self, db_name, collection_name):
            self.model = SentenceTransformer("all-MiniLM-L6-v2")

            self.client = pymongo.MongoClient("mongodb://localhost:27017/")
            self.collection = self.client[db_name][collection_name]

    def search(self, query, threshold = 0.40, snippets = 5) -> list:
        all_docs = list(self.collection.find({}))

        if not all_docs:
            return []

        query_vector = self.model.encode(query).reshape(1,-1)

        result = []
        chunk_vector = []

        for docs in all_docs:
            chunk_vector.append(docs["embedding"])
        
        scores = cosine_similarity(query_vector, chunk_vector).flatten()

        for i, doc in enumerate(all_docs):
            if scores[i] >= threshold:
                result.append({
                    "file_name" : doc["file_name"],
                    "chunk_id" : doc["chunk_id"],
                    "text" : doc["text"],
                    "score" : scores[i],
                })

        result.sort(key=lambda x: x["score"], reverse=True)
        return result[:snippets]

    
