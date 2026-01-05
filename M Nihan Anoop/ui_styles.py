# Styles module for BankBot - Updated 2025-12-02 21:00
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

        /* Premium Animated Background */
        .stApp {
            background: linear-gradient(-45deg, #0f0c29, #302b63, #24243e, #141e30);
            background-size: 400% 400%;
            animation: gradient 15s ease infinite;
        }

        @keyframes gradient {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }

        /* Header Styling (Native st.title) */
        h1 {
            background: linear-gradient(to right, #00c6ff, #0072ff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-align: center;
            font-size: 3.5rem !important;
            padding-bottom: 1rem;
            text-shadow: 0 0 30px rgba(0, 114, 255, 0.3);
        }
        
        /* Subheader/Text Styling */
        p {
            font-size: 1.1rem;
            line-height: 1.6;
            color: rgba(255, 255, 255, 0.9);
        }

        /* Glassmorphic Buttons */
        .stButton > button {
            background: rgba(255, 255, 255, 0.05) !important;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            color: white !important;
            border-radius: 12px !important;
            padding: 0.75rem 1.5rem !important;
            transition: all 0.3s ease !important;
            font-weight: 500 !important;
        }
        
        .stButton > button:hover {
            background: rgba(255, 255, 255, 0.15) !important;
            border-color: #00c6ff !important;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
        }

        /* Chat Input Styling */
        .stChatInput textarea {
            background-color: rgba(0, 0, 0, 0.3) !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            color: white !important;
            border-radius: 15px !important;
        }
        
        .stChatInput textarea:focus {
            border-color: #00c6ff !important;
            box-shadow: 0 0 15px rgba(0, 198, 255, 0.3) !important;
        }

        /* Sidebar Styling */
        [data-testid="stSidebar"] {
            background-color: rgba(0, 0, 0, 0.2);
            backdrop-filter: blur(20px);
            border-right: 1px solid rgba(255, 255, 255, 0.05);
        }
        
        /* File Uploader Styling */
        [data-testid="stFileUploader"] {
            margin-top: 1rem;
        }
        
        /* Hide Streamlit Branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
    </style>
    """
