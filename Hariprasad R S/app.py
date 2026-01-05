import streamlit as st
import requests
from datetime import datetime

st.set_page_config(page_title="BankBot AI", page_icon="🤖", layout="wide")

# ---------------- Global Welcome Message ----------------
welcome_msg = (
    "Welcome to BankBot! Enter your banking-related query.\n\n"
    "Common topics include: Loan Plans, Account Opening, ATM / Cash Issues, "
    "Card Blocking, Bank Timings, Net Banking, FD Interest Rates, and RD Plans."
)

# ---------------- Banking Scope Restriction ----------------
BANKING_KEYWORDS = [
    "bank", "account", "loan", "interest", "atm", "card",
    "deposit", "fd", "rd", "net banking", "upi",
    "transaction", "balance", "statement", "cheque",
    "kyc", "branch", "ifsc"
]

def is_banking_query(text: str) -> bool:
    text = text.lower()
    return any(keyword in text for keyword in BANKING_KEYWORDS)

RESTRICTED_RESPONSE = (
    "⚠️ I can assist with banking-related queries such as:\n"
    "Loans, Accounts, ATM issues, Cards, Deposits, Net Banking, FD, RD."
)

# ---------------- Ollama call ----------------
def ask_ollama(prompt: str, model: str = "mistral") -> str:
    try:
        resp = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": model, "prompt": prompt},
            timeout=120,
        )
        # Check if the response is valid JSON and extract the 'response' field
        if resp.status_code == 200:
            return resp.json().get("response", "⚠️ No response or valid content from Ollama.")
        else:
            return f"⚠️ Ollama API returned status code {resp.status_code}: {resp.text}"
    except requests.exceptions.ConnectionError:
        return "⚠️ Connection Error: Could not connect to Ollama at http://localhost:11434. Please ensure Ollama is running."
    except Exception as e:
        return f"⚠️ Ollama error: {e}"

# ---------------- FAQ Knowledge Base ----------------
# The FAQ data is kept for direct matching/lookup from user input
faq_data = {
    "loan plans": """Here are our available loan plans:

1. Home Loan — Up to ₹50 lakhs (from 7.5% p.a)
2. Personal Loan — Up to ₹10 lakhs (from 12.0% p.a)
3. Car Loan — Up to ₹20 lakhs (from 8.0% p.a)
4. Education Loan — Up to ₹50 lakhs (from 7.5% p.a)
5. Business Loan — Up to ₹1 crore (from 10.0% p.a)
6. Gold Loan — Borrow up to 80% of gold value.
""",
    "account opening": "To open an account you need ID proof, address proof, passport-size photo and an initial deposit.",
    "atm / cash issues": "For ATM issues, contact customer support with your transaction ID and time.",
    "card blocking": "Block your card instantly using our mobile app or phone banking.",
    "bank timings": "Bank branches operate from 9:00 AM to 4:00 PM, Monday–Friday.",
    "net banking": "Activate net banking via 'New User Registration' on our website using your account number and OTP.",
    "fd interest rates": "FD rates range between 6.0% and 7.5% depending on tenure.",
    "rd plans": "RD tenure ranges from 6 months to 10 years with competitive interest rates.",
}

# ---------------- Helpers ----------------
def timestamp_now() -> str:
    return datetime.now().strftime("%H:%M")

def get_chat_title(chat_name: str) -> str:
    msgs = st.session_state.all_chats.get(chat_name, [])
    # Find the first user message for the title
    for s, m, _ in msgs:
        if s == "You":
            return m[:20] + "..." if len(m) > 20 else m
    return "(Empty Chat)"

# ---------------- Session State Init ----------------
if "all_chats" not in st.session_state:
    st.session_state.all_chats = {"Chat 1": []}
    st.session_state.all_chats["Chat 1"].append(
        ("BankBot", welcome_msg, timestamp_now())
    )

if "current_chat" not in st.session_state:
    st.session_state.current_chat = "Chat 1"

if "chat_counter" not in st.session_state:
    st.session_state.chat_counter = 1

# ---------------- Sidebar ----------------
with st.sidebar:
    st.title("Chat History")

    if st.button("➕ New Chat"):
        st.session_state.chat_counter += 1
        new_chat = f"Chat {st.session_state.chat_counter}"
        st.session_state.all_chats[new_chat] = [
            ("BankBot", welcome_msg, timestamp_now())
        ]
        st.session_state.current_chat = new_chat
        st.rerun()

    st.write("---")
    st.subheader("Previous Chats")

    # Display chat history buttons
    for cname in reversed(list(st.session_state.all_chats.keys())):
        if st.button(get_chat_title(cname), key=f"chat_{cname}", use_container_width=True):
            st.session_state.current_chat = cname

    st.write("---")
    if st.button("🗑 Clear All Chat History", use_container_width=True):
        st.session_state.clear()
        st.rerun()

# ---------------- Main UI ----------------
st.title("🏦 BankBot — AI Chat for Banking Support")
st.write(f"💬 Current Chat: {get_chat_title(st.session_state.current_chat)}")
st.write("---")

# ---------------- Conversation ----------------
st.subheader("Conversation")

for sender, msg, ts in st.session_state.all_chats[st.session_state.current_chat]:
    # Use st.chat_message for a more native Streamlit look
    with st.chat_message("user" if sender == "You" else "assistant"):
        st.markdown(msg)
        st.caption(f"{ts}")

# ---------------- Bottom Input ----------------
with st.form("chat_form", clear_on_submit=True):
    user_text = st.text_input("Message BankBot…")
    send = st.form_submit_button("Send")

if send and user_text.strip():
    ts = timestamp_now()
    st.session_state.all_chats[st.session_state.current_chat].append(("You", user_text, ts))

    low = user_text.lower()
    reply = None

    # Step 1: FAQ Match (if a user types a common query like "loan plans")
    for k, v in faq_data.items():
        if k in low:
            reply = v
            break

    # Step 2: Banking-only validation / Ollama call
    if not reply:
        if is_banking_query(user_text):
            # For better context, prepend a summary of the current chat history to the prompt
            history_summary = "\n".join([
                f"{s}: {m}" for s, m, _ in st.session_state.all_chats[st.session_state.current_chat]
            ])
            
            prompt = (
                "You are BankBot, a helpful banking assistant. "
                "Answer ONLY banking-related questions. "
                "If the question is not about banking, you must state that you cannot assist with that topic. "
                "Keep your answers concise and professional.\n\n"
                "Current Conversation History:\n"
                f"{history_summary}\n\n"
                f"User Question: {user_text}"
            )
            reply = ask_ollama(prompt)
        else:
            reply = RESTRICTED_RESPONSE

    st.session_state.all_chats[st.session_state.current_chat].append(("BankBot", reply, ts))
    st.rerun()