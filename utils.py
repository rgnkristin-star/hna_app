import pandas as pd
from db import SessionLocal
from fuzzywuzzy import process

def load_data():
    session = SessionLocal()
    df = pd.read_sql("SELECT * FROM hna_data", session.bind)
    session.close()
    return df

def filter_data(df, region=None, mitra=None, group=None, bulan=None, tahun=None):
    if region:
        df = df[df['region'] == region]
    if mitra:
        df = df[df['mitra'] == mitra]
    if group:
        df = df[df['group_transaksi'] == group]
    if bulan:
        df = df[df['periode_bulan'] == bulan]
    if tahun:
        df = df[df['periode_tahun'] == tahun]
    return df

def search_similarity(df, query, column='nama_barang', limit=10):
    choices = df[column].tolist()
    results = process.extract(query, choices, limit=limit)
    return pd.DataFrame(results, columns=[column, 'Similarity'])
