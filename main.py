import streamlit as st
import pandas as pd
import io
from db import SessionLocal
from models import HNAData, format_currency_id
from models_penunjang import PemeriksaanPenunjang
from sidebar_manager import SidebarManager
from fuzzywuzzy import process
import re
from themes import get_theme_css  

# Set page config
st.set_page_config(
    page_title="HNA Comparison System",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# untuk tema, st.session
if 'theme' not in st.session_state:
    st.session_state.theme = 'light'

# Initialize session and managers
session = SessionLocal()
sidebar_mgr = SidebarManager(session)
hna_mgr = HNAData(session)
penunjang_mgr = PemeriksaanPenunjang(session)

# Apply selected theme
theme_css = get_theme_css(st.session_state.theme)
st.markdown(theme_css, unsafe_allow_html=True)

# Meta untuk memaksa light theme
st.markdown(
    """
    <meta name="color-scheme" content="light">
    <meta name="theme-color" content="#007bff">
    """,
    unsafe_allow_html=True
)

def preprocess_text(text):
    """Preprocess text untuk similarity matching yang lebih akurat"""
    if pd.isna(text):
        return ""
    # Convert to lowercase, remove extra spaces, remove special characters
    text = str(text).lower().strip()
    text = re.sub(r'[^\w\s]', ' ', text)  
    text = re.sub(r'\s+', ' ', text)  
    return text

def advanced_similarity_search(df, query, column='nama_barang', threshold=85, limit=20):
    """Advanced similarity search dengan multiple strategies"""
    if not query or df.empty:
        return df
    
    query_processed = preprocess_text(query)
    choices = df[column].dropna().unique().tolist()
    
    if not choices:
        return pd.DataFrame()
    
    # Strategy 1: Exact match (case insensitive)
    exact_matches = df[df[column].str.lower() == query.lower()]
    if not exact_matches.empty:
        return exact_matches
    
    # Strategy 2: Contains match
    contains_matches = df[df[column].str.lower().str.contains(query.lower(), na=False)]
    if not contains_matches.empty:
        return contains_matches
    
    # Strategy 3: Fuzzy matching dengan processed text
    choices_processed = [preprocess_text(choice) for choice in choices]
    results = process.extract(query_processed, choices_processed, limit=limit)
    
    # Filter berdasarkan threshold dan ambil original names
    matched_original_names = []
    for processed_choice, score, original_choice in zip(choices_processed, [r[1] for r in results], choices):
        if score >= threshold:
            matched_original_names.append(original_choice)
    
    if matched_original_names:
        return df[df[column].isin(matched_original_names)]
    
    return pd.DataFrame()

def render_upload_page(hna_mgr):
    """Render upload data page"""
    # Download template
    template_df = pd.DataFrame(columns=["Kode Item", "Nama Barang", "Group Transaki", "Satuan", "HNA"])

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        template_df.to_excel(writer, index=False, sheet_name="Template HNA")
    
        worksheet = writer.sheets['Template HNA']
        for row in range(2, 5):
            cell = worksheet[f'E{row}']
            cell.number_format = '#,##0'

    st.download_button(
        label="📥 Download Template Excel",
        data=output.getvalue(),
        file_name="template_hna.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )

    # Upload form
    with st.form("upload_form"):
        col1, col2 = st.columns(2)
        with col1:
            region = st.text_input("Regional*", placeholder="Contoh: Jawa Barat")
            mitra = st.text_input("Nama Mitra*", placeholder="Contoh: St. Yusup")
        with col2:
            bulan = st.selectbox("Periode Bulan*", [""] + ["Januari","Februari","Maret","April","Mei","Juni",
                                                         "Juli","Agustus","September","Oktober","November","Desember"])
            tahun = st.number_input("Periode Tahun*", min_value=2000, max_value=2100, value=2025)
        
        uploaded_file = st.file_uploader("Pilih File Excel*", type=["xlsx"], help="Format harus sesuai template")
        
        submit_btn = st.form_submit_button("🚀 Upload File", use_container_width=True)
        
        if submit_btn:
            if not all([region, mitra, bulan, tahun, uploaded_file]):
                st.error("❌ Harap lengkapi semua field yang wajib diisi (*)")
            else:
                hna_mgr.upload_excel(uploaded_file, region, mitra, bulan, tahun, st.session_state['username'])

def render_data_page(hna_mgr):
    """Render data display page"""
    df = hna_mgr.load_data()
    
    if df.empty:
        st.warning("📭 Belum ada data HNA.")
        return
    
    # Filters
    st.subheader("🔍 Filter Data")
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    with col1:
        region_options = ["Semua"] + sorted(df['region'].unique().tolist())
        region_filter = st.selectbox("Region", region_options)
    with col2:
        mitra_options = ["Semua"] + sorted(df['mitra'].unique().tolist())
        mitra_filter = st.selectbox("Mitra", mitra_options)
    with col3:
        group_options = ["Semua"] + sorted(df['group_transaksi'].unique().tolist())
        group_filter = st.selectbox("Group Transaksi", group_options)
    with col4:
        satuan_options = ["Semua"] + sorted(df['satuan'].unique().tolist())
        satuan_filter = st.selectbox("Satuan", satuan_options)
    with col5:
        bulan_options = ["Semua"] + sorted(df['periode_bulan'].unique().tolist())
        bulan_filter = st.selectbox("Bulan", bulan_options)
    with col6:
        tahun_options = ["Semua"] + sorted(df['periode_tahun'].unique().tolist())
        tahun_filter = st.selectbox("Tahun", tahun_options)
    
    # Advanced search options
    st.subheader("🔎 Pencarian Nama Obat")
    name_query = st.text_input(
        "Masukkan nama barang", 
        placeholder="Contoh: VERBAN ELASTIS ELASTOMUL HAFT 8X4 PER CM",
        help="Pencarian akan mencari match exact terlebih dahulu, kemudian similarity"
    )
    
    # Search options - hidden, menggunakan session state
    if 'similarity_threshold' not in st.session_state:
        st.session_state.similarity_threshold = 85
    if 'search_mode' not in st.session_state:
        st.session_state.search_mode = "Auto (Exact + Similarity)"

    similarity_threshold = st.session_state.similarity_threshold
    search_mode = st.session_state.search_mode
    
    # Apply basic filters
    filtered_df = df.copy()
    
    if region_filter != "Semua":
        filtered_df = filtered_df[filtered_df['region'] == region_filter]
    if mitra_filter != "Semua":
        filtered_df = filtered_df[filtered_df['mitra'] == mitra_filter]
    if group_filter != "Semua":
        filtered_df = filtered_df[filtered_df['group_transaksi'] == group_filter]
    if satuan_filter != "Semua":
        filtered_df = filtered_df[filtered_df['satuan'] == satuan_filter]
    if bulan_filter != "Semua":
        filtered_df = filtered_df[filtered_df['periode_bulan'] == bulan_filter]
    if tahun_filter != "Semua":
        filtered_df = filtered_df[filtered_df['periode_tahun'] == tahun_filter]
    
    # Apply name search
    search_results = None
    if name_query:
        if search_mode == "Hanya Exact Match":
            # Exact match only
            search_results = filtered_df[filtered_df['nama_barang'].str.lower() == name_query.lower()]
        elif search_mode == "Hanya Similarity":
            # Similarity only
            search_results = advanced_similarity_search(
                filtered_df, name_query, 'nama_barang', similarity_threshold
            )
        else:  # Auto mode
            # Try exact match first
            exact_matches = filtered_df[filtered_df['nama_barang'].str.lower() == name_query.lower()]
            if not exact_matches.empty:
                search_results = exact_matches
                st.success("🎯 Ditemukan exact match!")
            else:
                # Fallback to similarity
                search_results = advanced_similarity_search(
                    filtered_df, name_query, 'nama_barang', similarity_threshold
                )
                if not search_results.empty:
                    st.info(f"🔍 Ditemukan {len(search_results)} hasil similarity (threshold: {similarity_threshold}%)")
                else:
                    st.warning("❌ Tidak ditemukan hasil untuk pencarian ini")
        
        if search_results is not None:
            filtered_df = search_results
    
    # Display results
    st.subheader(f"📋 Hasil Filter ({len(filtered_df)} data)")
    
    if not filtered_df.empty:
        # BUAT COPY UNTUK DISPLAY DENGAN FORMAT
        display_df = filtered_df.copy()
        
        # FORMAT KOLOM HNA untuk tampilan
        display_df['hna_formatted'] = display_df['hna'].apply(format_currency_id)
        
        # Reset index untuk membuat nomor urut
        display_df = display_df.reset_index(drop=True)
        display_df.index = display_df.index + 1
        display_df = display_df.rename_axis('No').reset_index()
        
        # Pilih kolom yang akan ditampilkan - gunakan hna_formatted
        selected_columns = [
            'No', 'region', 'mitra', 'kode_item', 'nama_barang', 
            'group_transaksi', 'satuan', 'hna_formatted', 'periode_bulan', 'periode_tahun', 
            'uploaded_by', 'uploaded_at'
        ]
        
        # Pastikan kolom yang diminta ada dalam dataframe
        available_columns = [col for col in selected_columns if col in display_df.columns]
        display_df = display_df[available_columns]
        
        # Rename kolom untuk tampilan yang lebih baik
        column_mapping = {
            'No': 'No',
            'region': 'Regional',
            'mitra': 'Mitra', 
            'kode_item': 'Kode Item',
            'nama_barang': 'Nama Barang',
            'group_transaksi': 'Group Transaksi',
            'satuan': 'Satuan',
            'hna_formatted': 'HNA',
            'periode_bulan': 'Periode Bulan',
            'periode_tahun': 'Periode Tahun',
            'uploaded_by': 'Uploaded By',
            'uploaded_at': 'Uploaded At'
        }
        
        display_df = display_df.rename(columns=column_mapping)
        
        # Show similarity scores jika dalam mode similarity
        if name_query and search_mode in ["Auto (Exact + Similarity)", "Hanya Similarity"] and not filtered_df.empty:
            similarity_scores = []
            for name in filtered_df['nama_barang']:
                score = process.extractOne(preprocess_text(name_query), [preprocess_text(name)])[1]
                similarity_scores.append(score)
            
            display_df['Similarity (%)'] = similarity_scores
            display_df = display_df.sort_values('Similarity (%)', ascending=False)
        
        # Format tanggal
        try:
            display_df['Uploaded At'] = pd.to_datetime(display_df['Uploaded At']).dt.strftime('%Y-%m-%d %H:%M')
        except:
            pass
        
        # Tampilkan dataframe
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        
        # Download button - dengan data asli (tanpa format)
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # Untuk download, gunakan dataframe asli tanpa formatting
            download_df = filtered_df.reset_index(drop=True)
            download_df.index = download_df.index + 1
            download_df = download_df.rename_axis('No').reset_index()
            
            # Pilih kolom untuk download (gunakan hna asli)
            download_columns = [
                'No', 'region', 'mitra', 'kode_item', 'nama_barang', 
                'group_transaksi', 'satuan', 'hna', 'periode_bulan', 'periode_tahun', 
                'uploaded_by', 'uploaded_at'
            ]
            download_columns = [col for col in download_columns if col in download_df.columns]
            download_df = download_df[download_columns]
            
            # Rename untuk download
            download_mapping = {
                'No': 'No',
                'region': 'Regional',
                'mitra': 'Mitra', 
                'kode_item': 'Kode Item',
                'nama_barang': 'Nama Barang',
                'group_transaksi': 'Group Transaksi',
                'satuan': 'Satuan',
                'hna': 'HNA',  
                'periode_bulan': 'Periode Bulan',
                'periode_tahun': 'Periode Tahun',
                'uploaded_by': 'Uploaded By',
                'uploaded_at': 'Uploaded At'
            }
            
            download_df = download_df.rename(columns=download_mapping)
            download_df.to_excel(writer, index=False, sheet_name='HNA Data')
            
            # Set format untuk kolom HNA di Excel
            worksheet = writer.sheets['HNA Data']
            for row in range(2, len(download_df) + 2):
                cell = worksheet[f'H{row}']
                cell.number_format = '#,##0'
        
        st.download_button(
            label="📥 Download Data",
            data=output.getvalue(),
            file_name="HNA_Data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    else:
        st.warning("Tidak ada data yang sesuai dengan filter yang dipilih")

def render_upload_page_penunjang(penunjang_mgr):
    """Render upload data pemeriksaan penunjang page"""

    # Download template
    template_df = pd.DataFrame(columns=["KODE", "DESKRIPSI", "GROUP TRANSAKSI", "SATUAN"])
    
    # Contoh data untuk template
    example_data = {
        "KODE": ["LAB001", "RAD002"],
        "DESKRIPSI": ["HEMATOLOGY TEST", "X-RAY THORAX"],
        "GROUP TRANSAKSI": ["Laboratorium", "Radiologi"],
        "SATUAN": ["TEST", "EXAM"]
    }
    template_df = pd.DataFrame(example_data)
    
    # Informasi tentang kolom tambahan
    st.info("""
    **📝 Template Pemeriksaan Penunjang:**
    - **Kolom Pakem (Wajib):** KODE, DESKRIPSI, GROUP TRANSAKSI, SATUAN
    - **Kolom Tambahan (Opsional):** Anda bisa menambahkan kolom lain di sebelah kanan, contoh: KATEGORI, SUB_KATEGORI, KELAS, dll.
    - **Kolom tambahan akan otomatis terdeteksi dan disimpan.**
    """)
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        template_df.to_excel(writer, index=False, sheet_name="Template Penunjang")
    
    st.download_button(
        label="📥 Download Template Pemeriksaan Penunjang",
        data=output.getvalue(),
        file_name="template_pemeriksaan_penunjang.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )

    # Upload form
    st.markdown("---")
    st.subheader("📤 Upload Data Pemeriksaan Penunjang")
    
    # Input untuk mitra
    mitra = st.text_input("Nama Mitra*", placeholder="Contoh: St. Yusup")
    
    uploaded_file = st.file_uploader(
        "Pilih File Excel Pemeriksaan Penunjang*", 
        type=["xlsx"], 
        help="File harus berisi kolom pakem: KODE, DESKRIPSI, GROUP TRANSAKSI, SATUAN"
    )
    
    if st.button("🚀 Upload File Pemeriksaan Penunjang", use_container_width=True):
        if not uploaded_file or not mitra:
            st.error("❌ Harap pilih file dan isi nama mitra yang akan diupload")
        else:
            penunjang_mgr.upload_excel(uploaded_file, mitra, st.session_state['username'])

def render_data_page_penunjang(penunjang_mgr):
    """Render data display page pemeriksaan penunjang"""
    df = penunjang_mgr.load_data()
    if df.empty:
        st.warning("📭 Belum ada data Pemeriksaan Penunjang.")
        return          

    # untuk mendapatkan daftar kolom tambahan yang tersedia
    available_columns = penunjang_mgr.get_available_columns()

    # Filter dan pencarian
    st.subheader("🔍 Filter Data Pemeriksaan Penunjang")
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        mitra_options = ["Semua"] + sorted(df['mitra'].unique().tolist())
        mitra_filter = st.selectbox("Mitra", mitra_options)
    with col2:
        group_options = ["Semua"] + sorted(df['group_transaksi'].unique().tolist())
        group_filter = st.selectbox("Group Transaksi", group_options)
    with col3:
        satuan_options = ["Semua"] + sorted(df['satuan'].unique().tolist())
        satuan_filter = st.selectbox("Satuan", satuan_options)
    with col4:
        kelas_options = ["Semua"] + available_columns
        kelas_filter = st.selectbox("Pilih Kelas", kelas_options)
    with col5:
        search_query = st.text_input("Cari Deskripsi", placeholder="Cari nama pemeriksaan...")  

    # Apply filters
    filtered_df = df.copy()

    if mitra_filter != "Semua":
        filtered_df = filtered_df[filtered_df['mitra'] == mitra_filter]
    if group_filter != "Semua":
        filtered_df = filtered_df[filtered_df['group_transaksi'] == group_filter]
    if satuan_filter != "Semua":
        filtered_df = filtered_df[filtered_df['satuan'] == satuan_filter]
    if search_query:
        filtered_df = filtered_df[filtered_df['deskripsi'].str.contains(search_query, case=False, na=False)]
    
    # Display results
    st.subheader(f"📋 Data Pemeriksaan Penunjang ({len(filtered_df)} data)")

    if not filtered_df.empty:
        # Siapkan data untuk ditampilkan
        display_data = []

        for _, row in filtered_df.iterrows():
            base_data = {
                'Mitra': row['mitra'],
                'Kode': row['kode'],
                'Deskripsi': row['deskripsi'],
                'Group Transaksi': row['group_transaksi'],
                'Satuan': row['satuan']
            }

            if kelas_filter != "Semua" and row['additional_data']:
                base_data['Kelas'] = row['additional_data'].get(kelas_filter, '')

            display_data.append(base_data)

        display_df = pd.DataFrame(display_data)

        # Reset index untuk nomor urut
        display_df = display_df.reset_index(drop=True)
        display_df.index = display_df.index + 1
        display_df = display_df.rename_axis('No').reset_index()
        
        # Tampilkan dataframe
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        
        # Detail view untuk setiap item
        st.subheader("🔍 Detail Pemeriksaan Penunjang")
        
        if len(filtered_df) == 1:
            selected_item = filtered_df.iloc[0]
        else:
            # Pilih item untuk melihat detail
            item_options = [f"{row['kode']} - {row['deskripsi']}" for _, row in filtered_df.iterrows()]
            selected_item_idx = st.selectbox("Pilih item untuk melihat detail:", range(len(item_options)), format_func=lambda x: item_options[x])
            selected_item = filtered_df.iloc[selected_item_idx]
        
        # Tampilkan detail item yang dipilih
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Data Utama:**")
            st.write(f"**Mitra:** {selected_item['mitra']}")
            st.write(f"**Kode:** {selected_item['kode']}")
            st.write(f"**Deskripsi:** {selected_item['deskripsi']}")
            st.write(f"**Group Transaksi:** {selected_item['group_transaksi']}")
            st.write(f"**Satuan:** {selected_item['satuan']}")
        
        with col2:
            st.write("**Data Tambahan:**")
            additional_data = selected_item.get('additional_data', {})
            if additional_data:
                for key, value in additional_data.items():
                    display_name = penunjang_mgr.get_column_display_name(key)
                    st.write(f"**{display_name}:** {value}")
            else:
                st.write("Tidak ada data tambahan")
        
        # Download button
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:            # Siapkan data untuk download (termasuk semua kolom tambahan)
            download_data = []
            for _, row in filtered_df.iterrows():
                row_data = {
                    'Mitra': row['mitra'],
                    'Kode': row['kode'],
                    'Deskripsi': row['deskripsi'],
                    'Group Transaksi': row['group_transaksi'],
                    'Satuan': row['satuan']
                }
                
                # Tambahkan semua kolom tambahan
                additional_data = row.get('additional_data', {})
                for col in available_columns:
                    row_data[col] = additional_data.get(col, '')
                
                download_data.append(row_data)
            
            download_df = pd.DataFrame(download_data)
            download_df.to_excel(writer, index=False, sheet_name='Data Penunjang')
        
        st.download_button(
            label="📥 Download Data Pemeriksaan Penunjang",
            data=output.getvalue(),
            file_name="Pemeriksaan_Penunjang_Data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    else:
        st.warning("Tidak ada data yang sesuai dengan filter yang dipilih")

def render_user_management_page(user_mgr):
    """Render user management page (admin only)"""
    if st.session_state['role'] != 'admin':
        st.warning("⛔ Hanya admin yang bisa mengakses halaman ini")
        return
    
    with st.form("add_user_form"):
        st.subheader("Tambah User Baru")
        col1, col2 = st.columns(2)
        with col1:
            new_user = st.text_input("Username*", placeholder="Username baru")
            new_pass = st.text_input("Password*", type="password", placeholder="Password")
        with col2:
            role = st.selectbox("Role*", ["user", "admin"])
        
        submit_btn = st.form_submit_button("➕ Tambah User", use_container_width=True)
        
        if submit_btn:
            if not all([new_user, new_pass]):
                st.error("❌ Harap isi semua field yang wajib (*)")
            else:
                user_mgr.add_user(new_user, new_pass, role)

# Render sidebar and get selected page
selected_page = sidebar_mgr.render_sidebar()

# Main content based on selected page
if st.session_state['login']:
    if selected_page == "Upload Data":
        st.title("📤 Upload Data HNA")
        render_upload_page(hna_mgr)
        
    elif selected_page == "Tampilan Data":
        st.title("📊 Data HNA")
        render_data_page(hna_mgr)

    elif selected_page == "Upload Penunjang":
        st.title("🩺 Upload Data Pemeriksaan Penunjang")
        render_upload_page_penunjang(penunjang_mgr)
    
    elif selected_page == "Tampilan Penunjang":
        st.title("📋 Data Pemeriksaan Penunjang")
        render_data_page_penunjang(penunjang_mgr)
        
    elif selected_page == "Manajemen User":
        st.title("👥 Manajemen User")
        render_user_management_page(sidebar_mgr.user_mgr)