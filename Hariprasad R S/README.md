# 🏦 BankBot – AI Chatbot for Banking FAQs (Streamlit + Ollama)

BankBot is a **domain-restricted AI chatbot** designed to answer **banking-related frequently asked questions** such as loans, account opening, ATM issues, card blocking, deposits, and net banking.  
The application is built using **Python and Streamlit**, with **Ollama (local LLM)** integrated in a **controlled and secure manner**.

---

## 📌 Features

- Banking-only chatbot (restricted domain)
- Predefined banking FAQ knowledge base
- Controlled Ollama AI integration (fallback only)
- Keyword-based banking query validation
- Multiple chat sessions (ChatGPT-like)
- Auto chat title generation
- Persistent chat history using Streamlit session state
- Clean and interactive UI
- Fully offline AI support (local Ollama)

---

## 🛠️ Technology Stack

- **Python 3.9+**
- **Streamlit** – UI framework
- **Ollama (Mistral model)** – Local LLM
- **Requests** – API communication
- **Datetime** – Timestamp handling

---

## 📦 Dependencies Installation

Ensure Python is installed on your system.

### Install required Python packages
```bash
pip install streamlit requests

### Ollama Setup (Required for AI Responses)
### Install Ollama
### Download and install Ollama from:

https://ollama.com
### Pull the Mistral model
ollama pull mistral


###Verify Ollama is running
ollama run mistral

### Ollama should be running on:

http://localhost:11434
▶
### How to Run the Project
### Navigate to project directory
cd BankBot


### Run the Streamlit application
streamlit run app.py

#### Open in browser
http://localhost:8501
