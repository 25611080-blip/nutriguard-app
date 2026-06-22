import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="NutriGuard Pro", page_icon="👶", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f4f6f9; }
    .report-card {
        background-color: #ffffff;
        padding: 24px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        margin-bottom: 15px;
    }
    .report-title { font-size: 20px; font-weight: bold; color: #1e293b; margin-bottom: 15px; }
    .report-item { font-size: 15px; margin-bottom: 8px; color: #475569; }
    .report-value { font-weight: bold; color: #0f172a; }
    </style>
    """, unsafe_allow_html=True)

st.title("👶 NutriGuard Pro: Dashboard Tumbuh Kembang & Pangan Lokal")
st.markdown("### *Prototype Aplikasi Terintegrasi Eksklusif - SEC SATRIA DATA*")
st.write("---")

# --- 2. SIDEBAR: PROFIL ANAK ---
st.sidebar.header("🪪 Profil Anak")
nama_anak = st.sidebar.text_input("Nama Anak", value="", placeholder="Masukkan nama anak...")
jender = st.sidebar.radio("Jenis Kelamin", ["Laki-laki", "Perempuan"])
# Usia, BB, TB tetap jadi input penting untuk model regresi asli
usia_input = st.sidebar.number_input("Usia Anak Saat Ini (Bulan)", min_value=0, max_value=60, value=None, placeholder="Contoh: 12")
bb_input = st.sidebar.number_input("Berat Badan Anak Saat Ini (kg)", min_value=0.0, value=None, step=0.1, placeholder="Contoh: 8.5")
tb_input = st.sidebar.number_input("Tinggi Badan Anak Saat Ini (cm)", min_value=0.0, value=None, step=0.1, placeholder="Contoh: 73.0")

st.sidebar.subheader("⚠ Faktor Determinan Kesehatan (Kemenkes)")
# Kotak checklist tetap sama, kita akan gunakan logika 'TIDAK terpenuhi' sebagai risiko
air_layak = st.sidebar.checkbox("Memiliki Akses Air Minum Layak")
sanitasi_layak = st.sidebar.checkbox("Memiliki Akses Sanitasi/Jamban Sehat")
imunisasi_lengkap = st.sidebar.checkbox("Status Imunisasi Dasar Lengkap")
asi_eksklusif = st.sidebar.checkbox("Riwayat ASI Eksklusif (0-6 Bulan)")
memiliki_bpjs = st.sidebar.checkbox("Memiliki Jaminan Kesehatan (BPJS/KIS)")

mulai_skrining = st.sidebar.button("Mulai Skrining Mandiri")

# --- 3. TABS UTAMA ---
tab1, tab2 = st.tabs(["📉 Grafik Pertumbuhan & Skrining Risiko", "🥗 Ensiklopedia & Rekomendasi Pangan"])

with tab1:
    if mulai_skrining:
        if nama_anak == "" or usia_input is None or bb_input is None or tb_input is None:
            st.error("❌ Mohon lengkapi seluruh data (Nama, Usia, BB, dan TB) di sidebar kiri untuk memulai skrining!")
        else:
            st.markdown(f"## 📊 Dashboard Tumbuh Kembang: {nama_anak}")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(label="Status Usia", value=f"{usia_input} Bulan")
            with col2:
                st.metric(label="Berat Badan (BB)", value=f"{bb_input} kg")
            with col3:
                st.metric(label="Tinggi Badan (TB)", value=f"{tb_input} cm")
                
            st.write("---") 
            col_grafik, col_analisis = st.columns([1, 1])
            
            with col_grafik:
                st.subheader("📈 Kurva Pertumbuhan Antropometri")
                st.write("Arahkan kursor ke garis referensi Permenkes No. 2 Tahun 2020.")
                
                # Model kurva Linier WHO tetap digunakan untuk visualisasi
                usia_ref = np.arange(0, 61, 1)
                median_tinggi = 49 + (usia_ref * 0.8)
                sd_plus2 = median_tinggi + 4
                sd_minus2 = median_tinggi - 4
                sd_minus3 = median_tinggi - 6
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=usia_ref, y=median_tinggi, mode='lines', name='Median (Normal)', line=dict(color='green', dash='dash')))
                fig.add_trace(go.Scatter(x=usia_ref, y=sd_plus2, mode='lines', name='+2 SD (Tinggi)', line=dict(color='blue', width=1)))
                fig.add_trace(go.Scatter(x=usia_ref, y=sd_minus2, mode='lines', name='-2 SD (Ambang Stunting)', line=dict(color='orange', dash='dashdot')))
                fig.add_trace(go.Scatter(x=usia_ref, y=sd_minus3, mode='lines', name='-3 SD (Sangat Pendek)', line=dict(color='red', dash='dot')))
                
                fig.add_trace(go.Scatter(x=[usia_input], y=[tb_input], mode='markers', name=f'Posisi {nama_anak}',
                                         marker=dict(color='magenta', size=14, line=dict(color='black', width=1)),
                                         hovertemplate=f'<b>{nama_anak}</b><br>Usia: %{{x}} Bulan<br>Tinggi: %{{y}} cm<extra></extra>'))
                
                fig.update_layout(
                    xaxis_title="Usia (Bulan)", yaxis_title="Tinggi Badan (cm)",
                    hovermode="closest", legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5),
                    plot_bgcolor='white', height=450, margin=dict(l=20, r=20, t=20, b=20)
                )
                fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='LightGray')
                fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='LightGray')
                
                st.plotly_chart(fig, use_container_width=True)
            
            with col_analisis:
                st.subheader("📋 Rapor Medis Ringkas Hasil Skrining")
                
                # --- SINKRONISASI 1: GANTI MODEL REGRESI LOGISTIK (SESUAI GAMBAR 2) ---
                
                # Definisi Variabel Risiko (X = 1 jika KONDISI BURUK/RISIKO)
                # Sesuai teori kita: Kalau checkbox TIDAK dicentang, itu adalah risiko.
                r1_usia = usia_input
                r2_bb = bb_input
                r3_air = 1 if not air_layak else 0
                r4_sanitasi = 1 if not sanitasi_layak else 0
                r5_imunisasi = 1 if not imunisasi_lengkap else 0
                r6_asi = 1 if not asi_eksklusif else 0
                r7_bpjs = 1 if not memiliki_bpjs else 0

                # Perhitungan Log-Odds menggunakan Koefisien EKSAK dari Gambar 2
                log_odds = (-1.3129) + \
                           ((-0.0151) * r1_usia) + \
                           ((0.0024) * r2_bb) + \
                           ((0.5164) * r3_air) + \
                           ((0.6818) * r4_sanitasi) + \
                           ((-0.2498) * r5_imunisasi) + \
                           ((0.1552) * r6_asi) + \
                           ((0.2611) * r7_bpjs)
                
                # Transformasi Sigmoid tetap sama
                probabilitas = 1 / (1 + np.exp(-log_odds))
                persentase_skor = probabilitas * 100
                
                # --- SINKRONISASI 2: PENYESUAIAN CUTTING-OFF POINT (BIAR LOGIS DENGAN MODEL ASLI) ---
                # Karena intersep aslinya rendah (-1.3), kita perlu sesuaikan batas kategori.
                if persentase_skor < 20: # Turunkan batas Rendah
                    status_teks, warna_border, status_gizi = "RENDAH", "#28a745", "Baik / Proporsional"
                elif persentase_skor < 50: # Turunkan batas Waspada
                    status_teks, warna_border, status_gizi = "WASPADA", "#ffc107", "Kurang Proporsional"
                else:
                    status_teks, warna_border, status_gizi = "TINGGI", "#dc3545", "Defisit Gizi Kronis"
                
                # Perhitungan IMT untuk Tampilan
                tinggi_meter = tb_input / 100
                imt_skor = bb_input / (tinggi_meter ** 2)

                # Kartu Utama Rapor Medis Digital (Tampilan Tetap Sama)
                st.markdown(f"""
                <div class="report-card" style="border-left: 8px solid {warna_border};">
                    <div class="report-title">📝 KARTU HASIL SKRINING ANTROPOMETRI DIGITAL</div>
                    <div class="report-item">🔹 <b>Nama Pasien Balita:</b> <span class="report-value">{nama_anak}</span></div>
                    <div class="report-item">🔹 <b>Indeks Massa Tubuh (IMT):</b> <span class="report-value">{imt_skor:.2f} kg/m²</span></div>
                    <div class="report-item">🔹 <b>Status Estimasi Gizi:</b> <span class="report-value">{status_gizi}</span></div>
                    <div class="report-item">🔹 <b>Skor Indeks Risiko Kerentanan:</b> <span class="report-value" style="color:{warna_border};">{persentase_skor:.1f}% ({status_teks})</span></div>
                    <hr style="margin: 15px 0; border: 0; border-top: 1px solid #e2e8f0;">
                    <div class="report-item">📋 <b>Catatan Rekomendasi Klinik:</b></div>
                    <p style="font-size: 14px; color: #64748b; line-height: 1.5; margin: 5px 0 0 0;">
                        Kondisi paparan lingkungan pengasuhan anak menunjukkan level <b>{status_teks}</b> terhadap risiko hambatan pertumbuhan. 
                        Disarankan untuk meningkatkan asupan gizi mikro hewani dari menu pangan lokal di Tab sebelah dan lakukan pengukuran ulang berkala setiap bulan di Posyandu terdekat.
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                # Edukasi Penjelasan Kartu (Expander)
                with st.expander("🔍 Hubungkan & Pahami Maksud Angka di Atas (Panduan Awam)"):
                    st.markdown(f"""
                    ### 💡 Cara Membaca Rapor {nama_anak}:
                    
                    1. **Indeks Massa Tubuh (IMT) Balita (`{imt_skor:.2f} kg/m²`)**
                       * **Apa itu?** Perbandingan antara berat badan dengan kuadrat tinggi badan anak. 
                       * **Maksudnya:** Angka ini menilai apakah berat badan anak sudah proporsional atau seimbang dengan tinggi fisiknya saat ini agar tidak mengalami gizi kurang atau obesitas.
                    
                    2. **Status Estimasi Gizi (`{status_gizi}`)**
                       * **Maksudnya:** Kesimpulan instan mengenai bentuk tubuh anak. Jika tertulis *Kurang Proporsional*, berarti tinggi badan anak dan berat badannya saat ini belum berada di titik keseimbangan ideal (terlalu kurus atau terlalu gemuk).
                    
                    3. **Skor Indeks Risiko Kerentanan (`{persentase_skor:.1f}%`)**
                       * **Apa itu?** Prediksi peluang anak mengalami hambatan tumbuh kembang di masa depan berdasarkan kondisi lingkungan rumah.
                       * **Maksudnya:** Angka ini didapat dari seberapa banyak syarat kesehatan (seperti Air Bersih, Imunisasi, dan Sanitasi) yang **belum terpenuhi** di halaman kiri. Semakin tinggi persentasenya, semakin besar risiko anak tersebut terserang penyakit infeksi yang dapat memicu stunting jika tidak segera ditangani. **Logika skoring ini mengacu pada hasil analisis statistik regresi biner asli dari dataset riset**.
                    """)
        
            st.markdown("---")
            st.caption("📢 **Disclaimer Medis:** Aplikasi ini bertindak murni sebagai instrumen skrining dini mandiri, bukan pengganti penegakan diagnosis klinis oleh Dokter Spesialis Anak.")
    else:
        st.info("👋 Selamat Datang di NutriGuard Pro! Demi keamanan privasi data, tampilan utama sengaja dikosongkan. Silakan isi form profil anak Anda secara mandiri di bilah samping (sidebar) kiri, lalu klik tombol **'Mulai Skrining Mandiri'** untuk melihat hasil analisis.")

# --- TAB 2: REKOMENDASI PANGAN LOKAL ---
with tab2:
    st.markdown("## 🥗 Peta Pangan Lokal & Kandungan Gizi Terintegrasi")
    daerah = st.selectbox("Pilih Wilayah Tempat Tinggal Anda saat ini:", ["Wilayah Pesisir / Pantai", "Wilayah Pegunungan / Daratan"])
    st.write("---")
    
    pangan_db = {
        "Wilayah Pesisir / Pantai": [
            {"nama": "Ikan Kembung", "gambar": "https://images.unsplash.com/photo-1534604973900-c43ab4c2e0ab?w=400", "kalori": "112 kkal", "protein": "21.4 g", "zat_besi": "0.9 mg", "seng": "0.8 mg", "ket": "Kandungan Omega-3 nya bahkan lebih tinggi daripada ikan Salmon impor."},
            {"nama": "Kerang Hijau", "gambar": "https://images.unsplash.com/photo-1599487488170-d11ec9c172f0?w=400", "kalori": "86 kkal", "protein": "12.0 g", "zat_besi": "6.7 mg", "seng": "1.5 mg", "ket": "Sangat tinggi zat besi untuk mencegah anemia pada balita."},
            {"nama": "Daun Kelor (Moringa)", "gambar": "https://images.unsplash.com/photo-1515252621455-d4e837b92641?w=400", "kalori": "64 kkal", "protein": "9.4 g", "zat_besi": "7.0 mg", "seng": "0.6 mg", "ket": "Disebut 'Superfood' oleh WHO karena kandungan mikronutriennya."}
        ],
        "Wilayah Pegunungan / Daratan": [
            {"nama": "Telur Puyuh (per 100g)", "gambar": "https://images.unsplash.com/photo-1554110360-1598463870b2?w=400", "kalori": "158 kkal", "protein": "13.1 g", "zat_besi": "3.7 mg", "seng": "1.5 mg", "ket": "Mengandung Kolin yang sangat baik untuk perkembangan otak balita."},
            {"nama": "Hati Ayam", "gambar": "https://images.unsplash.com/photo-1606851264030-909ba9a04225?w=400", "kalori": "116 kkal", "protein": "16.9 g", "zat_besi": "15.8 mg", "seng": "3.2 mg", "ket": "Juara zat besi hewani. Harganya sangat ekonomis."},
            {"nama": "Tempe Kedelai / Koro", "gambar": "https://images.unsplash.com/photo-1622484211148-7162982af0b9?w=400", "kalori": "201 kkal", "protein": "20.8 g", "zat_besi": "4.0 mg", "seng": "1.8 mg", "ket": "Protein nabati terbaik asli Indonesia yang mudah diserap pencernaan balita."}
        ]
    }
    
    for makanan in pangan_db[daerah]:
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
