import pandas as pd
from matcher import match_courses, normalize_code, classify_transcript_elective

# Mock Transkript Data based on debug output
data = [
    {'Ders_Kodu': 'MMB411', 'Ders_Adi': 'Mekanik Sistem Tasarımı', 'AKTS': 4.0, 'Harf_Notu': 'AA', 'Basarisiz': False, 'Donem': '2025-2026 Güz'},
    {'Ders_Kodu': 'MMB421', 'Ders_Adi': 'Bitirme Tezi', 'AKTS': 6.0, 'Harf_Notu': 'Devam Ediyor', 'Basarisiz': False, 'Donem': '2025-2026 Bahar'},
    {'Ders_Kodu': 'MAK324', 'Ders_Adi': 'LABORATUVAR -II', 'AKTS': 1.0, 'Harf_Notu': 'BA', 'Basarisiz': False, 'Donem': '2024-2025 Bahar'},
    {'Ders_Kodu': 'MMB4303', 'Ders_Adi': 'Kaldırma ve İletme Makinaları', 'AKTS': 5.0, 'Harf_Notu': 'Devam Ediyor', 'Basarisiz': False, 'Donem': '2025-2026 Bahar'},
    {'Ders_Kodu': 'MMB3009', 'Ders_Adi': 'ENERJİ ÜRETİM SİSTEMLERİ', 'AKTS': 5.0, 'Harf_Notu': 'CB', 'Basarisiz': False, 'Donem': '2024-2025 Güz'},
    {'Ders_Kodu': 'MMB3010', 'Ders_Adi': 'İMALAT YÖNTEMLERİ -II', 'AKTS': 5.0, 'Harf_Notu': 'AA', 'Basarisiz': False, 'Donem': '2024-2025 Güz'},
    {'Ders_Kodu': 'MAK3002', 'Ders_Adi': 'İLERİ TEKNOLOJİ MALZEMELERİ', 'AKTS': 5.0, 'Harf_Notu': 'AA', 'Basarisiz': False, 'Donem': '2024-2025 Bahar'},
]

transkript_df = pd.DataFrame(data)

with open('reproduction_output.txt', 'w', encoding='utf-8') as f:
    f.write("=== MOCK TRANSCRIPT DF ===\n")
    f.write(transkript_df.to_string() + "\n")

    f.write("\n=== ELECTROVE CATEGORIES ===\n")
    for code in transkript_df['Ders_Kodu']:
        cat = classify_transcript_elective(code)
        f.write(f"{code} -> {cat}\n")

    # Load Mufredat
    try:
        mufredat_df = pd.read_excel('mufredatlar/mufredat_2024.xlsx')
        f.write(f"\nLoaded mufredat_2024.xlsx with {len(mufredat_df)} rows\n")
    except:
        # Use 2025 if 2024 not found, strictly for testing logic
        try:
            mufredat_df = pd.read_excel('mufredatlar/mufredat_2025.xlsx')
            f.write(f"\nLoaded mufredat_2025.xlsx with {len(mufredat_df)} rows\n")
        except:
             f.write("No mufredat found\n")
             import sys; sys.exit()

    # Run Matcher
    results = match_courses(mufredat_df, transkript_df)

    # Check specific problematic courses
    problem_codes = ['MMB 411', 'MMB 421', 'MMB 324', 'MMB 43xx', 'MMB 30xx', 'MAK 324']

    f.write("\n=== ALL MATCHING RESULTS ===\n")
    for r in results:
        if r['Transkript_Kodu']:
            f.write(f"Mufredat: {r['Mufredat_Kodu']} ({r['Mufredat_Adi']}) -> Tr: {r['Transkript_Kodu']} ({r['Transkript_Adi']}) | Score: {r['Eslesme_Skoru']}\n")
        else:
            f.write(f"Mufredat: {r['Mufredat_Kodu']} ({r['Mufredat_Adi']}) -> NOT MATCHED\n")
