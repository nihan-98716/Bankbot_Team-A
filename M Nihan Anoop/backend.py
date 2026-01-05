import logging
import os
import uuid
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class BankBotBackend:
    def __init__(self):
        self.persist_directory = "bankbot_db"
        self.rag_enabled = False
        self.collection = None
        self.model = None

        try:
            import chromadb
            from sentence_transformers import SentenceTransformer
            
            # Initialize ChromaDB Client
            self.client = chromadb.PersistentClient(path=self.persist_directory)
            self.collection_name = "rbi_faqs"
            self.collection = self.client.get_or_create_collection(name=self.collection_name)
            
            # Initialize Embedding Model
            logging.info("Loading embedding model...")
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            logging.info("Embedding model loaded.")
            self.rag_enabled = True
            logging.info("✅ RAG Backend initialized successfully.")
        except ImportError as e:
            logging.warning(f"⚠️ RAG dependencies missing ({e}). Running in LLM-only mode.")
        except Exception as e:
            logging.error(f"❌ RAG initialization failed: {e}. Running in LLM-only mode.")

    def initialize_knowledge_base(self):
        """Initializes the knowledge base. Scraper removed as per request."""
        if not self.rag_enabled:
            logging.info("RAG disabled. Skipping knowledge base initialization.")
            return

        if self.collection.count() > 0:
            logging.info(f"Knowledge base already exists with {self.collection.count()} items.")
            return
        
        logging.info("Knowledge base is empty. Running in LLM-only mode or waiting for manual ingestion.")
        pass

    def query_knowledge_base(self, query_text, n_results=3):
        """Queries the knowledge base for relevant context."""
        if not self.rag_enabled:
            return []

        try:
            query_embedding = self.model.encode([query_text]).tolist()
            
            results = self.collection.query(
                query_embeddings=query_embedding,
                n_results=n_results
            )
            
            # Extract documents
            if results['documents']:
                return results['documents'][0] # List of strings
            return []
        except Exception as e:
            logging.error(f"Error querying knowledge base: {e}")
            return []

    def get_collection_stats(self):
        """Returns stats about the knowledge base."""
        if not self.rag_enabled:
            return {"count": 0, "status": "RAG Disabled (LLM Only)"}

        try:
            count = self.collection.count()
            return {"count": count, "status": "Active"}
        except Exception as e:
            logging.error(f"Error getting stats: {e}")
            return {"count": 0, "status": "Error"}

if __name__ == "__main__":
    backend = BankBotBackend()
    backend.initialize_knowledge_base()
    
    # Test Query
    q = "What are the ATM withdrawal limits?"
    print(f"\nQuery: {q}")
    results = backend.query_knowledge_base(q)
    for i, res in enumerate(results):
        print(f"Result {i+1}: {res[:100]}...")
