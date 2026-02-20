# -*- coding: utf-8 -*-
"""
PDF Parser Modülü
=================
Öğrenci transkript PDF dosyalarını okuyarak yapılandırılmış veri çıkarır.
pdfplumber kullanarak tablo verilerini ayrıştırır ve pandas DataFrame'e dönüştürür.
"""

import re
import pdfplumber
import pandas as pd
import io


def normalize_code(code: str) -> str:
    """Ders kodundaki boşlukları kaldırarak normalize eder.
    Örn: 'MMB 312E' -> 'MMB312E', 'FİZ 103' -> 'FİZ103'
    """
    return re.sub(r'\s+', '', code.strip().upper())


def parse_transcript(uploaded_file) -> tuple:
    """
    Yüklenen transkript PDF dosyasını okuyarak ders bilgilerini çıkarır.

    Transkript yapısı (her tablo):
        R0: ['2022-2023 Güz', None, ...]     <- Dönem başlığı
        R1: ['Ders Kodu', 'Ders Adı', ...]   <- Sütun başlıkları
        R2-Rn: ['BİL107 BİLGİSAYAR... 3 4 12 AA', None, ...]  <- Ders verileri
        Son satırlar: ANO / AGNO

    Parameters:
        uploaded_file: Streamlit file_uploader'dan gelen dosya objesi veya dosya yolu

    Returns:
        tuple: (pd.DataFrame, float) - Derslerin tablosu ve PDF'ten okunan AGNO
    """
    # PDF dosyasını oku
    if hasattr(uploaded_file, 'read'):
        pdf_bytes = uploaded_file.read()
        uploaded_file.seek(0)
        pdf = pdfplumber.open(io.BytesIO(pdf_bytes))
    else:
        pdf = pdfplumber.open(uploaded_file)

    all_courses = []
    parsed_agno = 0.0

    # Dönem algılama regex'i: "2022-2023 Güz" veya "2025 - 2026 Bahar"
    semester_pattern = re.compile(r'(20\d{2}\s*[-–]\s*20\d{2}\s+(?:Güz|Bahar|G[üu]z|Bahar))', re.IGNORECASE)
    
    # AGNO algılama regex'i
    agno_pattern = re.compile(r'AGNO\s+(?:::\s*)?(\d+[.,]\d+)', re.IGNORECASE)

    # Ders satırı regex'i:
    # DERSKODU DERSADI KREDİ AKTS PUAN HARFNOTU
    course_pattern = re.compile(
        r'^([A-ZÇĞİÖŞÜa-zçğıöşü]{2,6}\s?\d{2,5}[A-Za-z]?)\s+'  # Ders kodu
        r'(.+?)\s+'                                                  # Ders adı
        r'(\d+[.,]?\d*)\s+'                                         # Kredi
        r'(\d+[.,]?\d*)\s+'                                         # AKTS
        r'([\d.,]+|--)\s+'                                           # Puan
        r'([A-Z]{2}|--)$',                                           # Harf notu
        re.IGNORECASE
    )

    # Tüm sayfaları ve tabloları tara
    for page in pdf.pages:
        # AGNO parsing from raw text
        text = page.extract_text()
        if text:
            matches = agno_pattern.findall(text)
            if matches:
                parsed_agno = float(matches[-1].replace(',', '.'))
                
        tables = page.extract_tables()

        for table in tables:
            if not table or len(table) < 2:
                continue

            # İlk satırdan dönem bilgisini al
            first_cell = str(table[0][0] or "").strip()

            # Harf/Puan/Katsayı not tablosunu atla
            if first_cell in ("Harf", "Puan", "Katsayı"):
                continue

            # Dönem bilgisini çıkar
            current_semester = ""
            sem_match = semester_pattern.search(first_cell)
            if sem_match:
                current_semester = sem_match.group(1).strip()
            else:
                # Dönem bilgisi olmayan tabloda — genel bilgi tablosu olabilir
                continue

            # Her satırı işle (ilk 2 satır başlık, son satırlar ANO/AGNO)
            for row in table[1:]:  # İlk satır (dönem başlığı) atla
                if not row or not row[0]:
                    continue

                cell = str(row[0]).strip()

                # Başlık ve özet satırları atla
                if cell.startswith("Ders Kodu") or cell.startswith("Ders Ko"):
                    continue
                if cell in ("ANO", "AGNO") or cell.startswith("ANO") or cell.startswith("AGNO"):
                    continue
                if cell.startswith("Toplam") or cell.startswith("Genel"):
                    continue

                # Ders satırını regex ile ayrıştır
                match = course_pattern.match(cell)
                if match:
                    ders_kodu = match.group(1).strip()
                    ders_adi = match.group(2).strip()
                    akts_str = match.group(4).replace(',', '.')
                    harf_notu = match.group(6).strip().upper()

                    # AKTS'yi float'a çevir
                    try:
                        akts_val = float(akts_str)
                    except ValueError:
                        akts_val = 0

                    # Harf notu '--' ise henüz not girilmemiş
                    if harf_notu == '--':
                        harf_notu = 'Devam Ediyor'

                    # Başarısızlık durumu
                    basarisiz = harf_notu in ('FF', 'FD', 'DZ')

                    all_courses.append({
                        'Ders_Kodu': normalize_code(ders_kodu),
                        'Ders_Adi': ders_adi,
                        'AKTS': akts_val,
                        'Harf_Notu': harf_notu,
                        'Basarisiz': basarisiz,
                        'Donem': current_semester
                    })

    pdf.close()

    if not all_courses:
        return pd.DataFrame(columns=['Ders_Kodu', 'Ders_Adi', 'AKTS', 'Harf_Notu', 'Basarisiz', 'Donem']), parsed_agno

    df = pd.DataFrame(all_courses)

    # Aynı ders birden fazla kez alınmışsa (tekrar/iyileştirme),
    # kodu farklı olsa bile (MAK224 -> MMB224) aynı ders sayılmalı.
    # Bunun için 'MAK' veya 'MMB' öneklerini silip geçici bir baz kod oluşturalım.
    def get_base_code(code):
        c = str(code)
        if c.startswith('MMB') or c.startswith('MAK'):
            return c[3:] # Sadece sayı (ve varsa E) kısmını al
        return c

    df['Base_Kodu'] = df['Ders_Kodu'].apply(get_base_code)

    # En son alınan (son dönem) kaydı tut (orijinal sırasına göre sonuncu)
    df = df.drop_duplicates(subset=['Base_Kodu'], keep='last')
    
    # Geçici kolonu sil
    df = df.drop(columns=['Base_Kodu'])

    return df, parsed_agno
