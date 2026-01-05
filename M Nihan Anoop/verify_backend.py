
import sys
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def check_imports():
    print("Checking imports...")
    try:
        import chromadb
        print("[OK] chromadb imported")
    except ImportError as e:
        print(f"[FAIL] chromadb missing: {e}")

    try:
        from sentence_transformers import SentenceTransformer
        print("[OK] sentence_transformers imported")
    except ImportError as e:
        print(f"[FAIL] sentence_transformers missing: {e}")

    try:
        import requests
        print("[OK] requests imported")
    except ImportError as e:
        print(f"[FAIL] requests missing: {e}")

def check_ollama():
    print("\nChecking Ollama connectivity...")
    import requests
    try:
        response = requests.get("http://localhost:11434", timeout=2)
        if response.status_code == 200:
            print("[OK] Ollama is running")
        else:
            print(f"[WARN] Ollama reachable but returned status {response.status_code}")
    except requests.RequestException:
        print("[FAIL] Ollama is NOT running or not reachable at localhost:11434")

def check_backend_rag():
    print("\nChecking RAG Backend (ChromaDB + Embeddings)...")
    try:
        from backend import BankBotBackend
        backend = BankBotBackend()
        # Initialize (should be fast if DB exists)
        backend.initialize_knowledge_base()
        print("[OK] BankBotBackend initialized")
        
        # Test Query
        results = backend.query_knowledge_base("ATM limit")
        print(f"[OK] RAG Query successful. Retrieved {len(results)} chunks.")
    except Exception as e:
        print(f"[FAIL] RAG Backend error: {e}")

def check_llm_engine():
    print("\nChecking LLM Engine...")
    try:
        from llm_engine import LLMEngine
        engine = LLMEngine()
        if engine.model:
            print(f"[OK] LLM Engine initialized with model: {engine.model}")
            # Simple generation test
            print("   Testing generation (this might take a few seconds)...")
            response = engine.query_ollama("Say 'System Operational'", [])
            print(f"[OK] LLM Response: {response}")
        else:
            print("[FAIL] LLM Engine failed to detect model")
    except Exception as e:
        print(f"[FAIL] LLM Engine error: {e}")

if __name__ == "__main__":
    print("--- BankBot Backend Verification ---")
    check_imports()
    check_ollama()
    check_backend_rag()
    check_llm_engine()
    print("------------------------------------")
