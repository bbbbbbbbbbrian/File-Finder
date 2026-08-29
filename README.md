# Semantic Notes Search

A Python-based semantic search engine for school notes. It converts notes into vector embeddings and retrieves the most relevant sections based on the **meaning** of a user's query rather than exact keyword matches.

## How It Works

1. **Extracts text** from PDF, TXT, and Markdown files.
2. **Chunks documents** into overlapping sections.
3. Uses **Sentence Transformers (`all-MiniLM-L6-v2`)** to generate embeddings for each chunk.
4. **Stores** text and embeddings in MongoDB.
5. Converts a user's question into an embedding.
6. Uses **cosine similarity** to find and rank the most relevant chunks.
7. Returns the top matching snippets with their source file and similarity score.

```text
Notes
  ↓
Text Extraction
  ↓
Chunking
  ↓
Transformer Embeddings
  ↓
MongoDB
  ↑
Query → Embedding → Cosine Similarity
                         ↓
                  Relevant Snippets
```

## Tech Stack

* **Python**
* **Sentence Transformers** — semantic text embeddings
* **MongoDB / PyMongo** — document and embedding storage
* **scikit-learn** — cosine similarity
* **pypdf** — PDF text extraction

## Project Structure

```text
semantic-notes-search/
├── main.py
├── file_process.py
├── file_search.py
└── README.md
```

* `file_process.py` — extracts, chunks, embeds, and stores notes.
* `file_search.py` — embeds queries and retrieves relevant chunks.
* `main.py` — provides the command-line interface.

## Example

A query such as:

```text
What makes an AVL tree balanced?
```

can retrieve relevant sections from notes even when the notes use different wording, because the search is based on **semantic similarity** rather than exact word matching.

This project explores the core pipeline behind modern **semantic search and retrieval-augmented generation (RAG)** systems.
