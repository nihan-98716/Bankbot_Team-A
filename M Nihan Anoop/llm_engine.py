import requests
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class LLMEngine:
    def __init__(self, model=None):
        self.base_url = "http://127.0.0.1:11434/api/chat"
        self.model = model
        
        if not self.model:
            try:
                tags_url = "http://127.0.0.1:11434/api/tags"
                response = requests.get(tags_url, timeout=2)
                if response.status_code == 200:
                    models = response.json().get('models', [])
                    if models:
                        self.model = models[0]['name']
                        logging.info(f"Auto-selected model: {self.model}")
                    else:
                        self.model = "llama3" 
                        logging.warning("No models found in Ollama, defaulting to llama3")
                else:
                    self.model = "llama3"
            except Exception as e:
                logging.error(f"Error detecting model: {e}")
                self.model = "llama3"

    def query_ollama(self, user_query, context_chunks, system_instructions=None):
       
        if system_instructions:
            system_prompt = system_instructions
        else:
            context_text = "\n\n".join(context_chunks)
            system_prompt = f"""You are BankBot, a specialized, professional, and friendly Banking Assistant.
        
        Your Mission:
        Provide accurate, helpful, and secure banking information to customers.
        
        Guidelines:
        1. **Scope:** Answer ONLY banking-related questions (e.g., accounts, transactions, loans, cards, regulations, security).
        2. **Guardrails:** 
           - If a user asks a non-banking question (e.g., "Who made you?", "Weather?", "General knowledge"), gently redirect them: "I am a dedicated Banking Assistant. I can help you with your financial questions. How can I assist you with your banking needs today?"
           - Do not answer meta-questions about your underlying model or training data.
        3. **Tone:** Professional, empathetic, and concise.
        4. **Context:** Use the provided context if relevant. If context is empty, use your general banking knowledge but be cautious not to hallucinatory specific policy details.
        
        Context:
        {context_text}
        """
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_query}
            ],
            "stream": False
        }
        
        try:
            logging.info(f"Sending query to Ollama ({self.model})...")
            response = requests.post(self.base_url, json=payload, timeout=60)
            response.raise_for_status()
            
            result = response.json()
            return result['message']['content']
            
        except requests.RequestException as e:
            logging.error(f"Error communicating with Ollama: {e}")
            return "I'm having trouble connecting to my AI brain (Ollama) right now. Please ensure Ollama is running."

if __name__ == "__main__":
    engine = LLMEngine()
    # Test
    ctx = ["RBI says ATM withdrawal limit is Rs 10,000 per day for this bank."]
    print(engine.query_ollama("What is the ATM limit?", ctx))
