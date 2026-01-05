from backend import BankBotBackend
import time

print("Initializing backend...")
start = time.time()
backend = BankBotBackend()
backend.initialize_knowledge_base()
end = time.time()
print(f"Backend initialized in {end - start:.2f} seconds")

print("Querying knowledge base...")
results = backend.query_knowledge_base("exchange of soiled notes")
print(f"Results: {results}")
