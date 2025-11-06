import streamlit as st
from db import SessionLocal
from sqlalchemy import text
import hashlib

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()
    
def login(self, username, password):
    try:
        stmt = text("SELECT * FROM users WHERE username = :username")
        
        # Gunakan mappings() agar bisa akses dengan nama kolom
        result = self.session.execute(stmt, {"username": username}).mappings().fetchone()
        
        if result and password == result['password']:
            st.session_state['login'] = True
            st.session_state['username'] = username
            st.session_state['role'] = result['role']
            return True
        return False
    except Exception as e:
        st.error(f"Error login: {e}")
        return False


