import streamlit as st
import time
import uuid
from datetime import datetime

# --- Backend Integration ---
BACKEND_AVAILABLE = False
LLM_AVAILABLE = False

try:
    from llm_engine import LLMEngine
    LLM_AVAILABLE = True
except ImportError as e:
    print(f"LLM Engine import failed: {e}")

try:
    from backend import BankBotBackend
    BACKEND_AVAILABLE = True
except ImportError as e:
    print(f"Backend (RAG) import failed: {e}")

# --- Custom CSS (Inlined for Stability) ---
def get_custom_css():
    return """
    <style>
        /* Import Premium Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=Space+Grotesk:wght@300;400;500;600;700&display=swap');

        /* Global Font Settings */
        html, body, [class*="css"] {
            font-family: 'Outfit', sans-serif;
            color: #ffffff;
        }
        
        h1, h2, h3 {
            font-family: 'Space Grotesk', sans-serif;
            font-weight: 700;
            letter-spacing: -0.5px;
        }

        /* Premium Animated Background - Deep Midnight Theme */
        .stApp {
            background: linear-gradient(-45deg, #0f2027, #203a43, #2c5364); /* Professional Dark Teal */
            background-size: 400% 400%;
            background-attachment: fixed; /* Ensures background stays even when scrolling */
            animation: gradient 15s ease infinite;
        }

        /* Ensure main container is transparent to show background */
        [data-testid="stAppViewContainer"] {
            background: transparent !important;
        }

        @keyframes gradient {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }

        /* Header Styling - Neon Pop (Negative/High Contrast) */
        h1 {
            color: #ffffff !important;
            text-align: center;
            font-size: 4.5rem !important;
            font-weight: 800 !important;
            padding-bottom: 1rem;
            margin-top: 1rem;
            text-shadow: 0 0 10px rgba(0, 212, 255, 0.8), 0 0 20px rgba(0, 212, 255, 0.5), 0 0 30px rgba(0, 212, 255, 0.3); /* Neon Cyan Glow */
            letter-spacing: -1px;
            background: transparent !important;
            -webkit-text-fill-color: #ffffff !important;
        }
        
        /* Sidebar Title - BankBot Pop */
        [data-testid="stSidebar"] h1 {
            font-size: 3rem !important;
            text-shadow: 0 0 15px rgba(255, 255, 255, 0.6);
            color: #ffffff !important;
        }
        
        /* Subheader/Text Styling */
        p, label, .stMarkdown {
            font-size: 1.1rem;
            line-height: 1.6;
            color: #e0e0e0 !important; /* Off-white for readability */
        }
        
        /* Global Text Color Override */
        html, body, [class*="css"] {
            color: #ffffff !important;
        }
        
        /* Advanced Glassmorphic Buttons */
        .stButton > button {
            background: rgba(255, 255, 255, 0.1) !important;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2) !important;
            color: #ffffff !important;
            border-radius: 12px !important;
            padding: 0.75rem 1.5rem !important;
            transition: all 0.3s ease !important;
            font-weight: 600 !important;
            text-transform: uppercase;
            letter-spacing: 1px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        }
        
        .stButton > button:hover {
            background: rgba(0, 212, 255, 0.2) !important; /* Cyan tint */
            border-color: #00d4ff !important;
            transform: translateY(-3px);
            box-shadow: 0 0 20px rgba(0, 212, 255, 0.4);
            color: #ffffff !important;
        }

        /* Chat Input Styling - Responsive Bottom Rectangle */
        .stChatInput {
            /* Remove fixed position to let Streamlit handle sidebar adjustment */
            background: rgba(15, 32, 39, 0.95) !important;
            backdrop-filter: blur(20px);
            border-top: 1px solid rgba(255, 255, 255, 0.1);
            padding: 1rem 1rem !important;
            z-index: 100; /* Lower than sidebar */
        }
        
        .stChatInputContainer {
            padding-bottom: 0 !important;
        }
        
        .stChatInput textarea {
            background-color: rgba(255, 255, 255, 0.1) !important;
            border: 1px solid rgba(255, 255, 255, 0.2) !important;
            color: #ffffff !important;
            border-radius: 12px !important;
            padding: 0.8rem 1rem !important;
            font-size: 1rem;
            box-shadow: none !important;
        }
        
        .stChatInput textarea:focus {
            background-color: rgba(255, 255, 255, 0.15) !important;
            border-color: #00d4ff !important;
            box-shadow: 0 0 15px rgba(0, 212, 255, 0.1) !important;
        }
        
        /* Adjust main container */
        .main .block-container {
            padding-bottom: 100px !important;
            max-width: 1000px;
        }
        
        /* Header Styling - Transparent but Visible for Hamburger */
        [data-testid="stHeader"] {
            background: transparent !important;
            color: white !important;
        }
        
        /* Style the hamburger menu button if possible (Streamlit specific) */
        [data-testid="stHeader"] button {
            color: white !important;
        }

        /* Sidebar Styling */
        [data-testid="stSidebar"] {
            background-color: rgba(15, 32, 39, 0.8); /* Slightly more opaque */
            backdrop-filter: blur(20px);
            border-right: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        /* Chat Message Bubbles */
        [data-testid="stChatMessageContent"] {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            color: #ffffff;
            border-radius: 15px;
        }

        /* Hide Footer only */
        footer {visibility: hidden;}
        #MainMenu {visibility: visible;} /* Ensure menu is visible */
    </style>
    """

# --- Page Config ---
st.set_page_config(
    page_title="BankBot FAQ",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Inject Custom CSS ---
st.markdown(get_custom_css(), unsafe_allow_html=True)

# --- Session State Initialization ---
if 'history' not in st.session_state:
    st.session_state.history = [] # List of past conversations
if 'current_chat' not in st.session_state:
    st.session_state.current_chat = [
        {"role": "assistant", "content": "Hello! I'm your Banking Assistant. Ask me anything about our services or upload a document for review.", "timestamp": datetime.now().strftime("%H:%M")}
    ]
if 'chat_id' not in st.session_state:
    st.session_state.chat_id = str(uuid.uuid4())


# --- Backend Initialization (Cached) ---
@st.cache_resource
def get_backend():
    backend = None
    engine = None
    ollama_status = False

    # Initialize RAG Backend
    if BACKEND_AVAILABLE:
        try:
            backend = BankBotBackend()
            backend.initialize_knowledge_base()
        except Exception as e:
            print(f"Error initializing backend: {e}")
            backend = None

    # Initialize LLM Engine
    if LLM_AVAILABLE:
        try:
            engine = LLMEngine()
            
            # Check Ollama Connectivity
            try:
                import requests
                response = requests.get("http://127.0.0.1:11434", timeout=1)
                if response.status_code == 200:
                    ollama_status = True
            except:
                ollama_status = False
        except Exception as e:
            print(f"Error initializing LLM Engine: {e}")
            engine = None
            
    return backend, engine, ollama_status

backend, engine, ollama_online = get_backend()

# --- Helper Functions ---
def start_new_chat():
        # Generate a context-based title using LLM
        title_text = "New Chat"
        if len(st.session_state.current_chat) > 1:
            try:
                # Extract conversation context
                conversation_text = ""
                for msg in st.session_state.current_chat:
                    if msg['role'] == 'user':
                        conversation_text += f"User: {msg['content']}\n"
                
                # Use LLM to summarize if available
                if engine and ollama_online and conversation_text:
                    prompt = "Summarize this banking query into a single short 2-3 word title (e.g., 'Credit Card Fees', 'Account Opening'). Do not use quotes or punctuation."
                    # We pass empty context chunks as we don't need RAG for summarization
                    summary = engine.query_ollama(conversation_text, [], system_instructions=prompt)
                    title_text = summary.strip().replace('"', '').replace("'", "")
                    # Fallback if specific failure or too long
                    if len(title_text) > 40: 
                        title_text = title_text[:37] + "..."
                else:
                    # Fallback to simple truncation
                    first_user_msg = st.session_state.current_chat[1]['content']
                    title_text = (first_user_msg[:30] + '...') if len(first_user_msg) > 30 else first_user_msg
            except Exception as e:
                print(f"Title generation error: {e}")
                first_user_msg = st.session_state.current_chat[1]['content']
                title_text = (first_user_msg[:30] + '...') if len(first_user_msg) > 30 else first_user_msg

        st.session_state.history.insert(0, {
            "id": st.session_state.chat_id,
            "title": title_text,
            "messages": st.session_state.current_chat,
            "preview": st.session_state.current_chat[1]['content'][:50] + "..." if len(st.session_state.current_chat) > 1 else "New Chat"
        })
        st.session_state.chat_id = str(uuid.uuid4())
        st.session_state.current_chat = [
             {"role": "assistant", "content": "Hello! I'm your Banking Assistant. Ask me anything about our services or upload a document for review.", "timestamp": datetime.now().strftime("%H:%M")}
        ]

def load_chat(chat_data):
    st.session_state.current_chat = chat_data["messages"]
    st.session_state.chat_id = chat_data["id"]

def process_user_input(user_text, uploaded_file=None):
    """Processes user input and generates a response using the backend."""
    
    # Add User Message to Chat
    new_msg = {
        "role": "user", 
        "content": user_text if user_text else "Sent a file.",
        "timestamp": datetime.now().strftime("%H:%M")
    }
    
    if uploaded_file:
        new_msg["image"] = uploaded_file
        new_msg["content"] += " (File Uploaded)"
        
    st.session_state.current_chat.append(new_msg)
    
    # Generate Bot Response
    with st.spinner("Analyzing..."):
        bot_response = ""
        
        if backend and engine and ollama_online:
            try:
                # 1. Retrieve Context
                context = backend.query_knowledge_base(user_text)
                
                # 2. Generate Response
                bot_response = engine.query_ollama(user_text, context)
            except Exception as e:
                bot_response = f"I encountered an error processing your request: {str(e)}"
        else:
            # Fallback / Simulation Mode
            time.sleep(1.0)
            if not ollama_online:
                 bot_response = "⚠️ **System Offline:** I cannot generate a smart response because my AI brain (Ollama) is disconnected. Please run `ollama serve` in your terminal."
            else:
                 bot_response = "Backend is not connected. I am running in UI-only mode."
            
            if uploaded_file:
                bot_response += " (File upload received)"

        st.session_state.current_chat.append({
            "role": "assistant",
            "content": bot_response,
            "timestamp": datetime.now().strftime("%H:%M")
        })
    st.rerun()

# --- Views ---

def sidebar():
    # Deduplicate history
    seen_ids = set()
    unique_history = []
    for chat in st.session_state.history:
        if chat['id'] not in seen_ids:
            seen_ids.add(chat['id'])
            unique_history.append(chat)
    st.session_state.history = unique_history

    with st.sidebar:
        st.title("💬 BankBot")
        
        # Status Indicator
        if ollama_online:
            st.success("🟢 System Online")
        else:
            st.error("🔴 AI Offline")
            st.caption("Run `ollama serve` to enable AI.")
        
        # Navigation
        st.markdown("### 🧭 Navigation")

        if st.button("+ New Chat", use_container_width=True):
            start_new_chat()
            st.rerun()
            
        st.markdown("### 🕒 History")
        for chat in st.session_state.history:
            if st.button(f"{chat['title']}", key=chat['id'], use_container_width=True):
                load_chat(chat)
                st.rerun()
                
        st.markdown("---")
        st.markdown("### ⚙️ Actions")
        
        # Export Chat
        if st.session_state.current_chat:
            chat_text = "\\n".join([f"{msg['role'].upper()}: {msg['content']}" for msg in st.session_state.current_chat])
            st.download_button(
                label="📥 Export Chat",
                data=chat_text,
                file_name=f"bankbot_chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain",
                use_container_width=True
            )
            
        # Clear History
        if st.button("🗑️ Clear History", use_container_width=True):
            st.session_state.history = []
            start_new_chat()
            st.rerun()
            
        st.markdown("<div style='margin-top: 2rem; opacity: 0.5; font-size: 0.8rem; text-align: center;'>BankBot v1.0</div>", unsafe_allow_html=True)


def chat_interface():
    # Native Header
    st.markdown("<h1 style='text-align: center;'>Banking Assistant</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; margin-bottom: 3rem;'>Ask questions or upload documents for analysis.</p>", unsafe_allow_html=True)
    
    # Display Chat Messages
    for message in st.session_state.current_chat:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "image" in message:
                st.image(message["image"])

    # FAQ Prompts (Only show if chat is empty/new)
    if len(st.session_state.current_chat) <= 1:
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        
        if col1.button("What's my balance?", use_container_width=True):
            process_user_input("What's my balance?")
        if col2.button("Compare credit cards", use_container_width=True):
            process_user_input("Compare credit cards")
        if col3.button("Reset my PIN", use_container_width=True):
            process_user_input("Reset my PIN")

    # Suggested Follow-up Questions
    if len(st.session_state.current_chat) > 1 and st.session_state.current_chat[-1]["role"] == "assistant":
        st.markdown("<br>", unsafe_allow_html=True)
        st.caption("Suggested:")
        cols = st.columns(3)
        suggestions = ["How do I open an account?", "Interest rates?", "Contact support"]
        
        for i, sugg in enumerate(suggestions):
            if cols[i].button(sugg, key=f"sugg_{len(st.session_state.current_chat)}_{i}", use_container_width=True):
                process_user_input(sugg)

    # File Uploader - Native Streamlit
    with st.container():
        uploaded_file = st.file_uploader("Upload Document", type=['png', 'jpg', 'jpeg', 'pdf'], key="chat_uploader", label_visibility="collapsed")

    # Chat Input
    if prompt := st.chat_input("Type your question here..."):
        process_user_input(prompt, uploaded_file)

# --- Main App Logic ---
def main():
    sidebar()
    chat_interface()

if __name__ == "__main__":
    main()
