# -*- coding: utf-8 -*-
"""
Bulanık Eşleştirme (Fuzzy Matching) Modülü
===========================================
Müfredattaki dersler ile transkriptteki dersleri eşleştirir.
Ders kodu bazlı kesin eşleştirme + ders adı bazlı bulanık eşleştirme kullanır.
"""

import re
import pandas as pd
from thefuzz import fuzz, process


def normalize_code(code: str) -> str:
    """Ders kodundaki boşlukları kaldırarak normalize eder."""
    return re.sub(r'\s+', '', code.strip().upper())


# İngilizce ders olarak sayılan ek kodlar (sonu E ile bitmeyen ama İngilizce olan dersler)
EXTRA_ENGLISH_CODES = {'MTH101', 'MTH102', 'MEC321', 'MEC325'}


def is_english_course(ders_kodu: str) -> bool:
    """Dersin İngilizce olup olmadığını belirler.
    Kural: Ders kodu 'E' harfi ile bitiyorsa VEYA özel listede yer alıyorsa İngilizce.
    """
    code = normalize_code(ders_kodu)
    if code in EXTRA_ENGLISH_CODES:
        return True
    # Kodun son karakteri 'E' ve ondan önceki karakter rakam ise (ör: MMB312E)
    if len(code) >= 4 and code[-1] == 'E' and code[-2].isdigit():
        return True
    return False


def is_elective_slot(ders_kodu: str) -> bool:
    """Müfredattaki genel seçmeli slot mu kontrol eder.
    Örn: 'MMB 30xx', 'MAK41xx', 'UNI-SEC', 'MMB35xx'
    """
    code = ders_kodu.strip().upper()
    return ('XX' in code) or ('UNI-SEC' in code)


def get_elective_category(ders_kodu: str) -> str:
    """Seçmeli ders kodunun kategorisini belirler.
    Döndürdükleri: 'mekanik_tasarim', 'isil_tasarim', 'bolum_mekanik',
    'bolum_termo', 'bolum_konstruksiyon', 'universite', 'bilinmiyor'
    """
    code = normalize_code(ders_kodu)
    
    # 2025 müfredatı: 35xx (Isıl), 36xx (Mekanik), 45xx, 46xx, 47xx
    if re.match(r'(MMB|MED)35', code):
        return 'isil_tasarim'
    if re.match(r'(MMB|MED)36', code):
        return 'mekanik_tasarim'
    if re.match(r'(MMB|MED)45', code):
        return 'bolum_mekanik'
    if re.match(r'(MMB|MED)46', code):
        return 'bolum_termo'
    if re.match(r'(MMB|MED)47', code):
        return 'bolum_konstruksiyon'

    # 2022/2024 müfredatı: 30xx, 41xx, 42xx, 43xx
    if re.match(r'(MMB|MAK|MEC)30', code):
        return 'tasarim_secmeli'  # Hem mekanik hem ısıl olabilir
    if re.match(r'(MMB|MAK|MEC)41', code):
        return 'bolum_mekanik'
    if re.match(r'(MMB|MAK|MEC)42', code):
        return 'bolum_termo'
    if re.match(r'(MMB|MAK|MEC)43', code):
        return 'bolum_konstruksiyon'
    if 'UNI' in code or 'SEC' in code:
        return 'universite'
    
    return 'bilinmiyor'


def classify_transcript_elective(ders_kodu: str) -> str:
    """Transkriptteki dersin hangi seçmeli kategorisine ait olduğunu belirler.
    Ders koduna bakarak seçmeli türünü tespit eder.
    """
    code = normalize_code(ders_kodu)
    
    # 2025 format: 35xx/36xx serisi (5-6. YY), 45xx/46xx/47xx serisi (7-8. YY)
    if re.match(r'(MMB|MED)35\d{2}', code):
        return 'isil_tasarim'
    if re.match(r'(MMB|MED)36\d{2}', code):
        return 'mekanik_tasarim'
    if re.match(r'(MMB|MED)45\d{2}', code):
        return 'bolum_mekanik'
    if re.match(r'(MMB|MED)46\d{2}', code):
        return 'bolum_termo'
    if re.match(r'(MMB|MED)47\d{2}', code):
        return 'bolum_konstruksiyon'

    # 2022/2024 format: 30xx serisi (5-6. YY), 41xx/42xx/43xx serisi (7-8. YY)
    if re.match(r'(MMB|MAK|MEC)30\d{2}', code):
        return 'tasarim_secmeli'
    if re.match(r'(MMB|MAK|MEC)41\d{2}', code):
        return 'bolum_mekanik'
    if re.match(r'(MMB|MAK|MEC)42\d{2}', code):
        return 'bolum_termo'
    if re.match(r'(MMB|MAK|MEC)43\d{2}', code):
        return 'bolum_konstruksiyon'
    
    # Alan dışı seçmeli: Farklı bölüm kodları (CEK, MAD, vb.)
    if not re.match(r'(MMB|MAK|MEC|MED|MTH|MAT|FİZ|KİM|BİL|ZTD|ZAI|MUH|HZD)', code):
        return 'universite'
    
    return 'bilinmiyor'


def match_courses(mufredat_df: pd.DataFrame, transkript_df: pd.DataFrame) -> list:
    """
    Müfredat ile transkriptteki dersleri eşleştirir.

    Eşleştirme stratejisi (Çok Geçişli Algoritma):
    Pass 0: Seçmeli dersleri kategorize et.
    Pass 1: Seçmeli dersleri müfredat slotlarıyla eşleştir.
    Pass 2: Kalan dersleri EXACT ders kodlarına (MAK/MMB varyasyonları dahil) göre eşleştir.
    Pass 3: Hala eşleşmeyenleri ders adına göre FUZZY match (Bulanık Eşleştirme) ile eşleştir.
    """
    results = []
    
    transkript_df = transkript_df.reset_index(drop=True)
    tr_codes = {normalize_code(c): i for i, c in enumerate(transkript_df['Ders_Kodu'])}
    used_transcript_indices = set()

    elective_pool = {}
    for idx, row in transkript_df.iterrows():
        cat = classify_transcript_elective(row['Ders_Kodu'])
        if cat != 'bilinmiyor':
            if cat not in elective_pool:
                elective_pool[cat] = []
            elective_pool[cat].append(idx)

    # Initialize results list
    for _, muf_row in mufredat_df.iterrows():
        muf_code = muf_row['Ders_Kodu']
        muf_name = muf_row['Ders_Adi']
        muf_akts = muf_row['AKTS']
        muf_tur = muf_row['Tur']
        muf_donem = muf_row['Donem']
        
        results.append({
            'Donem': muf_donem,
            'Mufredat_Kodu': muf_code,
            'Mufredat_Adi': muf_name,
            'Mufredat_AKTS': muf_akts,
            'Tur': muf_tur,
            'Transkript_Kodu': '',
            'Transkript_Adi': '',
            'Transkript_Notu': '',
            'Transkript_AKTS': 0,
            'Eslesme_Skoru': 0,
            'Durum': 'Eksik',
            'Basarisiz': False,
            'Ikon': '❌',
            'Ingilizce': is_english_course(muf_code),
            '_matched': False # temporary flag
        })

    # PASS 1: SEÇMELİ DERS EŞLEŞTİRME
    for result in results:
        muf_code = result['Mufredat_Kodu']
        if is_elective_slot(muf_code):
            cat = get_elective_category(muf_code)
            search_cats = [cat]
            if cat == 'tasarim_secmeli':
                search_cats = ['tasarim_secmeli', 'mekanik_tasarim', 'isil_tasarim']
            elif cat == 'mekanik_tasarim':
                search_cats = ['mekanik_tasarim', 'tasarim_secmeli']
            elif cat == 'isil_tasarim':
                search_cats = ['isil_tasarim', 'tasarim_secmeli']

            for search_cat in search_cats:
                if search_cat in elective_pool:
                    for tr_idx in list(elective_pool[search_cat]):
                        if tr_idx not in used_transcript_indices:
                            tr_row = transkript_df.loc[tr_idx]
                            result['Transkript_Kodu'] = tr_row['Ders_Kodu']
                            result['Transkript_Adi'] = tr_row['Ders_Adi']
                            result['Transkript_Notu'] = tr_row['Harf_Notu']
                            result['Transkript_AKTS'] = tr_row['AKTS']
                            result['Basarisiz'] = tr_row['Basarisiz']
                            result['Eslesme_Skoru'] = 100
                            result['_matched'] = True

                            if tr_row['Harf_Notu'] == 'Devam Ediyor':
                                result['Durum'] = 'Devam Ediyor'
                                result['Ikon'] = '🔵'
                            elif tr_row['Basarisiz']:
                                result['Durum'] = 'Başarısız'
                                result['Ikon'] = '❌'
                            else:
                                result['Durum'] = 'Başarılı'
                                result['Ikon'] = '✅'

                            used_transcript_indices.add(tr_idx)
                            elective_pool[search_cat].remove(tr_idx)
                            if is_english_course(tr_row['Ders_Kodu']):
                                result['Ingilizce'] = True
                            break
                if result['_matched']:
                    break

    # PASS 2: EXACT CODE MATCHING FOR ZORUNLU
    for result in results:
        if result['_matched'] or is_elective_slot(result['Mufredat_Kodu']):
            continue
            
        muf_code = result['Mufredat_Kodu']
        norm_muf_code = normalize_code(muf_code)
        
        candidate_codes = [norm_muf_code]
        if norm_muf_code.startswith('MMB'):
            candidate_codes.append(norm_muf_code.replace('MMB', 'MAK'))
        elif norm_muf_code.startswith('MAK'):
            candidate_codes.append(norm_muf_code.replace('MAK', 'MMB'))
            
        for cand in candidate_codes:
            if cand in tr_codes:
                tr_idx = tr_codes[cand]
                if tr_idx not in used_transcript_indices:
                    tr_row = transkript_df.loc[tr_idx]
                    result['Transkript_Kodu'] = tr_row['Ders_Kodu']
                    result['Transkript_Adi'] = tr_row['Ders_Adi']
                    result['Transkript_Notu'] = tr_row['Harf_Notu']
                    result['Transkript_AKTS'] = tr_row['AKTS']
                    result['Basarisiz'] = tr_row['Basarisiz']
                    result['Eslesme_Skoru'] = 100
                    result['_matched'] = True
                    
                    if tr_row['Harf_Notu'] == 'Devam Ediyor':
                        result['Durum'] = 'Devam Ediyor'
                        result['Ikon'] = '🔵'
                    elif tr_row['Basarisiz']:
                        result['Durum'] = 'Başarısız'
                        result['Ikon'] = '❌'
                    else:
                        result['Durum'] = 'Başarılı'
                        result['Ikon'] = '✅'
                        
                    used_transcript_indices.add(tr_idx)
                    break

    # PASS 3: FUZZY NAME MATCHING FOR REMAINING
    for result in results:
        if result['_matched'] or is_elective_slot(result['Mufredat_Kodu']):
            continue
            
        muf_name = result['Mufredat_Adi']
        available_indices = [i for i in range(len(transkript_df)) if i not in used_transcript_indices]
        
        if available_indices:
            available_names = [transkript_df.iloc[i]['Ders_Adi'] for i in available_indices]
            choices_dict = {i: name for i, name in enumerate(available_names)}
            
            best_match = process.extractOne(muf_name, choices_dict, scorer=fuzz.token_sort_ratio)
            
            if best_match:
                match_name = best_match[0]
                score = best_match[1]
                match_idx_in_list = best_match[2] if len(best_match) > 2 else available_names.index(match_name)
                actual_idx = available_indices[match_idx_in_list]
                tr_row = transkript_df.iloc[actual_idx]
                
                if score >= 65:
                    result['Transkript_Kodu'] = tr_row['Ders_Kodu']
                    result['Transkript_Adi'] = tr_row['Ders_Adi']
                    result['Transkript_Notu'] = tr_row['Harf_Notu']
                    result['Transkript_AKTS'] = tr_row['AKTS']
                    result['Basarisiz'] = tr_row['Basarisiz']
                    result['Eslesme_Skoru'] = score
                    result['_matched'] = True
                    
                    if score >= 85:
                        if tr_row['Harf_Notu'] == 'Devam Ediyor':
                            result['Durum'] = 'Devam Ediyor'
                            result['Ikon'] = '🔵'
                        elif tr_row['Basarisiz']:
                            result['Durum'] = 'Başarısız'
                            result['Ikon'] = '❌'
                        else:
                            result['Durum'] = 'Başarılı'
                            result['Ikon'] = '✅'
                    else:
                        result['Durum'] = 'Şüpheli Eşleşme'
                        result['Ikon'] = '⚠️'
                        
                    used_transcript_indices.add(actual_idx)

    # Clean up temporary flag
    for r in results:
        r.pop('_matched', None)

    return results


def generate_summary(results: list, transkript_df: pd.DataFrame, parsed_agno: float = 0.0) -> dict:
    """
    Eşleştirme sonuçlarından özet istatistikleri üretir.

    Returns:
        dict: toplam_akts, basarili_akts, eksik_ders_sayisi, basarisiz_ders_sayisi,
              supheli_sayisi, devam_eden_sayisi, mezuniyet_durumu
    """
    toplam_mufredat_akts = sum(r['Mufredat_AKTS'] for r in results)
    basarili_akts = sum(
        r['Mufredat_AKTS'] for r in results
        if r['Durum'] == 'Başarılı'
    )
    eksik = sum(1 for r in results if r['Durum'] == 'Eksik')
    basarisiz = sum(1 for r in results if r['Durum'] == 'Başarısız')
    supheli = sum(1 for r in results if r['Durum'] == 'Şüpheli Eşleşme')
    devam_eden = sum(1 for r in results if r['Durum'] == 'Devam Ediyor')
    basarili = sum(1 for r in results if r['Durum'] == 'Başarılı')

    if parsed_agno > 0:
        agno = parsed_agno
    else:
        # AGNO hesaplama (transkriptten)
        katsayi_map = {
            'AA': 4.0, 'BA': 3.5, 'BB': 3.0, 'CB': 2.5, 'CC': 2.0,
            'DC': 1.5, 'DD': 1.5, 'FD': 1.0, 'FF': 0.0, 'BL': None, 'DZ': 0.0
        }
        
        toplam_puan = 0
        toplam_akts_hesap = 0
        for _, row in transkript_df.iterrows():
            notu = row['Harf_Notu']
            if notu in katsayi_map and katsayi_map[notu] is not None:
                toplam_puan += katsayi_map[notu] * row['AKTS']
                toplam_akts_hesap += row['AKTS']
        
        agno = round(toplam_puan / toplam_akts_hesap, 2) if toplam_akts_hesap > 0 else 0.0

    # Mezuniyet durumu
    if eksik == 0 and basarisiz == 0 and devam_eden == 0 and supheli == 0:
        mezuniyet = "✅ Mezuniyet Koşulları Sağlanıyor"
    elif devam_eden > 0 and eksik == 0 and basarisiz == 0:
        mezuniyet = "🔵 Dersler Devam Ediyor"
    else:
        mezuniyet = f"❌ Mezuniyet Koşulları Sağlanmıyor ({eksik} eksik, {basarisiz} başarısız)"

    # İngilizce ders AKTS hesaplama (başarılı + devam eden)
    ingilizce_basarili_akts = sum(
        r['Mufredat_AKTS'] for r in results
        if r['Durum'] == 'Başarılı' and r.get('Ingilizce', False)
    )
    ingilizce_devam_akts = sum(
        r['Mufredat_AKTS'] for r in results
        if r['Durum'] == 'Devam Ediyor' and r.get('Ingilizce', False)
    )
    ingilizce_toplam_akts = ingilizce_basarili_akts + ingilizce_devam_akts
    ingilizce_toplam_mufredat = sum(
        r['Mufredat_AKTS'] for r in results
        if r.get('Ingilizce', False)
    )
    toplam_aktif_akts = basarili_akts + sum(
        r['Mufredat_AKTS'] for r in results if r['Durum'] == 'Devam Ediyor'
    )
    ingilizce_oran = round(
        (ingilizce_toplam_akts / toplam_aktif_akts * 100) if toplam_aktif_akts > 0 else 0, 1
    )
    ingilizce_yeterli = ingilizce_oran >= 30

    # Mezuniyet durumuna İngilizce kontrolü ekle
    if not ingilizce_yeterli and 'Sağlanıyor' in mezuniyet:
        mezuniyet = f"❌ İngilizce Ders Oranı Yetersiz (%{ingilizce_oran} < %30)"

    return {
        'toplam_mufredat_akts': toplam_mufredat_akts,
        'basarili_akts': basarili_akts,
        'eksik_ders_sayisi': eksik,
        'basarisiz_ders_sayisi': basarisiz,
        'supheli_sayisi': supheli,
        'devam_eden_sayisi': devam_eden,
        'basarili_ders_sayisi': basarili,
        'agno': agno,
        'mezuniyet_durumu': mezuniyet,
        'toplam_ders': len(results),
        'ingilizce_basarili_akts': ingilizce_basarili_akts,
        'ingilizce_devam_akts': ingilizce_devam_akts,
        'ingilizce_toplam_akts': ingilizce_toplam_akts,
        'ingilizce_toplam_mufredat': ingilizce_toplam_mufredat,
        'ingilizce_oran': ingilizce_oran,
        'ingilizce_yeterli': ingilizce_yeterli,
    }
