# 🏦 BankBot - Secure AI Banking Assistant

A fully offline, local banking chatbot built with Streamlit and Ollama that strictly answers only banking-related queries. Features include authentication, file upload with OCR, chat history management, and theme customization.

---

## ✨ Features

- **Strict Banking Restriction**: Only answers banking, finance, and account-related questions
- **Local Authentication**: JSON-based login/signup system (no cloud required)
- **File Upload & Context Awareness**: Upload `.txt`, `.pdf`, `.docx`, and images with OCR support
- **Chat History Management**: Save, load, and delete previous conversations
- **Light/Dark Theme**: Professional UI with theme toggle
- **Fully Offline**: Runs entirely on your local machine using Ollama

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- Ollama installed and running
- Tesseract OCR (for image text extraction)

---

## 📦 Installation

### Step 1: Install Python Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Install Ollama

#### Windows

1. Download Ollama from [https://ollama.ai/download](https://ollama.ai/download)
2. Run the installer
3. Open Command Prompt and verify installation:
   ```bash
   ollama --version
   ```

#### macOS

```bash
brew install ollama
```

#### Linux

```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

### Step 3: Pull the Banking Model

```bash
ollama pull qwen2.5:1.5b
```

This downloads the lightweight 1.5B parameter model (approx. 1GB).

### Step 4: Install Tesseract OCR (for image support)

#### Windows

1. Download installer from [https://github.com/UB-Mannheim/tesseract/wiki](https://github.com/UB-Mannheim/tesseract/wiki)
2. Install and add to PATH:
   ```
   C:\Program Files\Tesseract-OCR
   ```

#### macOS

```bash
brew install tesseract
```

#### Linux

```bash
sudo apt-get install tesseract-ocr
```

### Step 5: Start Ollama Server

```bash
ollama serve
```

Leave this terminal open. Ollama will run on `http://localhost:11434`

---

## ▶️ Running the Application

In a new terminal, navigate to the project folder and run:

```bash
streamlit run app.py
```

The app will open automatically in your browser at `http://localhost:8501`

---

## 🎯 Usage Guide

### Authentication

1. **Sign Up**: Create a new account with username and password
2. **Login**: Enter your credentials to access the chatbot
3. Passwords are stored locally in `users.json` (for academic use only)

### Chatting with BankBot

- Type any banking-related question in the chat input
- BankBot will **only** answer questions about:
  - Bank accounts (savings, current, etc.)
  - Loans and mortgages
  - Credit/debit cards
  - Interest rates
  - KYC and documentation
  - Digital banking services
  - Bank timings and branches

- Non-banking questions will receive:
  ```
  I can assist only with banking-related queries.
  ```

### File Upload

1. Click **"Browse files"** in the sidebar
2. Upload supported formats:
   - `.txt` - Plain text documents
   - `.pdf` - PDF documents
   - `.docx` - Word documents
   - `.png`, `.jpg`, `.jpeg` - Images (OCR extraction)
3. BankBot will use the file content as context for your questions
4. Click **"Clear File Context"** to remove uploaded content

### Chat History

- **New Chat**: Start a fresh conversation (current chat is auto-saved)
- **Load Chat**: Click on any saved chat to restore it
- **Delete Chat**: Remove saved conversations

### Theme Toggle

- Use the **"Dark Mode"** toggle in the sidebar
- Changes apply immediately to the entire interface

### Model Settings

- **Temperature**: Control response randomness (0.0 = deterministic, 1.0 = creative)
- **Max Tokens**: Limit response length (128-1024)

---

## 📁 Project Structure

```
BankBot/
│
├── app.py                  # Main Streamlit application
├── users.json              # Local user database (auto-created)
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

---

## 🔧 Configuration

### Change the Model

Edit `app.py` and modify:

```python
DEFAULT_MODEL = "qwen2.5:1.5b"
```

Available models:
- `qwen2.5:1.5b` (fast, lightweight)
- `qwen2.5:3b` (balanced)
- `qwen2.5:7b` (more accurate, slower)
- `llama3.2:3b` (alternative)

Pull new models with:
```bash
ollama pull <model-name>
```

### Customize System Prompt

Edit the `SYSTEM_PROMPT` variable in `app.py` to adjust BankBot's behavior.

---

## 🛠 Troubleshooting

### Ollama Connection Error

**Error**: "Unable to connect to the banking assistant service"

**Solution**:
1. Ensure Ollama is running: `ollama serve`
2. Check if the model is downloaded: `ollama list`
3. Verify Ollama is accessible: `curl http://localhost:11434/api/tags`

### Tesseract Not Found

**Error**: "pytesseract.pytesseract.TesseractNotFoundError"

**Solution**:
1. Install Tesseract OCR (see Step 4 above)
2. Add Tesseract to your system PATH
3. On Windows, set the path explicitly in `app.py`:
   ```python
   pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
   ```

### Import Errors

**Error**: "ModuleNotFoundError"

**Solution**:
```bash
pip install -r requirements.txt --upgrade
```

### Port Already in Use

**Error**: "Address already in use"

**Solution**:
```bash
streamlit run app.py --server.port 8502
```

---

## 🔐 Security Notes

- This application is designed for **academic and local use only**
- Passwords are stored in **plain text** in `users.json`
- **Do not use in production** without proper security measures
- For production deployment:
  - Use proper password hashing (bcrypt, argon2)
  - Implement HTTPS/SSL
  - Use a real database (PostgreSQL, MongoDB)
  - Add rate limiting and input validation

---

## 🎓 Academic Use

This project is ideal for:
- AI/ML coursework and demonstrations
- Fintech UI/UX portfolio projects
- Python and Streamlit learning
- Local LLM integration studies
- Banking chatbot research

---

## 📝 Example Banking Questions

✅ **Allowed**:
- "What types of savings accounts do you offer?"
- "How can I apply for a personal loan?"
- "What documents are required for KYC?"
- "What are your current interest rates?"
- "How do I activate my debit card?"

❌ **Blocked**:
- "Write me a Python script"
- "What's the weather today?"
- "Tell me a joke"
- "Who won the World Cup?"

---

## 📄 License

This project is provided as-is for educational purposes. No warranties or guarantees are provided.

---

## 🤝 Contributing

This is a complete, standalone academic project. Feel free to fork and modify for your own learning purposes.

---

## 📧 Support

For issues related to:
- **Ollama**: Visit [https://ollama.ai/](https://ollama.ai/)
- **Streamlit**: Check [https://docs.streamlit.io/](https://docs.streamlit.io/)
- **Tesseract**: See [https://github.com/tesseract-ocr/tesseract](https://github.com/tesseract-ocr/tesseract)

---

## ✅ Checklist Before Running

- [ ] Python 3.10+ installed
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Ollama installed and running (`ollama serve`)
- [ ] Model downloaded (`ollama pull qwen2.5:1.5b`)
- [ ] Tesseract OCR installed (optional, for image support)
- [ ] Run the app (`streamlit run app.py`)

---

**Enjoy using BankBot - Your secure, offline banking assistant!** 🏦
