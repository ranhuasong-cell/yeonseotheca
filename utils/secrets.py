import os
from dotenv import load_dotenv

load_dotenv()

def get_secret(key: str, default: str = "") -> str:
    try:
        import streamlit as st
        val = st.secrets.get(key)
        if val:
            return val
    except Exception:
        pass
    return os.getenv(key, default)
