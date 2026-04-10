import chromadb
import hashlib

# ChromaDB persistent storage — no onnxruntime needed
client = chromadb.PersistentClient(path="./chroma_db")

collection = client.get_or_create_collection(
    name="test_patterns"
)

def save_test_pattern(code: str, tests: str, bug_analysis: str):
    """Save a code+test pattern to memory."""
    try:
        doc_id = hashlib.md5(code.encode()).hexdigest()
        collection.upsert(
            documents=[code],
            metadatas=[{
                "tests": tests[:500],           # ✅ Limit size
                "analysis": bug_analysis[:300]  # ✅ Limit size
            }],
            ids=[doc_id]
        )
        print("✅ Pattern saved to RAG store")
    except Exception as e:
        print(f"❌ RAG Save Error: {e}")

def retrieve_similar_patterns(code: str, n: int = 2) -> list:
    """Find similar past test patterns."""
    try:
        count = collection.count()
        if count == 0:
            return []

        results = collection.query(
            query_texts=[code],
            n_results=min(n, count)
        )

        if results and results.get("metadatas") and results["metadatas"][0]:
            return results["metadatas"][0]
        return []

    except Exception as e:
        print(f"❌ RAG Retrieve Error: {e}")
        return []