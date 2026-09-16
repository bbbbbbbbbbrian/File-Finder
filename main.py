import os
from file_process import file_processer
from file_search import file_searcher

DB_NAME = "school_notes"
COLLECTION_NAME = "notes"
NOTES_FOLDER = os.path.join(os.path.expanduser("~/Downloads"), "my_notes")

def main():
    inverted_index = {}
    store_files = input("Process files? (type \"yes\"): ").strip()
    if store_files == "yes":            
        if not os.path.exists(NOTES_FOLDER):
            os.makedirs(NOTES_FOLDER)
            print("Add files to NOTES_FOLDER and rerun.")
            return

        processor = file_processer(notes_dir=NOTES_FOLDER, db_name=DB_NAME, collection_name=COLLECTION_NAME)
        inverted_index = processor.process_and_store()

    searcher = file_searcher(db_name=DB_NAME, collection_name=COLLECTION_NAME)

    while True:
        query = input("Question (type \"stop\" to stop): ").lower().strip()
        if query == "stop":
            break

        if not query:
            continue
        
        semantic_data = searcher.semantic_search(query = query)
        inverted_data = searcher.inverted_search(query = query, inverted_index = inverted_index)

        response_data = searcher.hybrid_search(semantic_data = semantic_data, inverted_data = inverted_data)

        if not response_data:
            print("No relevant materials found!")
            continue

        print("\n" + "=" * 50)
        print(f"{len(response_data)} RELEVANT SNIPPETS")
        print("=" * 50)

        for idx, match in enumerate(response_data, 1):
            source_file = match.get("file_name", "Unknown File")
            score = match.get("score", 0.0)
            text = match.get("text", "").strip()

            print(
                f"\n[Result {idx}] Source: {source_file} "
                f"(Hybrid: {score:.3f} | "
                f"Semantic: {match.get('semantic_score', 0.0):.3f} | "
                f"Keyword: {match.get('keyword_score', 0.0):.3f})"
            )

            print("Semantic:", len(semantic_data))
            print("Inverted:", len(inverted_data))
            print("Hybrid:", len(response_data))
                        
            print("-" * 50)
            print(text)

if __name__ == "__main__":
    main()
    



