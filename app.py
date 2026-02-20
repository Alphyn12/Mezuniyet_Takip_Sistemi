# -*- coding: utf-8 -*-
"""
Trakya Üniversitesi Makina Mühendisliği Bölümü
Mezuniyet Takip Sistemi
===============================================
Ana Streamlit uygulaması.

Kullanım:
    streamlit run app.py
"""

import os
import streamlit as st
import pandas as pd

from pdf_parser import parse_transcript
from matcher import match_courses, generate_summary
from report import generate_report

# ===== SAYFA YAPILANDIRMASI =====
st.set_page_config(
    page_title="Mezuniyet Takip Sistemi",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===== ÖZEL CSS STİLLERİ =====
st.markdown("""
<style>
    /* Genel font ve tema */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* Ayarlar menüsünü ve varsayılan başlık barını gizle (Sadece koyu tema için) */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}

    .main .block-container {
        padding-top: 2rem;
        max-width: 1400px;
    }

    /* Başlık stili */
    .main-title {
        text-align: center;
        background: linear-gradient(135deg, #1e3a5f 0%, #2c5f8a 50%, #3a7fc1 100%);
        color: white;
        padding: 1.5rem 2rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 20px rgba(30, 58, 95, 0.3);
    }
    .main-title h1 { margin: 0; font-size: 2.2rem; font-weight: 700; color: white !important; }
    .main-title p { margin: 0.3rem 0 0 0; font-size: 0.95rem; opacity: 0.9; color: #e0e0e0 !important; }

    /* Özet kartları - Koyu tema uyumlu */
    .metric-card {
        background: rgba(30, 58, 95, 0.4);
        border: 1px solid rgba(100, 160, 220, 0.3);
        border-radius: 10px;
        padding: 1rem 1.2rem;
        text-align: center;
        box-shadow: 0 2px 12px rgba(0,0,0,0.2);
        transition: transform 0.2s;
        backdrop-filter: blur(4px);
    }
    .metric-card:hover { transform: translateY(-2px); box-shadow: 0 4px 16px rgba(0,0,0,0.3); }
    .metric-card .value {
        font-size: 1.8rem;
        font-weight: 700;
        margin: 0;
    }
    .metric-card .label {
        font-size: 0.8rem;
        color: #b0bec5 !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin: 0;
    }

    /* Başarılı ders satırı - Koyu tema */
    .course-success {
        background: rgba(40, 167, 69, 0.15);
        border-left: 4px solid #4caf50;
        padding: 0.5rem 0.8rem;
        margin: 0.2rem 0;
        border-radius: 0 6px 6px 0;
        font-size: 0.85rem;
        color: #c8e6c9 !important;
    }
    .course-success strong, .course-success span, .course-success em { color: #a5d6a7 !important; }

    /* Başarısız ders satırı - Koyu tema */
    .course-fail {
        background: rgba(220, 53, 69, 0.2);
        border-left: 4px solid #f44336;
        padding: 0.5rem 0.8rem;
        margin: 0.2rem 0;
        border-radius: 0 6px 6px 0;
        font-size: 0.85rem;
        color: #ffcdd2 !important;
    }
    .course-fail strong, .course-fail span, .course-fail em { color: #ef9a9a !important; }

    /* Eksik ders satırı - Koyu tema */
    .course-missing {
        background: rgba(255, 193, 7, 0.15);
        border-left: 4px solid #ffb300;
        padding: 0.5rem 0.8rem;
        margin: 0.2rem 0;
        border-radius: 0 6px 6px 0;
        font-size: 0.85rem;
        color: #fff8e1 !important;
    }
    .course-missing strong, .course-missing span, .course-missing em { color: #ffe082 !important; }

    /* Şüpheli eşleşme - Koyu tema */
    .course-suspect {
        background: rgba(255, 152, 0, 0.15);
        border-left: 4px solid #ff9800;
        padding: 0.5rem 0.8rem;
        margin: 0.2rem 0;
        border-radius: 0 6px 6px 0;
        font-size: 0.85rem;
        color: #ffe0b2 !important;
    }
    .course-suspect strong, .course-suspect span, .course-suspect em { color: #ffcc80 !important; }

    /* Devam eden ders - Koyu tema */
    .course-ongoing {
        background: rgba(33, 150, 243, 0.15);
        border-left: 4px solid #42a5f5;
        padding: 0.5rem 0.8rem;
        margin: 0.2rem 0;
        border-radius: 0 6px 6px 0;
        font-size: 0.85rem;
        color: #bbdefb !important;
    }
    .course-ongoing strong, .course-ongoing span, .course-ongoing em { color: #90caf9 !important; }

    /* Dönem başlığı */
    .semester-header {
        background: linear-gradient(90deg, #1e3a5f, #2c5f8a);
        color: white !important;
        padding: 0.6rem 1rem;
        border-radius: 8px;
        margin: 1rem 0 0.5rem 0;
        font-weight: 600;
        font-size: 0.95rem;
    }

    /* Sidebar stili */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e3a5f 0%, #15293e 100%);
    }
    section[data-testid="stSidebar"] .stMarkdown h1,
    section[data-testid="stSidebar"] .stMarkdown h2,
    section[data-testid="stSidebar"] .stMarkdown h3,
    section[data-testid="stSidebar"] .stMarkdown p,
    section[data-testid="stSidebar"] .stMarkdown label {
        color: white !important;
    }

    /* İndirme butonu */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #28a745, #218838) !important;
        color: white !important;
        border: none !important;
        padding: 0.7rem 2rem !important;
        font-size: 1rem !important;
        border-radius: 8px !important;
        width: 100% !important;
        transition: all 0.3s !important;
    }
    .stDownloadButton > button:hover {
        background: linear-gradient(135deg, #218838, #1e7e34) !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(40, 167, 69, 0.4) !important;
    }

    /* ===== YAZDIRILABİLİR (PRINT-FRIENDLY) CSS ===== */
    @media print {
        section[data-testid="stSidebar"],
        .stButton, .stDownloadButton,
        header[data-testid="stHeader"] {
            display: none !important;
        }
        .main .block-container {
            max-width: 100% !important;
            padding: 0 !important;
            margin: 0 !important;
        }
        body {
            background-color: white !important;
            color: black !important;
        }
        .metric-card, .semester-header, 
        .course-success, .course-fail, .course-missing, .course-suspect, .course-ongoing {
            break-inside: avoid;
            box-shadow: none !important;
        }
        .course-success strong, .course-success span, .course-success em,
        .course-fail strong, .course-fail span, .course-fail em,
        .course-missing strong, .course-missing span, .course-missing em,
        .course-suspect strong, .course-suspect span, .course-suspect em,
        .course-ongoing strong, .course-ongoing span, .course-ongoing em {
            color: black !important;
        }
        .metric-card p {
            color: black !important;
        }
    }

    /* ===== MOBİL CİHAZ UYARLAMASI CSS ===== */
    @media (max-width: 768px) {
        .main .block-container {
            padding-top: 1rem;
            padding-left: 1rem;
            padding-right: 1rem;
        }
        .main-title h1 {
            font-size: 1.5rem !important;
        }
        .metric-card {
            margin-bottom: 0.8rem;
        }
        .semester-header {
            font-size: 1rem;
            text-align: center;
        }
        .course-success, .course-fail, .course-missing, .course-suspect, .course-ongoing {
            font-size: 0.9rem;
            padding: 0.8rem;
            margin: 0.5rem 0;
            border-radius: 6px;
        }
        /* DataFrameler için yatay scroll */
        .stDataFrame, div[data-testid="stDataFrame"] {
            overflow-x: auto;
        }
    }
</style>
""", unsafe_allow_html=True)


# ===== YARDIMCI FONKSİYONLAR =====

@st.cache_data
def load_mufredat(filepath: str) -> pd.DataFrame:
    """Müfredat Excel dosyasını yükler ve önbelleğe alır."""
    return pd.read_excel(filepath)


def get_donem_adi(donem_no: int) -> str:
    """Dönem numarasından dönem adı üretir."""
    yil = (donem_no + 1) // 2
    tip = "Güz" if donem_no % 2 == 1 else "Bahar"
    return f"{yil}. Yıl - {tip} ({donem_no}. Yarıyıl)"


def get_css_class(durum: str) -> str:
    """Ders durumuna göre CSS sınıfı döndürür."""
    mapping = {
        'Başarılı': 'course-success',
        'Başarısız': 'course-fail',
        'Eksik': 'course-missing',
        'Şüpheli Eşleşme': 'course-suspect',
        'Devam Ediyor': 'course-ongoing',
    }
    return mapping.get(durum, 'course-missing')

def show_footer():
    """Tüm sayfalarda ortaktır: Geliştirici bilgisini daha belirgin gösterir."""
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; padding: 1.5rem 0 1rem 0;">
        <p style="font-size: 1.05rem; font-weight: 700; color: #90caf9; margin: 0;">Geliştiren: Barış KIRLI</p>
        <p style="font-size: 0.9rem; color: #b0bec5; margin: 0.3rem 0 0 0;">Trakya Üniversitesi Makine Mühendisliği Bölümü Öğrencisi</p>
    </div>
    """, unsafe_allow_html=True)


# ===== ANA UYGULAMA =====

def main():
    """Ana Streamlit uygulama döngüsü."""

    # ===== BAŞLIK =====
    st.markdown("""
    <div class="main-title">
        <h1>🎓 Trakya Üniversitesi Mezuniyet Takip Sistemi</h1>
        <p>Makina Mühendisliği Bölümü • Transkript Kontrol ve Analiz Platformu</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="background-color: rgba(30, 58, 95, 0.4); padding: 1.2rem; border-radius: 10px; border-left: 4px solid #3a7fc1; margin-bottom: 1.5rem; text-align: justify; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
        <p style="color: white !important; font-size: 1.15rem; line-height: 1.6; margin: 0; font-weight: 400;">
            ℹ️ Bu sistem, öğrencilerin Trakya Üniversitesi Öğrenci Bilgi Sistemi'nden (OBS) aldıkları transkript PDF dosyalarını okuyarak, seçilen yıla ait müfredat ile karşılaştırılmasını ve öğrencinin mezuniyet koşullarını (AKTS, kümülatif not, zorunlu/seçmeli ders eşleşmeleri, yabancı dil oranı vb.) sağlayıp sağlamadığını analiz etmeyi amaçlamaktadır.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ===== SIDEBAR =====
    with st.sidebar:
        st.markdown("## 📋 Ayarlar")
        st.markdown("---")

        # Müfredat seçimi
        st.markdown("### 📚 Müfredat Seçimi")
        mufredat_options = {
            "2018-2019 Müfredatı": "mufredatlar/mufredat_2018.xlsx",
            "2022-2023 Müfredatı": "mufredatlar/mufredat_2022.xlsx",
            "2024-2025 Müfredatı": "mufredatlar/mufredat_2024.xlsx",
            "2025-2026 Müfredatı": "mufredatlar/mufredat_2025.xlsx",
        }

        selected_mufredat = st.selectbox(
            "Müfredat yılını seçin:",
            options=list(mufredat_options.keys()),
            index=1,  # Varsayılan: 2022
            help="Öğrencinin kayıtlı olduğu müfredat yılını seçin."
        )

        st.markdown("---")

        # PDF yükleme
        st.markdown("### 📄 Transkript Yükleme")
        uploaded_file = st.file_uploader(
            "Transkript PDF dosyanızı yükleyin",
            type=['pdf'],
            help="Trakya Üniversitesi OBS'den aldığınız öğrenci not belgesini (transkript) yükleyin."
        )
        st.markdown("---")

        # Eşleşme eşiği ayarı
        st.markdown("### ⚙️ Gelişmiş Ayarlar")
        threshold = st.slider(
            "Bulanık eşleşme eşiği",
            min_value=50,
            max_value=100,
            value=80,
            step=5,
            help="Eşleşme skoru bu değerin üzerindeyse ders eşleşmiş sayılır.",
        )

        st.markdown("---")

    # ===== ANA İÇERİK =====
    mufredat_path = mufredat_options[selected_mufredat]

    # Müfredat dosyası kontrolü
    if not os.path.exists(mufredat_path):
        st.error(f"⚠️ Müfredat dosyası bulunamadı: `{mufredat_path}`")
        return

    mufredat_df = load_mufredat(mufredat_path)

    # Dosya yüklenmemişse bilgi göster
    if uploaded_file is None:
        st.info("👈 Lütfen sol panelden transkript PDF dosyanızı yükleyin.")

        # Müfredat önizlemesi
        st.markdown("### 📚 Seçili Müfredat Önizlemesi")
        st.markdown(f"**{selected_mufredat}** - Toplam {len(mufredat_df)} ders")

        for donem_no in sorted(mufredat_df['Donem'].unique()):
            donem_dersleri = mufredat_df[mufredat_df['Donem'] == donem_no]
            with st.expander(f"📖 {get_donem_adi(donem_no)}", expanded=False):
                display_df = donem_dersleri[['Ders_Kodu', 'Ders_Adi', 'AKTS', 'Tur']].reset_index(drop=True)
                display_df.index = display_df.index + 1
                st.dataframe(display_df, use_container_width=True, hide_index=False)
                toplam_akts = donem_dersleri['AKTS'].sum()
                st.caption(f"Dönem Toplam AKTS: **{int(toplam_akts)}**")

        show_footer()
        return

    # ===== TRANSKRİPT İŞLEME =====
    with st.spinner("📊 Transkript analiz ediliyor..."):
        transkript_df, parsed_agno = parse_transcript(uploaded_file)

    if transkript_df.empty:
        st.error("❌ Transkriptten ders verisi çıkarılamadı. Lütfen PDF formatını kontrol edin.")
        return

    # ===== EŞLEŞTİRME =====
    with st.spinner("🔍 Dersler eşleştiriliyor..."):
        results = match_courses(mufredat_df, transkript_df)
        summary = generate_summary(results, transkript_df, parsed_agno)

    # ===== ÖZET KARTLARI =====
    st.markdown("### 📊 Genel Durum")
    cols = st.columns(5)

    metric_data = [
        ("🎯 Başarılı AKTS", f"{int(summary['basarili_akts'])} / {int(summary['toplam_mufredat_akts'])}", "#28a745"),
        ("📈 AGNO", f"{summary['agno']}", "#007bff"),
        ("✅ Başarılı", f"{summary['basarili_ders_sayisi']}", "#28a745"),
        ("❌ Eksik/Başarısız", f"{summary['eksik_ders_sayisi'] + summary['basarisiz_ders_sayisi']}", "#dc3545"),
        ("🔵 Devam Eden", f"{summary['devam_eden_sayisi']}", "#2196f3"),
    ]

    for col, (label, value, color) in zip(cols, metric_data):
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <p class="value" style="color: {color};">{value}</p>
                <p class="label">{label}</p>
            </div>
            """, unsafe_allow_html=True)

    # Mezuniyet durumu banner
    st.markdown("")
    if "Sağlanıyor" in summary['mezuniyet_durumu']:
        st.success(f"**{summary['mezuniyet_durumu']}**")
    elif "Devam" in summary['mezuniyet_durumu']:
        st.info(f"**{summary['mezuniyet_durumu']}**")
    else:
        st.error(f"**{summary['mezuniyet_durumu']}**")

    # ===== İNGİLİZCE DERS ORANI =====
    ing_oran = summary['ingilizce_oran']
    ing_toplam = summary['ingilizce_toplam_akts']
    ing_basarili = summary['ingilizce_basarili_akts']
    ing_devam = summary['ingilizce_devam_akts']
    ing_yeterli = summary['ingilizce_yeterli']
    toplam_aktif = int(summary['basarili_akts']) + sum(
        int(r['Mufredat_AKTS']) for r in results if r['Durum'] == 'Devam Ediyor'
    )
    gereken_akts = int(toplam_aktif * 0.30)
    eksik_akts = max(0, gereken_akts - int(ing_toplam))

    st.markdown('### <img src="https://flagcdn.com/w40/gb.png" width="28" style="vertical-align: middle; margin-bottom: 4px; border-radius: 3px; box-shadow: 0 1px 3px rgba(0,0,0,0.3);"> İngilizce Ders Oranı', unsafe_allow_html=True)
    progress_val = min(ing_oran / 30, 1.0)  # %30'a göre normalize

    devam_notu = f" (Başarılı: {int(ing_basarili)} + Devam Eden: {int(ing_devam)})" if ing_devam > 0 else ""

    if ing_yeterli:
        st.markdown(f"""
        <div style="background: rgba(40,167,69,0.15); border-left: 4px solid #4caf50; padding: 0.8rem 1rem; border-radius: 0 8px 8px 0; margin-bottom: 0.5rem;">
            <span style="color: #a5d6a7; font-weight: 600; font-size: 1rem;">✅ Mevcut İngilizce Oranı: %{ing_oran}</span>
            <span style="color: #81c784; font-size: 0.85rem;"> &nbsp;•&nbsp; İngilizce AKTS: {int(ing_toplam)} / {toplam_aktif}{devam_notu} &nbsp;•&nbsp; Mezuniyet için yeterli (≥ %30)</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style="background: rgba(220,53,69,0.15); border-left: 4px solid #f44336; padding: 0.8rem 1rem; border-radius: 0 8px 8px 0; margin-bottom: 0.5rem;">
            <span style="color: #ef9a9a; font-weight: 600; font-size: 1rem;">⚠️ Mevcut İngilizce Oranı: %{ing_oran}</span>
            <span style="color: #e57373; font-size: 0.85rem;"> &nbsp;•&nbsp; İngilizce AKTS: {int(ing_toplam)} / {toplam_aktif}{devam_notu} &nbsp;•&nbsp; Mezuniyet için en az %30 gereklidir (Eksik: ~{eksik_akts} AKTS)</span>
        </div>
        """, unsafe_allow_html=True)
    st.progress(progress_val)

    st.markdown("---")

    # ===== DERS KARŞILAŞTIRMA TABLOSU =====
    st.markdown("### 📋 Ders Karşılaştırma Tablosu")
    st.markdown("""
    <div style="font-size: 0.85rem; color: #b0bec5; margin-bottom: 0.8rem;">
        🔴 Zorunlu Ders &nbsp;│&nbsp; 🟡 Seçmeli Ders &nbsp;│&nbsp;
        ✅ Başarılı &nbsp;│&nbsp;
        🔴 Başarısız &nbsp;│&nbsp;
        🟠 Eksik &nbsp;│&nbsp;
        🔵 Devam Ediyor
    </div>
    """, unsafe_allow_html=True)

    # Dönemlere göre grupla
    donemler = sorted(mufredat_df['Donem'].unique())

    for donem_no in donemler:
        donem_results = [r for r in results if r['Donem'] == donem_no]
        if not donem_results:
            continue

        st.markdown(f"""
        <div class="semester-header">
            📖 {get_donem_adi(donem_no)}
        </div>
        """, unsafe_allow_html=True)

        # İki sütunlu layout
        col_left, col_right = st.columns(2)

        with col_left:
            st.markdown("**📚 Müfredat Dersi**")

        with col_right:
            st.markdown("**📝 Transkript Durumu**")

        for r in donem_results:
            col_left, col_right = st.columns(2)
            css_class = get_css_class(r['Durum'])

            with col_left:
                tur_badge = "🔴" if r['Tur'] == 'Zorunlu' else "🟡"
                en_badge = ' <span style="background:#1565c0; color:white; padding:0.1rem 0.3rem; border-radius:3px; font-size:0.7rem; font-weight:600;">EN</span>' if r.get('Ingilizce', False) else ''
                st.markdown(f"""
                <div class="{css_class}">
                    {tur_badge} <strong>{r['Mufredat_Kodu']}</strong> — {r['Mufredat_Adi']}{en_badge}
                    <span style="float:right; font-weight:600;">{int(r['Mufredat_AKTS'])} AKTS</span>
                </div>
                """, unsafe_allow_html=True)

            with col_right:
                if r['Durum'] == 'Eksik':
                    st.markdown(f"""
                    <div class="{css_class}">
                        {r['Ikon']} <em>Ders transkriptte bulunamadı</em>
                    </div>
                    """, unsafe_allow_html=True)
                elif r['Durum'] == 'Devam Ediyor':
                    tr_info = f"{r['Transkript_Kodu']} — {r['Transkript_Adi']}" if r['Transkript_Adi'] else ""
                    st.markdown(f"""
                    <div class="{css_class}">
                        {r['Ikon']} {tr_info}
                        <span style="float:right;">[Devam Ediyor]</span>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    skor_text = f" (Skor: {r['Eslesme_Skoru']})" if r['Eslesme_Skoru'] < 100 else ""
                    st.markdown(f"""
                    <div class="{css_class}">
                        {r['Ikon']} <strong>{r['Transkript_Kodu']}</strong> — {r['Transkript_Adi']}
                        <span style="float:right; font-weight:600;">
                            [{r['Transkript_Notu']}]{skor_text}
                        </span>
                    </div>
                    """, unsafe_allow_html=True)

    # ===== EKSİK VE BAŞARISIZ DERSLER ÖZETİ =====
    eksik_dersler = [r for r in results if r['Durum'] == 'Eksik']
    basarisiz_dersler = [r for r in results if r['Durum'] == 'Başarısız']
    supheli_dersler = [r for r in results if r['Durum'] == 'Şüpheli Eşleşme']

    if eksik_dersler or basarisiz_dersler or supheli_dersler:
        st.markdown("---")
        st.markdown("### ⚠️ Dikkat Gerektiren Dersler")

        tab1, tab2, tab3 = st.tabs(["❌ Eksik Dersler", "🔴 Başarısız Dersler", "⚠️ Şüpheli Eşleşmeler"])

        with tab1:
            if eksik_dersler:
                for r in eksik_dersler:
                    st.markdown(f"- **{r['Mufredat_Kodu']}** — {r['Mufredat_Adi']} ({int(r['Mufredat_AKTS'])} AKTS) — _{r['Tur']}_")
            else:
                st.success("Eksik ders bulunmuyor! ✅")

        with tab2:
            if basarisiz_dersler:
                for r in basarisiz_dersler:
                    st.markdown(f"- **{r['Mufredat_Kodu']}** — {r['Mufredat_Adi']} — Not: **{r['Transkript_Notu']}**")
            else:
                st.success("Başarısız ders bulunmuyor! ✅")

        with tab3:
            if supheli_dersler:
                for r in supheli_dersler:
                    st.markdown(
                        f"- **{r['Mufredat_Kodu']}** ({r['Mufredat_Adi']}) ↔ "
                        f"**{r['Transkript_Kodu']}** ({r['Transkript_Adi']}) — "
                        f"Skor: **{r['Eslesme_Skoru']}**"
                    )
            else:
                st.success("Şüpheli eşleşme bulunmuyor! ✅")

    # ===== TRANSKRİPT HAM VERİ =====
    st.markdown("<br><br><br>", unsafe_allow_html=True)  # Araya boşluk ekledik
    st.markdown("---")
    
    with st.expander("📊 Transkriptten Okunan Ham Veri", expanded=False):
        st.dataframe(transkript_df, use_container_width=True, hide_index=True)
        st.caption(f"Toplam {len(transkript_df)} ders tespit edildi.")

    # ===== PDF RAPOR İNDİRME =====
    st.markdown("---")
    st.markdown("### 📥 Rapor İndirme")

    try:
        pdf_bytes = generate_report(results, summary, selected_mufredat)
        st.download_button(
            label="📄 Sonuç Raporunu PDF Olarak İndir",
            data=pdf_bytes,
            file_name=f"mezuniyet_raporu_{selected_mufredat.replace(' ', '_')}.pdf",
            mime="application/pdf",
            use_container_width=True,
        )
    except Exception as e:
        st.error(f"PDF oluşturulurken hata: {e}")
        st.info("Rapor oluşturulamadı, lütfen tekrar deneyin.")

    # ===== HATA BİLDİRİM FORMU (FEEDBACK) =====
    st.markdown("---")
    st.markdown("### 🐛 Hata Bildir / Geri Bildirim")
    st.info("Eşleşmeyen, yanlış eşleşen bir ders fark ettiyseniz veya sistemle ilgili bir öneriniz varsa form üzerinden bize iletebilirsiniz.")

    with st.expander("Geri Bildirim Formunu Aç", expanded=False):
        with st.form("feedback_form"):
            fb_type = st.selectbox("Bildirim Türü", ["Yanlış Eşleşme", "Eksik Ders", "Yeni Özellik Önerisi", "Diğer Durumlar"])
            fb_desc = st.text_area("Detaylı Açıklama (Örn: MMB104 dersi yanlış eşleşti, x olması gerekiyordu)")
            fb_email = st.text_input("E-posta Adresiniz (Geri dönüş yapılmasını istiyorsanız - İsteğe bağlı)")
            
            submit_btn = st.form_submit_button("Gönder")
            if submit_btn:
                if fb_desc.strip():
                    # Geliştiricinin e-posta adresi
                    dev_email = "bariskirli@trakya.edu.tr"  # Trakya Üniversitesi e-posta adresi
                    
                    # E-posta konu ve içeriği oluşturma
                    subject = f"Mezuniyet Sistemi Bildirimi: {fb_type}"
                    body = f"Bildirim Türü: {fb_type}%0D%0A"
                    body += f"Kullanıcı E-postası: {fb_email if fb_email else 'Belirtilmedi'}%0D%0A%0D%0A"
                    body += f"Açıklama:%0D%0A{fb_desc.replace(chr(10), '%0D%0A')}"
                    
                    mailto_link = f"mailto:{dev_email}?subject={subject}&body={body}"
                    
                    st.success("Bildiriminiz için teşekkürler! Sistemin arka planı (veritabanı) henüz bağlı olmadığı için lütfen aşağıdaki linke tıklayarak bildirimi e-posta ile gönderin:")
                    st.markdown(f'<a href="{mailto_link}" target="_blank" style="display: inline-block; padding: 0.5em 1em; color: white; background-color: #007bff; border-radius: 5px; text-decoration: none;">E-posta Göndermek İçin Tıklayın ✉️</a>', unsafe_allow_html=True)
                else:
                    st.error("Lütfen formu göndermeden önce detaylı açıklama girin.")

    # ===== FOOTER =====
    show_footer()


if __name__ == "__main__":
    main()
