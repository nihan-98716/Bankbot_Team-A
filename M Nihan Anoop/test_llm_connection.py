
import sys
import os

print("Testing LLM Engine Isolation...")
try:
    from llm_engine import LLMEngine
    print("✅ LLMEngine imported successfully")
    
    engine = LLMEngine()
    print(f"✅ LLMEngine initialized. Model: {engine.model}")
    
    response = engine.query_ollama("Hello", [])
    print(f"✅ LLM Response: {response}")
    
except ImportError as e:
    print(f"❌ Import Error: {e}")
except Exception as e:
    print(f"❌ Runtime Error: {e}")
