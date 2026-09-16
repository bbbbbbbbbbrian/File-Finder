import glob 
import os
import pymongo
from pathlib import Path
from pypdf import PdfReader
from sentence_transformers import (SentenceTransformer)
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS

class file_processer():
    def __init__(self, notes_dir, db_name, collection_name):
        self.notes_dir = notes_dir
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

        self.mongo_uri = "mongodb://localhost:27017/"
        self.client = pymongo.MongoClient(self.mongo_uri)

        self.db = self.client[db_name]
        self.collection = self.db[collection_name]

    def get_files(self) -> list:
        pdf_paths = glob.glob(os.path.join(self.notes_dir, "*.pdf"))
        txt_paths = glob.glob(os.path.join(self.notes_dir, "*.txt"))
        md_paths = glob.glob(os.path.join(self.notes_dir, "*.md"))

        return pdf_paths + txt_paths + md_paths

    def extract_text(self, file_path:str) -> str:
        path = Path(file_path)
        suffix = path.suffix
        if suffix == ".pdf":
            reader = PdfReader(path)
            return " ".join([page.extract_text() or "" for page in reader.pages])
        elif suffix == ".txt" or suffix == ".md":
            return path.read_text(encoding="utf-8", errors="ignore")
        return ""

    def chunk_text(self, text:str) -> list:
        chunk_list = []
        text_words = text.split()
        for i in range(0, len(text_words), 200):
            window = i + 250
            chunk = " ".join(text_words[i:window])
            chunk_list.append(chunk)
        return chunk_list

    def process_and_store(self):
        files = []
        inverted_index = {}

        file_list = self.get_files()

        for file_path in file_list:
            file_name = os.path.basename(file_path)
            file_text = self.extract_text(file_path)
            chunked_file = self.chunk_text(file_text)
            for chunk_id, chunk in enumerate(chunked_file):
                vector = self.model.encode(chunk).tolist()
                words = chunk.lower().split()

                for word in words:
                    if word in ENGLISH_STOP_WORDS:
                        continue

                    if word not in inverted_index:
                        inverted_index[word] = set()

                    inverted_index[word].add((file_name, chunk_id))

                # OUTSIDE the word loop
                doc = {
                    "file_name": file_name,
                    "chunk_id": chunk_id,
                    "text": chunk,
                    "embedding": vector
                }

                files.append(doc)

        if not files:
            return

        self.collection.insert_many(files)

        return inverted_index
                
    


    