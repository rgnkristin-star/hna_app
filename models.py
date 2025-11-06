import pandas as pd
import streamlit as st
from sqlalchemy import text
from fuzzywuzzy import process

def format_currency_id(value):
    """Format angka menjadi format mata uang Indonesia (15.700.000)"""
    if pd.isna(value) or value == '':
        return ''
    try:
        # Pastikan value adalah numeric
        value = float(value)
        # Format dengan pemisah ribuan (titik) tanpa desimal
        return f"{value:,.0f}".replace(",", ".")
    except (ValueError, TypeError):
        return str(value)        

class UserManager:
    def __init__(self, session):
        self.session = session

    def login(self, username, password):
        try:
            stmt = text("SELECT * FROM users WHERE username = :username")
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

    def add_user(self, username, password, role='user'):
        if st.session_state.get('role') != 'admin':
            st.warning("Hanya admin yang bisa menambahkan user")
            return
        try:
            # Check jika username tersedia
            check_stmt = text("SELECT username FROM users WHERE username = :username")
            existing_user = self.session.execute(check_stmt, {"username": username}).fetchone()
            
            if existing_user:
                st.error(f"Username {username} sudah ada!")
                return
                
            stmt = text("INSERT INTO users (username, password, role) VALUES (:username, :password, :role)")
            self.session.execute(stmt, {"username": username, "password": password, "role": role})
            self.session.commit()
            st.success(f"User {username} berhasil ditambahkan!")
        except Exception as e:
            st.error(f"Error tambah user: {e}")

class HNAData:
    def __init__(self, session):
        self.session = session

    def upload_excel(self, file, region, mitra, bulan, tahun, user):
        try:
            df = pd.read_excel(file)
            expected_cols = ["Kode Item","Nama Barang","Group Transaki","Satuan", "HNA"]
            if list(df.columns) != expected_cols:
                st.error("Format kolom tidak sesuai template!")
                return

            # Validasi kolom HNA harus numeric
            if not pd.api.types.is_numeric_dtype(df['HNA']):
                st.error("Kolom HNA harus berisi angka! Pastikan format angka tanpa titik/koma.")
                return
            
            success_count = 0
            for _, row in df.iterrows():
                # Skip empty rows
                if pd.isna(row['Kode Item']) or pd.isna(row['Nama Barang']):
                    continue
                    
                stmt = text("""
                    INSERT INTO hna_data 
                    (region, mitra, kode_item, nama_barang, group_transaksi, satuan, hna, periode_bulan, periode_tahun, uploaded_by)
                    VALUES (:region, :mitra, :kode_item, :nama_barang, :group_transaksi, :satuan, :hna, :bulan, :tahun, :user)
                """)
                self.session.execute(stmt, {
                    "region": region,
                    "mitra": mitra,
                    "kode_item": row['Kode Item'],
                    "nama_barang": row['Nama Barang'],
                    "group_transaksi": row['Group Transaki'],
                    "satuan": row['Satuan'],
                    "hna": row['HNA'],
                    "bulan": bulan,
                    "tahun": tahun,
                    "user": user
                })
                success_count += 1
                
            self.session.commit()
            st.success(f"File berhasil diupload! {success_count} data tersimpan.")
        except Exception as e:
            st.error(f"Error upload: {e}")

    def load_data(self):
        try:
            df = pd.read_sql("SELECT * FROM hna_data ORDER BY uploaded_at DESC", self.session.bind)
            return df
        except Exception as e:
            st.error(f"Error loading data: {e}")
            return pd.DataFrame()

    def filter_data(self, df, region=None, mitra=None, group=None, bulan=None, tahun=None):
        if region: df = df[df['region'] == region]
        if mitra: df = df[df['mitra'] == mitra]
        if group: df = df[df['group_transaksi'] == group]
        if bulan: df = df[df['periode_bulan'] == bulan]
        if tahun: df = df[df['periode_tahun'] == tahun]
        return df