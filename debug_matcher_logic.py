import pandas as pd
import re
from thefuzz import fuzz, process

def normalize_code(code: str) -> str:
    return re.sub(r'\s+', '', str(code).strip().upper())

def is_elective_slot(ders_kodu: str) -> bool:
    code = str(ders_kodu).strip().upper()
    return ('XX' in code) or ('UNI-SEC' in code)

def classify_transcript_elective(ders_kodu: str) -> str:
    code = normalize_code(ders_kodu)
    # 2025 format
    if re.match(r'(MMB|MED)35\d{2}', code): return 'isil_tasarim'
    if re.match(r'(MMB|MED)36\d{2}', code): return 'mekanik_tasarim'
    if re.match(r'(MMB|MED)45\d{2}', code): return 'bolum_mekanik'
    if re.match(r'(MMB|MED)46\d{2}', code): return 'bolum_termo'
    if re.match(r'(MMB|MED)47\d{2}', code): return 'bolum_konstruksiyon'
    # 2022/2024 format
    if re.match(r'(MMB|MAK|MEC)30\d{2}', code): return 'tasarim_secmeli'
    if re.match(r'(MMB|MAK|MEC)41\d{2}', code): return 'bolum_mekanik'
    if re.match(r'(MMB|MAK|MEC)42\d{2}', code): return 'bolum_termo'
    if re.match(r'(MMB|MAK|MEC)43\d{2}', code): return 'bolum_konstruksiyon'
    if not re.match(r'(MMB|MAK|MEC|MED|MTH|MAT|FİZ|KİM|BİL|ZTD|ZAI|MUH|HZD)', code): return 'universite'
    return 'bilinmiyor'

def match_courses_debug(mufredat_df, transkript_df):
    results = []
    
    # Trace specific codes
    TRACE_CODES = ['MMB411', 'MMB421', 'MAK324', 'MMB324', 'MMB4303']
    
    tr_codes = {normalize_code(c): i for i, c in enumerate(transkript_df['Ders_Kodu'])}
    used_transcript_indices = set()
    
    print("DEBUG: tr_codes keys:", tr_codes.keys())

    elective_pool = {}
    for idx, row in transkript_df.iterrows():
        cat = classify_transcript_elective(row['Ders_Kodu'])
        if cat != 'bilinmiyor':
            if cat not in elective_pool: elective_pool[cat] = []
            elective_pool[cat].append(idx)
    
    print("DEBUG: Elective Pool:", elective_pool)

    for _, muf_row in mufredat_df.iterrows():
        muf_code = muf_row['Ders_Kodu']
        norm_muf_code = normalize_code(muf_code)
        
        is_traced = norm_muf_code in TRACE_CODES or any(t in norm_muf_code for t in TRACE_CODES)
        
        if is_traced:
             print(f"\nProcessing Mufredat: {muf_code} (Norm: {norm_muf_code})")

        result = {'Mufredat_Kodu': muf_code, 'Durum': 'Eksik'}

        # SEÇMELİ
        if is_elective_slot(muf_code):
            if is_traced: print(f"  -> Detected as Elective Slot")
            # (Skipping elective logic details for brevity unless needed)
            continue

        # ZORUNLU
        matched_by_code = False
        if norm_muf_code in tr_codes:
            if is_traced: print(f"  -> Found in tr_codes! Index: {tr_codes[norm_muf_code]}")
            tr_idx = tr_codes[norm_muf_code]
            if tr_idx not in used_transcript_indices:
                result['Durum'] = 'Başarılı' # Mock
                used_transcript_indices.add(tr_idx)
                matched_by_code = True
                if is_traced: print("  -> Match CONFIRMED.")
            else:
                 if is_traced: print(f"  -> Index {tr_idx} ALREADY USED!")
        else:
             if is_traced: print(f"  -> NOT found in tr_codes.")

        results.append(result)
    
    return results

# --- RUNNER ---
data = [
    {'Ders_Kodu': 'MMB411', 'Ders_Adi': 'Mekanik Sistem Tasarımı', 'AKTS': 4.0},
    {'Ders_Kodu': 'MMB421', 'Ders_Adi': 'Bitirme Tezi', 'AKTS': 6.0},
    {'Ders_Kodu': 'MAK324', 'Ders_Adi': 'LABORATUVAR -II', 'AKTS': 1.0},
]
transkript_df = pd.DataFrame(data)

try:
    mufredat_df = pd.read_excel('mufredatlar/mufredat_2024.xlsx')
except:
    print("Mufredat 2024 not found, using empty")
    mufredat_df = pd.DataFrame({'Ders_Kodu': ['MMB 411', 'MMB 421', 'MMB 324'], 'Ders_Adi': ['X', 'Y', 'Z'], 'AKTS': [4,6,1], 'Tur':['Zorunlu','Zorunlu','Zorunlu'], 'Donem':['1','1','1']})

with open('debug_logic_output.txt', 'w', encoding='utf-8') as f:
    import sys
    sys.stdout = f
    match_courses_debug(mufredat_df, transkript_df)
