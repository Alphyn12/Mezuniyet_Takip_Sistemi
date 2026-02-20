import pandas as pd
from pdf_parser import parse_transcript
from matcher import match_courses, generate_summary

# Create a mock transcript with a failed course and a later successful retake
data = [
    {'Ders_Kodu': 'MMB224', 'Ders_Adi': 'TERMODİNAMİK - II', 'AKTS': 4.0, 'Harf_Notu': 'FF', 'Basarisiz': True, 'Donem': '2022-2023 Bahar'},
    {'Ders_Kodu': 'MMB224', 'Ders_Adi': 'TERMODİNAMİK - II', 'AKTS': 4.0, 'Harf_Notu': 'BA', 'Basarisiz': False, 'Donem': '2023-2024 Bahar'},
    {'Ders_Kodu': 'MMB225E', 'Ders_Adi': 'DIFFERENTIAL EQUATIONS', 'AKTS': 8.0, 'Harf_Notu': 'DZ', 'Basarisiz': True, 'Donem': '2023-2024 Bahar'}
]

# We need to simulate the raw parse list BEFORE drop_duplicates to see if drop_duplicates
# is the issue, or if creating the dataframe from the raw list does something wrong.
df_raw = pd.DataFrame(data)

print("=== RAW PARSED DATA ===")
print(df_raw)

# Simulate pdf_parser logic
df_final = df_raw.drop_duplicates(subset=['Ders_Kodu'], keep='last')

print("\n=== FINAL TRANSCRIPT DF (After drop_duplicates) ===")
print(df_final)

# Let's test it with the real transcript to see what the parser actually spits out
t = parse_transcript('transkript 2.pdf')

print("\n=== REAL TRANSCRIPT MMB224 ENTRIES ===")
# parse_transcript already drops duplicates, so we won't see multiple entries here unless
# the course codes aren't matching perfectly in the raw PDF.
mmb224_entries = t[t['Ders_Kodu'].str.contains('MMB224', regex=False, na=False)]
print(mmb224_entries)

# We need to hook into the raw data before drop_duplicates.
# Let's write a quick dirty parse to see the raw list.
import re
import pdfplumber
import io

def get_raw_courses(filename):
    pdf = pdfplumber.open(filename)
    all_courses = []
    semester_pattern = re.compile(r'(20\d{2}\s*[-–]\s*20\d{2}\s+(?:Güz|Bahar|G[üu]z|Bahar))', re.IGNORECASE)
    course_pattern = re.compile(
        r'^([A-ZÇĞİÖŞÜa-zçğıöşü]{2,6}\s?\d{2,5}[A-Za-z]?)\s+'
        r'(.+?)\s+(\d+[.,]?\d*)\s+(\d+[.,]?\d*)\s+([\d.,]+|--)\s+([A-Z]{2}|--)$',
        re.IGNORECASE
    )
    for page in pdf.pages:
        for table in page.extract_tables():
            if not table or len(table) < 2: continue
            first_cell = str(table[0][0] or "").strip()
            if first_cell in ("Harf", "Puan", "Katsayı"): continue
            
            sem_match = semester_pattern.search(first_cell)
            current_semester = sem_match.group(1).strip() if sem_match else ""
            if not current_semester: continue

            for row in table[1:]:
                if not row or not row[0]: continue
                cell = str(row[0]).strip()
                match = course_pattern.match(cell)
                if match:
                    all_courses.append({
                        'Kodu': match.group(1).strip().replace(" ", "").upper(),
                        'Notu': match.group(6).strip().upper(),
                        'Donem': current_semester
                    })
    return all_courses

raw = get_raw_courses('transkript 2.pdf')
m224 = [c for c in raw if 'MMB224' in c['Kodu'] or 'MMB 224' in c['Kodu'] or 'MAK224' in c['Kodu']]
print("\n=== RAW PDF EXTRACT FOR MMB224/MAK224 ===")
for c in m224:
    print(c)
