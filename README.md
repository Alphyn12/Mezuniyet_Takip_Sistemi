<div align="center">

<img src="https://raw.githubusercontent.com/Alphyn12/Mezuniyet_Takip_Sistemi/main/assets/readme_banner.png" width="100%" alt="Banner">

# 🎓 Trakya Üniversitesi Mezuniyet Takip Sistemi

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge.svg)](https://tu-makina-mezuniyet.streamlit.app/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/Alphyn12/Mezuniyet_Takip_Sistemi/graphs/commit-activity)

**Trakya Üniversitesi Makine Mühendisliği öğrencileri için akıllı mezuniyet analiz platformu.**

[Canlı Sistemi Görüntüle 🚀](https://tu-makina-mezuniyet.streamlit.app/) • [Hata Bildir 🐛](https://github.com/Alphyn12/Mezuniyet_Takip_Sistemi/issues) • [Özellik Öner 💡](https://github.com/Alphyn12/Mezuniyet_Takip_Sistemi/issues)

</div>

---

## 📋 Genel Bakış

Bölüm müfredatları yıllara göre (2018, 2022, 2024 vb.) değişiklik gösterebilmektedir. Öğrencilerin hangi dersleri alması gerektiğini manuel olarak takip etmesi, kodları değişen eşdeğer derslerin çakışması veya eksik seçmeli derslerin hesaplanması hata yapmaya çok müsait bir süreçtir.

**Mezuniyet Takip Sistemi**, OBS'den alınan transkript PDF'lerini anında analiz ederek müfredat uyumluluğunu denetleyen, eksik dersleri listeleyen ve mezuniyet yol haritanızı netleştiren bağımsız bir araçtır.

## ✨ Temel Özellikler

*   🔍 **Gelişmiş PDF Analizi:** `pdfplumber` motoru ile transkript verilerini %99 doğrulukla dijitalleştirme.
*   🗺️ **Dinamik Müfredat Desteği:** 2018'den 2025'e kadar tüm güncel Makine Mühendisliği müfredatları ile uyumluluk.
*   🧠 **Akıllı Eşleştirme Sistemi:**
    *   **Levenshtein Algoritması:** Ders isimleri değişse bile benzerlik oranına göre otomatik tanıma.
    *   **Kategorik Filtreleme:** Teknik, Bölüm dışı ve Üniversite seçmelilerini otomatik sınıflandırma.
*   📊 **Detaylı İstatistikler:** AGNO (GANO) hesaplama, tamamlanan AKTS takibi ve dönem bazlı başarı analizi.
*   📑 **PDF Rapor Çıktısı:** Analiz sonuçlarını resmi danışman görüşmelerinde kullanmak üzere profesyonel PDF formatında indirme.
*   📱 **Modern ve Duyarlı Arayüz:** Streamlit tabanlı, karanlık mod (dark mode) odaklı ve mobil cihazlara tam uyumlu tasarım.

## 🚀 Hızlı Başlangıç (Lokal Kurulum)

Projeyi kendi bilgisayarınızda çalıştırmak için aşağıdaki adımları izleyin:

```bash
# 1. Repoyu klonlayın
git clone https://github.com/Alphyn12/Mezuniyet_Takip_Sistemi.git

# 2. Proje dizinine gidin
cd Mezuniyet_Takip_Sistemi

# 3. Bağımlılıkları yükleyin
pip install -r requirements.txt

# 4. Uygulamayı başlatın
streamlit run app.py
```

## 🛠️ Kullanılan Teknolojiler

- **Backend:** Python 3.9+
- **Frontend:** Streamlit
- **Veri Analizi:** Pandas, Openpyxl
- **PDF İşleme:** pdfplumber, FPDF2
- **Algoritma:** TheFuzz (Bulanık Eşleştirme)

## 👤 Geliştirici

**Barış KIRLI**  
*Trakya Üniversitesi Makine Mühendisliği Bölümü Öğrencisi*

---

<div align="center">

> [!IMPORTANT]
> Bu proje Trakya Üniversitesi Makine Mühendisliği öğrencilerine kolaylık sağlamak amacıyla bağımsız olarak geliştirilmiştir. **Resmi danışmanlık onayı yerine geçmez.**

</div>

<p align="right">(<a href="#top">başa dön</a>)</p>
