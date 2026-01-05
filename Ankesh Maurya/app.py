import streamlit as st
import json
import os
import requests
from datetime import datetime
from PIL import Image
import pytesseract
import PyPDF2
import docx
from io import BytesIO
from difflib import get_close_matches
import hashlib
import re

st.set_page_config(
    page_title="BankBot - Banking Assistant",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
USERS_FILE = "users.json"
DEFAULT_MODEL = "qwen2.5:1.5b"

SYSTEM_PROMPT = """You are BankBot, a restricted banking assistant.
You must answer only banking, finance, or account-related questions.
If the question is not related to banking, reply exactly:
"I can assist only with banking-related queries."
Do not provide programming, medical, legal, personal, or general knowledge answers.
Do not speculate or invent information.
Be helpful, professional, and concise in your banking responses."""

BANKING_SYNONYMS = {
    "money": "balance",
    "funds": "balance",
    "cash": "balance",
    "salary": "salary account",
    "income": "salary account",
    "pay": "upi",
    "payment": "transaction",
    "send": "transfer",
    "receive": "credit",
    "withdrawal": "withdraw",
    "depositing": "deposit",
    "loan amount": "loan",
    "interest charge": "interest",
    "monthly payment": "emi",
    "installment": "emi",
    "card swipe": "debit card",
    "bank app": "mobile banking",
    "online transfer": "net banking"
}

def normalize_with_synonyms(text: str) -> str:
    text_lower = text.lower()
    for synonym, actual in BANKING_SYNONYMS.items():
        text_lower = text_lower.replace(synonym, actual)
    return text_lower

# Enhanced color system matching your requirements
COLOR_SYSTEM = {
    "light": {
        "bg": "#F8FAFC",
        "secondary_bg": "#FFFFFF",
        "sidebar_bg": "#FFFFFF",
        "text_primary": "#0F172A",
        "text_secondary": "#64748B",
        "user_bubble": "#3B82F6",
        "user_text": "#FFFFFF",
        "bot_bubble": "#EFF6FF",
        "bot_text": "#1E40AF",
        "border": "#E2E8F0",
        "accent": "#3B82F6",
        "accent_hover": "#60A5FA",
        "input_bg": "#FFFFFF",
        "button_primary": "#3B82F6",
        "button_hover": "#60A5FA",
        "icon_color": "#64748B",
        "document_box_bg": "#F1F5F9",  # Changed from dark to light gray
        "document_box_text": "#0F172A",  # Changed from light to dark text
        "chat_input_border": "#CBD5E1",
        "chat_input_bg": "#F8FAFC"  # Added new property for chat input background
    },
    "dark": {
        "bg": "#0F172A",
        "secondary_bg": "#1E293B",
        "sidebar_bg": "#1E293B",
        "text_primary": "#F1F5F9",
        "text_secondary": "#94A3B8",
        "user_bubble": "#60A5FA",
        "user_text": "#0F172A",
        "bot_bubble": "#1E40AF",
        "bot_text": "#EFF6FF",
        "border": "#334155",
        "accent": "#60A5FA",
        "accent_hover": "#3B82F6",
        "input_bg": "#1E293B",
        "button_primary": "#3B82F6",
        "button_hover": "#60A5FA",
        "icon_color": "#94A3B8",
        "chat_input_bg": "#1E293B"  # Added for consistency
    }
}

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=2)

def verify_login(username, password):
    users = load_users()
    hashed = hashlib.sha256(password.encode()).hexdigest()
    return username in users and users[username] == hashed

def create_user(username, password):
    users = load_users()
    if username in users:
        return False
    users[username] = hashlib.sha256(password.encode()).hexdigest()
    save_users(users)
    return True

def query_ollama(prompt, context="", model=DEFAULT_MODEL, temperature=0.7, num_predict=512):
    try:
        full_prompt = f"""{SYSTEM_PROMPT}

STRICT RULE:
If document context is provided, answer ONLY from it.
If the answer is not present, reply exactly:
"Answer not found in the provided document."
"""
        if context:
            full_prompt += f"Context from uploaded file:\n{context}\n\n"
        full_prompt += f"User: {prompt}\nAssistant:"

        payload = {
            "model": model,
            "prompt": full_prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": num_predict
            }
        }

        response = requests.post(OLLAMA_URL, json=payload, timeout=60)

        if response.status_code == 200:
            result = response.json()
            return result.get("response", "I apologize, but I couldn't process that request.")
        else:
            return "I'm currently unable to connect to the banking knowledge base. Please try again."

    except requests.exceptions.ConnectionError:
        return "Unable to connect to the banking assistant service. Please ensure Ollama is running."
    except requests.exceptions.Timeout:
        return "The request took too long. Please try a simpler question."
    except Exception:
        return "I encountered an error processing your request. Please try again."

def extract_text_from_pdf(file):
    try:
        pdf_reader = PyPDF2.PdfReader(BytesIO(file.read()))
        text = ""
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text
        return text
    except Exception as e:
        return f"Error extracting PDF: {str(e)}"

def extract_text_from_docx(file):
    try:
        doc = docx.Document(BytesIO(file.read()))
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return text
    except Exception as e:
        return f"Error extracting DOCX: {str(e)}"

def extract_text_from_image(file):
    try:
        image = Image.open(file)
        text = pytesseract.image_to_string(image)
        return text if text.strip() else "No text detected in image"
    except Exception as e:
        return f"Error extracting text from image: {str(e)}"

def extract_file_content(uploaded_file):
    file_type = uploaded_file.name.split('.')[-1].lower()
    if file_type == 'txt':
        return uploaded_file.read().decode('utf-8')
    elif file_type == 'pdf':
        return extract_text_from_pdf(uploaded_file)
    elif file_type == 'docx':
        return extract_text_from_docx(uploaded_file)
    elif file_type in ['png', 'jpg', 'jpeg']:
        return extract_text_from_image(uploaded_file)
    else:
        return "Unsupported file format"

def init_session_state():
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'username' not in st.session_state:
        st.session_state.username = ""
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'file_context' not in st.session_state:
        st.session_state.file_context = ""
    if 'file_name' not in st.session_state:
        st.session_state.file_name = ""
    if 'theme' not in st.session_state:
        st.session_state.theme = "light"
    if 'temperature' not in st.session_state:
        st.session_state.temperature = 0.7
    if 'max_tokens' not in st.session_state:
        st.session_state.max_tokens = 512
    if 'confirm_delete_history' not in st.session_state:
        st.session_state.confirm_delete_history = False
    if 'document_keywords' not in st.session_state:
        st.session_state.document_keywords = []
    if "scroll_to_bottom" not in st.session_state:
        st.session_state.scroll_to_bottom = False

def apply_banking_styles(theme):
    colors = COLOR_SYSTEM[theme]
    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        
        * {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        }}

        html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {{
            background-color: {colors['bg']} !important;
        }}

        [data-testid="stSidebar"] {{
            background-color: {colors['sidebar_bg']} !important;
            border-right: 1px solid {colors['border']};
        }}

        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {{
            color: {colors['text_primary']} !important;
        }}

        [data-testid="stSidebar"] * {{
            color: {colors['text_primary']} !important;
        }}

        /* Chat Messages */
        .stChatMessage {{
            padding: 1rem 1.25rem !important;
            border-radius: 1rem !important;
            margin-bottom: 1rem !important;
            line-height: 1.6 !important;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}

        .stChatMessage[data-testid*="user"] {{
            background-color: {colors['user_bubble']} !important;
            color: {colors['user_text']} !important;
            margin-left: 15% !important;
            border: none !important;
        }}

        .stChatMessage[data-testid*="user"] p {{
            color: {colors['user_text']} !important;
        }}

        .stChatMessage[data-testid*="assistant"] {{
            background-color: {colors['bot_bubble']} !important;
            color: {colors['bot_text']} !important;
            margin-right: 20% !important;
            border: 1px solid {colors['border']} !important;
        }}

        .stChatMessage[data-testid*="assistant"] p {{
            color: {colors['bot_text']} !important;
        }}

        /* Chat Input */
        .stChatInput {{
            border-radius: 1.5rem !important;
            border: 2px solid {colors.get('chat_input_border', colors['border'])} !important;
            background-color: {colors.get('chat_input_bg', colors['input_bg'])} !important;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05) !important;
        }}

        .stChatInput textarea {{
            color: {colors['text_primary']} !important;
            background-color: {colors.get('chat_input_bg', colors['input_bg'])} !important;
            font-size: 15px !important;
        }}

        .stChatInput textarea::placeholder {{
            color: {colors['text_secondary']} !important;
            font-size: 15px !important;
        }}

        /* Buttons */
        .stButton button {{
            border-radius: 0.75rem !important;
            font-weight: 500 !important;
            transition: all 0.2s ease !important;
            border: 1px solid {colors['border']} !important;
            background-color: {colors['secondary_bg']} !important;
            color: {colors['text_primary']} !important;
        }}

        .stButton button:hover {{
            background-color: {colors['button_hover']} !important;
            color: white !important;
            border-color: {colors['button_hover']} !important;
            transform: translateY(-1px) !important;
            box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3) !important;
        }}

        .stButton button[kind="primary"] {{
            background-color: {colors['button_primary']} !important;
            color: white !important;
            border: none !important;
        }}

        .stButton button[kind="primary"]:hover {{
            background-color: {colors['button_hover']} !important;
        }}

        /* Text Inputs */
        .stTextInput input, .stPasswordInput input {{
            border-radius: 0.75rem !important;
            border: 1px solid {colors['border']} !important;
            font-size: 15px !important;
            background-color: {colors['input_bg']} !important;
            color: {colors['text_primary']} !important;
        }}

        .stTextInput input:focus, .stPasswordInput input:focus {{
            border-color: {colors['accent']} !important;
            box-shadow: 0 0 0 2px {colors['accent']}30 !important;
        }}

        /* File Uploader */
        [data-testid="stFileUploader"] {{
            background-color: {colors.get('document_box_bg', colors['secondary_bg'])} !important;
            border: 1px dashed {colors['border']} !important;
            border-radius: 0.75rem !important;
            padding: 1rem !important;
        }}

        [data-testid="stFileUploader"] label {{
            color: {colors.get('document_box_text', colors['text_primary'])} !important;
            font-weight: 500 !important;
        }}

        [data-testid="stFileUploader"] small {{
            color: {colors.get('document_box_text', colors['text_secondary'])} !important;
        }}

        [data-testid="stFileUploader"] button {{
            background-color: {colors['accent']} !important;
            color: black !important;
            border: none !important;
            padding: 0.5rem 1rem !important;
            border-radius: 0.5rem !important;
            font-weight: 500 !important;
        }}

        [data-testid="stFileUploader"] button:hover {{
            background-color: {colors['accent_hover']} !important;
        }}

        /* Headers and Text */
        h1, h2, h3, h4, h5, h6 {{
            color: {colors['text_primary']} !important;
        }}

        p, span, div {{
            color: {colors['text_primary']} !important;
        }}

        .stMarkdown {{
            color: {colors['text_primary']} !important;
        }}

        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 0.5rem;
        }}

        .stTabs [data-baseweb="tab"] {{
            border-radius: 0.5rem !important;
            color: {colors['text_secondary']} !important;
            background-color: transparent !important;
        }}

        .stTabs [aria-selected="true"] {{
            background-color: {colors['accent']} !important;
            color: white !important;
        }}

        /* Divider */
        hr {{
            border-color: {colors['border']} !important;
        }}

        /* Success/Error/Warning Messages */
        .stSuccess {{
            background-color: #10B98120 !important;
            color: #059669 !important;
            border-radius: 0.75rem !important;
        }}

        .stError {{
            background-color: #EF444420 !important;
            color: #DC2626 !important;
            border-radius: 0.75rem !important;
        }}

        .stWarning {{
            background-color: #F59E0B20 !important;
            color: #D97706 !important;
            border-radius: 0.75rem !important;
        }}

        /* Custom Classes */
        .file-status {{
            padding: 0.875rem !important;
            border-radius: 0.75rem !important;
            background-color: {colors.get('document_box_bg', colors['secondary_bg'])} !important;
            border: 1px solid {colors.get('document_box_bg', colors['border'])} !important;
            font-size: 14px !important;
            color: {colors.get('document_box_text', colors['text_primary'])} !important;
            margin: 0.5rem 0 !important;
        }}

        .file-status strong {{
            color: {colors.get('document_box_text', colors['text_primary'])} !important;
        }}

        .info-box {{
            padding: 1rem !important;
            border-radius: 0.75rem !important;
            background-color: {colors['bot_bubble']} !important;
            border-left: 4px solid {colors['accent']} !important;
            font-size: 14px !important;
            color: {colors['bot_text']} !important;
            margin: 1rem 0 !important;
        }}

        /* Spinner */
        .stSpinner > div {{
            border-top-color: {colors['accent']} !important;
        }}

        /* Scrollbar */
        ::-webkit-scrollbar {{
            width: 8px;
            height: 8px;
        }}

        ::-webkit-scrollbar-track {{
            background: {colors['secondary_bg']};
        }}

        ::-webkit-scrollbar-thumb {{
            background: {colors['border']};
            border-radius: 4px;
        }}

        ::-webkit-scrollbar-thumb:hover {{
            background: {colors['accent']};
        }}

        /* Theme Toggle Button */
        .theme-toggle {{
            position: fixed;
            top: 1rem;
            right: 1rem;
            z-index: 999;
        }}
        </style>
    """, unsafe_allow_html=True)

def authentication_page():
    apply_banking_styles(st.session_state.theme)
    colors = COLOR_SYSTEM[st.session_state.theme]

    st.markdown(f"""
        <div style="text-align: center; margin: 3rem auto; max-width: 420px;">
            <div style="background: linear-gradient(135deg, {colors['accent']} 0%, {colors['accent_hover']} 100%); 
                        width: 80px; height: 80px; border-radius: 20px; margin: 0 auto 1.5rem; 
                        display: flex; align-items: center; justify-content: center; 
                        box-shadow: 0 10px 30px rgba(59, 130, 246, 0.3);">
                <span style="font-size: 40px;">🏦</span>
            </div>
            <h1 style="font-size: 36px; font-weight: 700; color: {colors['text_primary']}; margin-bottom: 0.5rem;">BankBot</h1>
            <p style="font-size: 16px; color: {colors['text_secondary']}; margin: 0;">Secure AI Banking Assistant</p>
        </div>
    """, unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["Login", "Create Account"])

    with tab1:
        st.markdown(f"""
            <div style="margin-bottom: 1.5rem;">
                <p style="color: {colors['text_secondary']}; font-size: 15px;">Sign in to access your banking assistant</p>
            </div>
        """, unsafe_allow_html=True)

        login_username = st.text_input("Username", placeholder="Enter your username", key="login_user")
        login_password = st.text_input("Password", type="password", placeholder="Enter your password", key="login_pass")

        if st.button("Sign In", type="primary", use_container_width=True):
            if login_username and login_password:
                if verify_login(login_username, login_password):
                    st.session_state.authenticated = True
                    st.session_state.username = login_username
                    st.rerun()
                else:
                    st.error("Email ID or password is incorrect. Please try again.", icon="❌")
            else:
                st.warning("Please enter your username and password", icon="⚠️")

    with tab2:
        st.markdown(f"""
            <div style="margin-bottom: 1.5rem;">
                <p style="color: {colors['text_secondary']}; font-size: 15px;">Create a new account to get started</p>
            </div>
        """, unsafe_allow_html=True)

        signup_username = st.text_input("Choose a username", placeholder="Username", key="signup_user")
        signup_password = st.text_input("Choose a password", type="password", placeholder="Password (min 6 characters)", key="signup_pass")
        signup_confirm = st.text_input("Confirm password", type="password", placeholder="Confirm password", key="signup_confirm")

        if st.button("Create Account", type="primary", use_container_width=True):
            if not signup_username or not signup_password or not signup_confirm:
                st.warning("Please fill in all fields", icon="⚠️")
            elif signup_password != signup_confirm:
                st.error("Passwords do not match", icon="❌")
            elif len(signup_password) < 6:
                st.error("Password must be at least 6 characters", icon="❌")
            else:
                if create_user(signup_username, signup_password):
                    st.success("Account created successfully! Please sign in.", icon="✅")
                else:
                    st.error("Username already exists", icon="❌")

BANKING_KEYWORDS = [
    "bank", "banking", "branch", "ifsc", "micr", "swift",
    "customer id", "cif", "account number",
    "account", "savings account", "current account", "salary account",
    "joint account", "zero balance account", "student account",
    "nri account", "demat account",
    "balance", "available balance", "ledger balance",
    "account statement", "mini statement", "passbook",
    "transaction", "credit", "debit", "transfer",
    "fund transfer", "money transfer", "bank transfer",
    "net banking", "internet banking", "mobile banking",
    "online banking", "digital banking",
    "upi", "upi id", "upi pin", "bhim",
    "google pay", "phonepe", "paytm",
    "neft", "rtgs", "imps", "ecs", "nach",
    "debit card", "credit card", "atm",
    "card limit", "card blocking",
    "loan", "personal loan", "home loan", "education loan",
    "car loan", "gold loan", "business loan",
    "interest", "interest rate", "emi",
    "fixed deposit", "fd", "recurring deposit", "rd",
    "kyc", "aadhaar", "pan card",
    "charges", "fees", "penalty",
    "cheque", "demand draft",
    "fraud", "otp", "mpin"
]

def fuzzy_match(text: str, keywords, cutoff=0.8) -> bool:
    words = text.lower().split()
    for word in words:
        if get_close_matches(word, keywords, n=1, cutoff=cutoff):
            return True
    return False

def is_banking_question(text: str) -> bool:
    text_norm = normalize_with_synonyms(text)
    if any(k in text_norm for k in BANKING_KEYWORDS):
        return True
    if st.session_state.get("document_keywords"):
        if any(k in text_norm for k in st.session_state.document_keywords):
            return True
    return fuzzy_match(text_norm, BANKING_KEYWORDS)

def extract_banking_terms(text: str):
    terms = BANKING_KEYWORDS
    found = sorted({t for t in terms if t in text.lower()})
    return found

def extract_keywords_from_document(text: str, base_keywords):
    text_lower = text.lower()
    return sorted({kw for kw in base_keywords if kw in text_lower})

def chunk_text(text, chunk_size=800, overlap=100):
    overlap = min(overlap, chunk_size - 1)
    chunks = []
    start = 0
    text_length = len(text)
    while start < text_length:
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start = end - overlap
    return chunks

def select_relevant_chunks(chunks, question, max_chunks=3):
    question_words = set(question.lower().split())
    scored = []
    for chunk in chunks:
        chunk_words = set(chunk.lower().split())
        score = len(question_words.intersection(chunk_words))
        scored.append((score, chunk))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [chunk for score, chunk in scored[:max_chunks] if score > 0]

def extract_questions_from_text(text: str):
    lines = re.split(r'\n|\.', text)
    questions = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if (line.endswith("?") or
            line.lower().startswith(("what", "how", "when", "where", "why", "who", "which", "can", "is", "are")) or
            "?" in line or
            line.lower().startswith(("explain", "describe", "define", "details of", "procedure for"))):
            questions.append(line)
    return questions

def get_banking_questions_from_document(text: str):
    all_questions = extract_questions_from_text(text)
    banking_questions = [q for q in all_questions if is_banking_question(q)]
    return banking_questions

def chat_interface():
    apply_banking_styles(st.session_state.theme)
    colors = COLOR_SYSTEM[st.session_state.theme]

    with st.sidebar:
        # Theme Toggle at Top
        st.markdown(f"""
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem; padding: 0.5rem 0;">
                <span style="font-size: 18px; font-weight: 600; color: {colors['text_primary']};">🏦 BankBot</span>
            </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns([3, 1])
        with col2:
            if st.button("🌓" if st.session_state.theme == "light" else "☀️", key="theme_toggle"):
                st.session_state.theme = "dark" if st.session_state.theme == "light" else "light"
                st.rerun()

        st.divider()

        # New Chat Section
        st.markdown(f"""<p style="font-size: 12px; color: {colors['text_secondary']}; font-weight: 600; margin-bottom: 0.75rem; text-transform: uppercase; letter-spacing: 0.5px;">💬 Chat</p>""", unsafe_allow_html=True)

        if st.button("➕ New Chat", use_container_width=True):
            if st.session_state.messages:
                first_question = next((m["content"] for m in st.session_state.messages if m["role"] == "user"), "New Chat")
                st.session_state.chat_history.insert(0, {
                    "title": first_question[:40] + ("..." if len(first_question) > 40 else ""),
                    "messages": st.session_state.messages.copy()
                })
            st.session_state.messages = []
            st.session_state.file_context = ""
            st.session_state.file_name = ""
            st.rerun()

        # Recent Chats
        if st.session_state.chat_history:
            st.markdown(f"""<p style="font-size: 11px; color: {colors['text_secondary']}; margin-top: 1rem; margin-bottom: 0.5rem; text-transform: uppercase; letter-spacing: 0.5px;">Recent Chats</p>""", unsafe_allow_html=True)
            for idx, chat in enumerate(st.session_state.chat_history):
                col1, col2 = st.columns([5, 1])
                with col1:
                    if st.button(f"{chat['title']}", key=f"load_{idx}", use_container_width=True):
                        st.session_state.messages = chat['messages'].copy()
                        st.rerun()
                with col2:
                    if st.button("×", key=f"delete_{idx}"):
                        st.session_state.chat_history.pop(idx)
                        st.rerun()

        if st.session_state.chat_history:
            if st.button("Delete History", use_container_width=True):
                st.session_state.confirm_delete_history = True

        if st.session_state.confirm_delete_history:
            st.warning("Delete all chat history?")
            col_yes, col_no = st.columns(2)
            with col_yes:
                if st.button("Yes"):
                    st.session_state.chat_history.clear()
                    st.session_state.confirm_delete_history = False
                    st.success("History deleted")
                    st.rerun()
            with col_no:
                if st.button("No"):
                    st.session_state.confirm_delete_history = False
                    st.rerun()

        st.divider()

        # Document Upload
        st.markdown(f"""<p style="font-size: 12px; color: {colors['text_secondary']}; font-weight: 600; margin-bottom: 0.75rem; text-transform: uppercase; letter-spacing: 0.5px;">📄 Document</p>""", unsafe_allow_html=True)

        uploaded_file = st.file_uploader(
            "Upload document",
            type=['txt', 'pdf', 'docx', 'png', 'jpg', 'jpeg'],
            label_visibility="collapsed"
        )

        if uploaded_file:
            with st.spinner("⏳ Processing..."):
                content = extract_file_content(uploaded_file)
                if content and content.strip():
                    st.session_state.file_context = content
                    st.session_state.document_keywords = extract_keywords_from_document(content, BANKING_KEYWORDS)
                    st.session_state.file_name = uploaded_file.name
                    st.success("Document loaded", icon="✅")
                else:
                    st.warning("⚠️ No readable text found")

            if st.button("Clear Document", use_container_width=True):
                st.session_state.file_context = ""
                st.session_state.file_name = ""
                st.rerun()

        elif st.session_state.file_context:
            st.markdown(f"""
                <div class="file-status">
                    📎 {st.session_state.file_name}
                </div>
            """, unsafe_allow_html=True)
            if st.button("Clear Document", use_container_width=True):
                st.session_state.file_context = ""
                st.session_state.file_name = ""
                st.rerun()

        st.divider()

        # User Info and Sign Out
        st.markdown(f"""
            <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px; color: {colors['text_primary']};">
                👤 <span style="font-size: 14px; font-weight: 500;">{st.session_state.username}</span>
            </div>
        """, unsafe_allow_html=True)

        if st.button("Sign Out", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.username = ""
            st.session_state.messages = []
            st.session_state.file_context = ""
            st.session_state.file_name = ""
            st.rerun()

    # Main Chat Area
    # st.markdown(f"""
    #     <h1 style="font-size: 32px; font-weight: 700; color: {colors['text_primary']}; margin: 1.5rem 0 0.5rem 0;">
    #         🏦 Banking Assistant
    #     </h1>
    #     <p style="font-size: 14px; color: {colors['text_secondary']}; margin-bottom: 2rem;">
    #         Your secure AI-powered banking helper
    #     </p>
    # """, unsafe_allow_html=True)

    # Welcome Message
    if not st.session_state.messages and not st.session_state.file_context:
        st.markdown(f"""
            <div style="text-align: center; margin: 4rem auto; max-width: 600px;">
                <div style="background: linear-gradient(135deg, {colors['accent']} 0%, {colors['accent_hover']} 100%); 
                            width: 100px; height: 100px; border-radius: 24px; margin: 0 auto 2rem; 
                            display: flex; align-items: center; justify-content: center; 
                            box-shadow: 0 10px 40px rgba(59, 130, 246, 0.3);">
                    <span style="font-size: 50px;">🏦</span>
                </div>
                <h2 style="font-size: 24px; font-weight: 600; color: {colors['text_primary']}; margin-bottom: 1rem;">
                    Welcome to BankBot Secure
                </h2>
                <p style="font-size: 16px; color: {colors['text_secondary']}; line-height: 1.6;">
                    How can I assist you with your banking needs today?
                </p>
                <div style="margin-top: 2rem; text-align: left; padding: 1.5rem; background-color: {colors['secondary_bg']}; border-radius: 1rem; border: 1px solid {colors['border']};">
                    <p style="font-size: 14px; color: {colors['text_secondary']}; margin-bottom: 0.75rem; font-weight: 600;">
                        💡 I can help you with:
                    </p>
                    <ul style="font-size: 14px; color: {colors['text_secondary']}; margin: 0; padding-left: 1.5rem; line-height: 2;">
                        <li>Account information and balances</li>
                        <li>Loans, EMIs, and interest rates</li>
                        <li>Cards, UPI, and digital banking</li>
                        <li>KYC and document verification</li>
                        <li>Transaction queries and support</li>
                    </ul>
                </div>
            </div>
        """, unsafe_allow_html=True)

    # Document Info Box
    if st.session_state.file_context:
        terms = extract_banking_terms(st.session_state.file_context)
        st.markdown(f"""
            <div class="info-box">
                <strong>Document Active:</strong> {st.session_state.file_name}<br>
                <small style="color: {colors['text_secondary']};">
                    <strong>Banking terms detected:</strong> {", ".join(terms[:5]) if terms else "None"}{" and more..." if len(terms) > 5 else ""}
                </small>
            </div>
        """, unsafe_allow_html=True)

    # Display Messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # Chat Input
    user_input = st.chat_input("Ask about loans, KYC, transactions...")

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})

        if user_input.lower().strip() == "answer" and st.session_state.file_context:
            banking_questions = get_banking_questions_from_document(st.session_state.file_context)
            if not banking_questions:
                response = "No banking-related questions were found in the uploaded document."
            else:
                answers = []
                chunks = chunk_text(st.session_state.file_context)
                for idx, question in enumerate(banking_questions, start=1):
                    if idx > 20:
                        break
                    relevant_chunks = select_relevant_chunks(chunks, question)
                    context = "\n\n".join(relevant_chunks)
                    answer = query_ollama(question, context=context, temperature=0.2, num_predict=200)
                    answers.append(f"**Q{idx}. {question}**\n\n{answer}")
                response = "\n\n---\n\n".join(answers)

        elif not is_banking_question(user_input):
            response = "I can assist only with banking-related queries."

        else:
            context_to_use = ""
            if st.session_state.file_context:
                chunks = chunk_text(st.session_state.file_context)
                relevant_chunks = select_relevant_chunks(chunks, user_input)
                if relevant_chunks:
                    context_to_use = "\n\n".join(relevant_chunks)

            with st.spinner("Thinking..."):
                response = query_ollama(
                    user_input,
                    context=context_to_use,
                    temperature=st.session_state.temperature,
                    num_predict=st.session_state.max_tokens
                )

        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()

def main():
    init_session_state()
    if not st.session_state.authenticated:
        authentication_page()
    else:
        chat_interface()

if __name__ == "__main__":
    main()