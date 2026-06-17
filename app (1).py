import streamlit as st
import pandas as pd
import numpy as np

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="NutriGuard Pro", page_icon="👶", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f7f9fc; }
    .stTabs [data-baseweb="tab"] { font-size: 16px; font-weight: bold; }
    .card {
        background-color: white; padding: 20px; border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("👶 NutriGuard Pro: Dashboard Tumbuh Kembang & Pangan Lokal")
st.markdown("### *Prototype Aplikasi Terintegrasi Eksklusif - SEC SATRIA DATA*")
st.write("---")

# --- 2. SIDEBAR: PROFIL ANAK ---
st.sidebar.header("🪪 Profil Anak")
nama_anak = st.sidebar.text_input("Nama Anak", value="Adek Raihan")
jender = st.sidebar.radio("Jenis Kelamin", ["Laki-laki", "Perempuan"])
usia_input = st.sidebar.number_input("Usia Anak Saat Ini (Bulan)", min_value=0, value=12)
bb_input = st.sidebar.number_input("Berat Badan Anak Saat Ini (kg)", min_value=0.0, value=8.5, step=0.1)
tb_input = st.sidebar.number_input("Tinggi Badan Anak Saat Ini (cm)", min_value=0.0, value=73.0, step=0.1)
diare_input = st.sidebar.selectbox("Riwayat Diare/Sakit Berulang (2 Bulan Terakhir)", ["Tidak", "Ya"])

# --- 3. MEMBUAT TABS UTAMA ---
tab1, tab2 = st.tabs(["📉 Grafik Pertumbuhan & Prediksi", "🥗 Ensiklopedia & Rekomendasi Pangan"])

# --- TAB 1: GRAFIK & PREDIKSI (METODE SEMESTER 2) ---
with tab1:
    st.markdown(f"## 📊 Dashboard Tumbuh Kembang: {nama_anak}")
    
    # KOTAK INFORMASI UTAMA
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Status Usia", value=f"{usia_input} Bulan")
    with col2:
        st.metric(label="Berat Badan", value=f"{bb_input} kg")
    with col3:
        st.metric(label="Tinggi Badan", value=f"{tb_input} cm")
        
    st.write("---")
    
    # MEMBUAT DATA GRAFIK MELENGKUNG (Standar WHO Laki-laki 0-24 Bulan)
    bulan_garis = np.arange(0, 25)
    garis_bawah = 2.5 + (bulan_garis * 0.33)  # Batas bawah stunting (-2 SD)
    garis_median = 3.3 + (bulan_garis * 0.42) # Garis normal (0 SD)
    garis_atas = 4.3 + (bulan_garis * 0.50)   # Batas atas (+2 SD)
    
    # Membuat DataFrame untuk grafik standar WHO
    chart_data = pd.DataFrame({
        'Batas Bawah Stunting (-2 SD)': garis_bawah,
        'Garis Normal WHO': garis_median,
        'Batas Atas (+2 SD)': garis_atas
    }, index=bulan_garis)
    chart_data.index.name = 'Bulan'
    
    # Memasukkan data anak secara dinamis ke dalam kurva standar
    chart_data[f'Posisi {nama_anak}'] = np.nan
    if len(chart_data) > usia_input:
        chart_data.loc[usia_input, f'Posisi {nama_anak}'] = bb_input
        
    st.subheader("📈 Kurva Pertumbuhan Berat Badan Menurut Usia (Standar WHO)")
    st.write("Garis melengkung menunjukkan standar internasional. Titik kuning/oranye adalah posisi anak Anda saat ini.")
    
    # Menampilkan grafik gabungan
    st.line_chart(chart_data, color=["#FF4B4B", "#00F4B4", "#4B8BFF", "#FFaa00"])
    
    st.write("---")
    
    # HITUNG RISIKO LOGISTIK REGRESI
    st.subheader("🔮 Hasil Analisis Prediksi Risiko 3 Bulan Kedepan")
    diare_val = 1 if diare_input == "Ya" else 0
    
    # Rumus Logistik Regresi Akademis Semester 2
    intercept = -0.5 
    coef_usia = 0.04
    coef_bb = -0.35  
    coef_diare = 1.2  
    
    z = intercept + (coef_usia * usia_input) + (coef_bb * bb_input) + (coef_diare * diare_val)
    probabilitas = 1 / (1 + np.exp(-z))
    
    st.write(f"**Probabilitas Kecenderungan Stunting:** {probabilitas * 100:.1f}%")
    
    if probabilitas >= 0.5:
        st.error(f"⚠️ **Peringatan untuk {nama_anak}:** Model mendeteksi adanya risiko 'Growth Faltering' (gagal tumbuh) dalam 3 bulan ke depan. Segera intervensi dengan pangan lokal kaya protein mikro di Tab sebelah!")
    else:
        st.success(f"✅ **Kondisi {nama_anak} Aman:** Risiko stunting dalam 3 bulan ke depan terpantau rendah. Pertahankan pola makan aktifnya!")
        
    # Tombol Cetak / Ekspor Laporan Hasil untuk Kader Posyandu
    laporan = f"LAPORAN KESEHATAN BALITA\nNama Anak: {nama_anak}\nUsia: {usia_input} Bulan\nBerat Badan: {bb_input} kg\nProbabilitas Risiko Stunting: {probabilitas * 100:.1f}%\n"
    st.download_button(label="📥 Unduh Laporan Hasil Analisis (TXT)", data=laporan, file_name=f"laporan_{nama_anak}.txt")

# --- TAB 2: REKOMENDASI PANGAN LOKAL LENGKAP DENGAN GAMBAR & GIZI ---
with tab2:
    st.markdown("## 🥗 Peta Pangan Lokal & Kandungan Gizi Terintegrasi")
    st.write("Rekomendasi bahan makanan padat gizi yang murah, mudah didapat, dan disesuaikan dengan wilayah tempat tinggal Anda.")
    
    daerah = st.selectbox("Pilih Wilayah Tempat Tinggal Anda saat ini:", [
        "Wilayah Pesisir / Pantai",
        "Wilayah Pegunungan / Daratan"
    ])
    
    st.write("---")
    
    # DATABASE PANGAN LOKAL
    pangan_db = {
        "Wilayah Pesisir / Pantai": [
            {
                "nama": "Ikan Kembung",
                "gambar": "https://images.unsplash.com/photo-1534604973900-c43ab4c2e0ab?w=400",
                "kalori": "112 kkal", "protein": "21.4 g", "zat_besi": "0.9 mg", "seng": "0.8 mg",
                "ket": "Kandungan Omega-3 nya bahkan lebih tinggi daripada ikan Salmon impor. Sangat murah di pasar ikan lokal."
            },
            {
                "nama": "Kerang Hijau",
                "gambar": "https://images.unsplash.com/photo-1599487488170-d11ec9c172f0?w=400",
                "kalori": "86 kkal", "protein": "12.0 g", "zat_besi": "6.7 mg", "seng": "1.5 mg",
                "ket": "Sangat tinggi zat besi untuk mencegah anemia pada balita, yang menjadi salah satu pemicu utama stunting."
            },
            {
                "nama": "Daun Kelor (Moringa)",
                "gambar": "https://images.unsplash.com/photo-1515252621455-d4e837b92641?w=400",
                "kalori": "64 kkal", "protein": "9.4 g", "zat_besi": "7.0 mg", "seng": "0.6 mg",
                "ket": "Disebut 'Superfood' oleh WHO karena kandungan mikronutriennya yang luar biasa. Bisa ditanam gratis di pekarangan rumah."
            }
        ],
        "Wilayah Pegunungan / Daratan": [
            {
                "nama": "Telur Puyuh (per 100g)",
                "gambar": "https://images.unsplash.com/photo-1554110360-1598463870b2?w=400",
                "kalori": "158 kkal", "protein": "13.1 g", "zat_besi": "3.7 mg", "seng": "1.5 mg",
                "ket": "Ukurannya kecil sehingga disukai anak-anak. Mengandung Kolin yang sangat baik untuk perkembangan otak balita."
            },
            {
                "nama": "Hati Ayam",
                "gambar": "https://images.unsplash.com/photo-1606851264030-909ba9a04225?w=400",
                "kalori": "116 kkal", "protein": "16.9 g", "zat_besi": "15.8 mg", "seng": "3.2 mg",
                "ket": "Juara zat besi hewani. Harganya sangat ekonomis namun efektivitasnya dalam mengejar ketertinggalan gizi anak sangat tinggi."
            },
            {
                "nama": "Tempe Kedelai / Koro",
                "gambar": "https://images.unsplash.com/photo-1622484211148-7162982af0b9?w=400",
                "kalori": "201 kkal", "protein": "20.8 g", "zat_besi": "4.0 mg", "seng": "1.8 mg",
                "ket": "Protein nabati terbaik asli Indonesia yang mudah diserap pencernaan balita karena hasil proses fermentasi."
            }
        ]
    }
    
    makanan_pilihan = pangan_db[daerah]
    
    for makanan in makanan_pilihan:
        col_img, col_desc = st.columns([1, 2])
        with col_img:
            st.image(makanan["gambar"], caption=makanan["nama"], use_container_width=True)
        with col_desc:
            st.subheader(makanan["nama"])
            st.write(f"ℹ️ *{makanan['ket']}*")
            
            gizi_df = pd.DataFrame({
                "Zat Gizi": ["Energi/Kalori", "Protein", "Zat Besi", "Seng (Zinc)"],
                "Kandungan (per 100g)": [makanan["kalori"], makanan["protein"], makanan["zat_besi"], makanan["seng"]]
            })
            st.dataframe(gizi_df, hide_index=True)
        st.write("---")
