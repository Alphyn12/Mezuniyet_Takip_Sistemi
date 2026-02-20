import sys; sys.path.insert(0,'.')
import pandas as pd
from pdf_parser import parse_transcript
from matcher import match_courses, generate_summary

# Transkript 2'yi parse et
t = parse_transcript('transkript 2.pdf')
# Write output to file with utf-8 encoding
with open('debug_output_utf8.txt', 'w', encoding='utf-8') as f:
    f.write("=== TRANSKRIPT 2 PARSE SONUCU ===\n")
    f.write(f"Toplam ders: {len(t)}\n")
    f.write(f"Donemler: {t['Donem'].unique().tolist()}\n\n")

    # Tum dersleri listele
    f.write(f"{'DONEM':<20} | {'KOD':<12} | {'AD':<50} | {'AKTS':<5} | {'NOT':<4}\n")
    f.write("-" * 100 + "\n")
    for _, row in t.sort_values('Ders_Kodu').iterrows():
        f.write(f"{row['Donem']:<20} | {row['Ders_Kodu']:<12} | {row['Ders_Adi'][:50]:<50} | {str(row['AKTS']):<5} | {row['Harf_Notu']:<4}\n")
    
    # 2024-2025 mufredat ile eslestir
    f.write("\n=== ESLESTIRME SONUCU (2024-2025 Mufredat) ===\n")
    try:
        m = pd.read_excel('mufredatlar/mufredat_2024.xlsx') # User selected 2024 in screenshot
        f.write(f"Mufredat (2024) ders sayisi: {len(m)}\n")
    except:
        f.write("Mufredat dosyasi bulunamadi!\n")
        sys.exit()

    r = match_courses(m, t)
    s = generate_summary(r, t)

    # Sorunlu dersler
    eksik = [x for x in r if x['Durum'] == 'Eksik']
    
    f.write(f"\nEksik dersler ({len(eksik)}):\n")
    for x in eksik:
        f.write(f"  {x['Mufredat_Kodu']} - {x['Mufredat_Adi']} ({x['Mufredat_AKTS']} AKTS)\n")
