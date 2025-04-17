import streamlit as st
import hashlib
from cryptography.fernet import Fernet
from streamlit_extras.switch_page_button import switch_page

# --- UI CONFIG ---
st.set_page_config(page_title="SecureLock 🔐", page_icon="🛡️", layout="centered")

# --- CUSTOM BACKGROUND STYLE ---
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #fbeaff, #f4e1f5, #f3f3ff);
        background-attachment: fixed;
        font-family: 'Segoe UI', sans-serif;
    }
    .css-1d391kg, .css-1v3fvcr {
        background-color: rgba(255, 255, 255, 0.7) !important;
        backdrop-filter: blur(10px);
        border-radius: 10px;
    }
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background: linear-gradient(160deg, #d1c4e9, #ede7f6);
        color: #4A0072;
        backdrop-filter: blur(8px);
        border-right: 2px solid #b39ddb;
    }
    section[data-testid="stSidebar"] .css-1v3fvcr {
        background-color: transparent !important;
    }
    .footer-text {
        text-align: center;
        font-size: 18px;
        font-weight: bold;
        color: #6A1B9A;
        margin-top: 30px;
        text-transform: uppercase;
        letter-spacing: 2px;
    }
    </style>
""", unsafe_allow_html=True)

# --- GLOBAL SETUP ---
KEY = b'Dq6UuyS5aYoJdB7c5f0gZV7fUZK_F0OG4GLJ3C8j3sA='
cipher = Fernet(KEY)

stored_data = {}
if 'failed_attempts' not in st.session_state:
    st.session_state.failed_attempts = 0
if 'is_logged_in' not in st.session_state:
    st.session_state.is_logged_in = True

# --- UTILS ---
def hash_passkey(passkey: str) -> str:
    return hashlib.sha256(passkey.encode()).hexdigest()

def encrypt_data(text: str) -> str:
    return cipher.encrypt(text.encode()).decode()

def decrypt_data(encrypted_text: str) -> str:
    return cipher.decrypt(encrypted_text.encode()).decode()

# --- HEADER ---
st.markdown("<h1 style='text-align:center; color:#4A0072;'>🔐 SecureLock</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#6A1B9A;'>An encrypted storage system using passkey protection 🔏</p>", unsafe_allow_html=True)
st.markdown("---")

# --- SIDEBAR NAV ---
page = st.sidebar.radio("📁 Navigation", ["🏠 Home", "📥 Store Data", "📤 Retrieve Data", "🔑 Login"])

# --- HOME PAGE ---
if page == "🏠 Home":
    st.subheader("Welcome 👋")
    st.info("Use **SecureLock** to safely store secret data and retrieve it with a unique passkey. Data is encrypted using advanced security.")

# --- STORE DATA PAGE ---
elif page == "📥 Store Data":
    st.subheader("📥 Securely Store Your Data")
    user_data = st.text_area("📝 Enter text to encrypt", placeholder="Write something secret...")
    passkey = st.text_input("🔑 Create a passkey", type="password")

    if st.button("🔒 Encrypt & Save"):
        if user_data and passkey:
            hashed = hash_passkey(passkey)
            encrypted = encrypt_data(user_data)
            stored_data[encrypted] = {"encrypted_text": encrypted, "passkey_hash": hashed}
            st.success("✅ Data encrypted and saved in memory.")
            st.code(encrypted, language='text')
        else:
            st.warning("⚠️ Please enter both data and passkey.")

# --- RETRIEVE DATA PAGE ---
elif page == "📤 Retrieve Data":
    st.subheader("📤 Decrypt Stored Data")
    encrypted_input = st.text_area("🔐 Paste your encrypted text")
    passkey_input = st.text_input("🔑 Enter your passkey", type="password")

    if not st.session_state.is_logged_in:
        st.warning("🚫 You must re-login after 3 failed attempts.")
        st.stop()

    if st.button("🔓 Decrypt"):
        if encrypted_input and passkey_input:
            hashed_pass = hash_passkey(passkey_input)
            found = False

            for key, val in stored_data.items():
                if val["encrypted_text"] == encrypted_input and val["passkey_hash"] == hashed_pass:
                    decrypted = decrypt_data(encrypted_input)
                    st.success("✅ Data decrypted successfully!")
                    st.text_area("🗝️ Your original text:", value=decrypted, height=150)
                    st.session_state.failed_attempts = 0
                    found = True
                    break

            if not found:
                st.session_state.failed_attempts += 1
                remaining = 3 - st.session_state.failed_attempts
                st.error(f"❌ Incorrect passkey! Attempts remaining: {remaining}")

                if st.session_state.failed_attempts >= 3:
                    st.session_state.is_logged_in = False
                    st.warning("🔒 Too many failed attempts! Please log in again.")
                    st.experimental_rerun()
        else:
            st.warning("⚠️ All fields are required!")

# --- LOGIN PAGE ---
elif page == "🔑 Login":
    st.subheader("🔐 Reauthorize Access")
    master_pass = st.text_input("🔐 Enter master password to continue", type="password")

    if st.button("Login"):
        if master_pass == "admin123":
            st.session_state.failed_attempts = 0
            st.session_state.is_logged_in = True
            st.success("✅ Login successful. You can now retry decryption.")
        else:
            st.error("❌ Invalid master password!")

# --- FOOTER --- 
st.markdown("<div class='footer-text'>Created by Maryam</div>", unsafe_allow_html=True)
