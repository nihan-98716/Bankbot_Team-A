
try:
    import chromadb
    print(f"chromadb imported: {chromadb.__version__}")
    if hasattr(chromadb, 'PersistentClient'):
        print("PersistentClient found")
    else:
        print("PersistentClient NOT found")
except ImportError:
    print("chromadb NOT imported")
except Exception as e:
    print(f"Error: {e}")
