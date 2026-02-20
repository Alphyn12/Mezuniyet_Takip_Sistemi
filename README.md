# 🎓 Trakya Üniversitesi Mezuniyet Takip Sistemi

Trakya Üniversitesi Makine Mühendisliği Bölümü öğrencileri için geliştirilmiş; Öğrenci Bilgi Sistemi (OBS) üzerinden alınan transkript PDF dosyalarını anında analiz ederek öğrencinin mezuniyet durumunu kontrol eden açık kaynaklı ve akıllı bir web platformudur.

🔗 **Canlı Sistem Linki:** [https://tu-makina-mezuniyet.streamlit.app/](https://tu-makina-mezuniyet.streamlit.app/)

## 🌟 Neden Bu Sistem?
Bölüm müfredatları yıllara göre (2018, 2022, 2024 vb.) değişiklik gösterebilmektedir. Öğrencilerin hangi dersleri alması gerektiğini manuel olarak takip etmesi, eşdeğer sayılan (kodları değişen) derslerin çakışması veya kalıntılı/eksi seçmelilerin hesaplanması genellikle saatler süren hatalara açık bir süreçtir. 

Bu proje, transkript belgenizi otomatik okur, sizin yerinize müfredat analizi yapar ve mezuniyetiniz için kalanları listeler.

## 🚀 Temel Özellikler
* 📄 **PDF Transkript Analizi:** `pdfplumber` ile OBS'den indirilen PDF transkriptlerden hatasız metin ve tablo kazıma işlemi. 
* 📚 **Dinamik Müfredat Desteği:** 2018-2019'dan 2025-2026'ya kadar tüm resmi Makine Mühendisliği müfredatları ile doğrudan entegrasyon.
* 🧠 **Akıllı Eşleşme Algoritması:** 
  * "MAK" ve "MMB" gibi eski/yeni kod değişikliklerini tolere eden 3-aşamalı (`exact`, `fuzzy`, `category`) doğrulama sistemi.
  * `thefuzz` (Levenshtein distance) tabanlı bulanık (fuzzy) eşleştirme ile adı değişen ancak aynı sayılan seçmeli dersleri tanıma.
* 📊 **AGNO ve AKTS Hesaplama:** Eksik/başarısız derslerin listelenmesi, tamamlanan AKTS sayısı ve net AGNO okuması.
* 📥 **Detaylı Raporlama:** Analiz sonuçlarının, danışman hocalarla anında paylaşılabilmesi adına yazdırılabilir / indirilebilir **PDF Rapor** olarak sunulması.
* 🌙 **Modern Arayüz:** Streamlit mimarisi ile kurulmuş, karanlık (dark) tema zorunlu, mobil uyumlu ve hızlı web arayüzü.

## 🛠️ Kurulum & Lokal Çalıştırma
Projeyi kendi bilgisayarınızda (lokal sunucuda) test etmek veya geliştirmek isterseniz:

1. Repoyu bilgisayarınıza indirin:
```bash
git clone https://github.com/Alphyn12/Mezuniyet_Takip_Sistemi.git
cd Mezuniyet_Takip_Sistemi
```

2. Gerekli kütüphaneleri yükleyin (`pip` yüklü olmalıdır):
```bash
pip install -r requirements.txt
```

3. Uygulamayı başlatın:
```bash
streamlit run app.py
```
*Sistem tarayıcınızda otomatik olarak `http://localhost:8501` adresinde açılacaktır.*

## 👨‍💻 Geliştirici
**Barış KIRLI**  
Trakya Üniversitesi Makine Mühendisliği Bölümü Öğrencisi 

---
> 💡 *Bu proje Trakya Üniversitesi Makine Mühendisliği öğrencilerine kolaylık sağlamak amacıyla bağımsız olarak geliştirilmiştir. Resmi danışmanlık onayı yerine geçmez.*
