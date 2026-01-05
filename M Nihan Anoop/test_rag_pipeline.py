
import logging
import sys
from backend import BankBotBackend

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def test_rag():
    print("--- Testing RAG Pipeline ---")
    
    try:
        print("1. Initializing Backend...")
        backend = BankBotBackend()
        
        print("2. Initializing Knowledge Base (Scraping/Indexing)...")
        backend.initialize_knowledge_base()
        
        print("3. Verifying Collection Stats...")
        stats = backend.get_collection_stats()
        print(f"   Stats: {stats}")
        
        if stats['count'] == 0:
            print("❌ Knowledge base is empty!")
            return
            
        print("4. Testing Retrieval...")
        query = "What is the daily ATM withdrawal limit?"
        print(f"   Query: '{query}'")
        
        results = backend.query_knowledge_base(query, n_results=2)
        
        if results:
            print(f"✅ Retrieved {len(results)} documents.")
            for i, doc in enumerate(results):
                print(f"   Doc {i+1}: {doc[:150]}...")
        else:
            print("❌ No documents retrieved.")
            
    except Exception as e:
        print(f"❌ Error during RAG test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_rag()
