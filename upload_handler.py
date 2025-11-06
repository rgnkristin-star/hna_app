import pandas as pd
import streamlit as st
from db import SessionLocal

def process_upload(file, region, mitra, bulan, tahun, user):
    try:
        df = pd.read_excel(file)
        expected_cols = ["Kode Item","Nama Barang","Group Transaki","Satuan", "HNA"]
        if list(df.columns) != expected_cols:
            st.error("Format kolom tidak sesuai template!")
            return
        
        # Validasi HNA harus numeric
        if not pd.api.types.is_numeric_dtype(df['HNA']):
            st.error("Kolom HNA harus berisi angka! Pastikan format angka tanpa titik/koma.")
            return
        
        df['Region'] = region
        df['Mitra'] = mitra
        df['Periode Bulan'] = bulan
        df['Periode Tahun'] = tahun
        df['Uploaded By'] = user
        
        session = SessionLocal()
        for _, row in df.iterrows():
            session.execute("""
            INSERT INTO hna_data 
            (region, mitra, kode_item, nama_barang, group_transaksi, satuan, hna, periode_bulan, periode_tahun, uploaded_by)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, (row['Region'], row['Mitra'], row['Kode Item'], row['Nama Barang'], 
                  row['Group Transaki'], row['Satuan'], float(row['HNA']), bulan, tahun, user))
        session.commit()
        session.close()
        st.success("File berhasil diupload!")
    except Exception as e:
        st.error(f"Error: {e}")