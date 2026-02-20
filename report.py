# -*- coding: utf-8 -*-
"""
PDF Rapor Modülü
================
FPDF2 kullanarak A4 boyutunda mezuniyet kontrol raporu oluşturur.
Türkçe karakter desteği için DejaVu fontu kullanır.
"""

import os
import io
from datetime import datetime
from fpdf import FPDF


class UnicodePDF(FPDF):
    """Türkçe karakter destekli PDF sınıfı."""

    def __init__(self):
        super().__init__()
        # Sistem fontlarından birini bul veya varsayılan kullan
        self.add_page()
        # DejaVu fontunu dene, yoksa Helvetica kullan
        try:
            # fpdf2 ile built-in unicode desteği
            self.add_font('DejaVu', '', os.path.join(os.path.dirname(__file__), 'fonts', 'DejaVuSans.ttf'), uni=True)
            self.add_font('DejaVu', 'B', os.path.join(os.path.dirname(__file__), 'fonts', 'DejaVuSans-Bold.ttf'), uni=True)
            self.font_family_name = 'DejaVu'
        except Exception:
            self.font_family_name = 'Helvetica'

    def header(self):
        """Sayfa başlığı."""
        self.set_font(self.font_family_name, 'B', 14)
        self.cell(0, 10, 'Trakya Universitesi', 0, 1, 'C')
        self.set_font(self.font_family_name, '', 11)
        self.cell(0, 7, 'Makina Muhendisligi Bolumu', 0, 1, 'C')
        self.cell(0, 7, 'Mezuniyet Kontrol Raporu', 0, 1, 'C')
        self.set_font(self.font_family_name, '', 9)
        self.cell(0, 5, f'Rapor Tarihi: {datetime.now().strftime("%d.%m.%Y %H:%M")}', 0, 1, 'C')
        self.ln(5)
        # Çizgi
        self.set_draw_color(0, 102, 204)
        self.set_line_width(0.5)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(5)

    def footer(self):
        """Sayfa alt bilgisi."""
        self.set_y(-15)
        self.set_font(self.font_family_name, '', 8)
        self.set_text_color(128)
        self.cell(0, 10, f'Sayfa {self.page_no()}/{{nb}}', 0, 0, 'C')


def safe_text(text: str) -> str:
    """Türkçe karakterleri ASCII-safe versiyonlarına çevirir (Helvetica fallback için)."""
    replacements = {
        'ç': 'c', 'Ç': 'C', 'ğ': 'g', 'Ğ': 'G',
        'ı': 'i', 'İ': 'I', 'ö': 'o', 'Ö': 'O',
        'ş': 's', 'Ş': 'S', 'ü': 'u', 'Ü': 'U',
        '✅': '[OK]', '❌': '[X]', '⚠️': '[!]', '🔵': '[~]'
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    return text


def generate_report(results: list, summary: dict, mufredat_adi: str = "") -> bytes:
    """
    Eşleştirme sonuçlarından PDF rapor oluşturur.

    Parameters:
        results: match_courses() çıktısı (list of dict)
        summary: generate_summary() çıktısı (dict)
        mufredat_adi: Seçilen müfredatın adı

    Returns:
        bytes: PDF dosyasının byte içeriği
    """
    pdf = FPDF()
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=20)

    # ===== BAŞLIK =====
    pdf.set_font('Helvetica', 'B', 16)
    pdf.cell(0, 10, 'Trakya Universitesi', 0, 1, 'C')
    pdf.set_font('Helvetica', 'B', 12)
    pdf.cell(0, 7, 'Makina Muhendisligi Bolumu', 0, 1, 'C')
    pdf.cell(0, 7, 'Mezuniyet Kontrol Raporu', 0, 1, 'C')
    pdf.set_font('Helvetica', '', 9)
    pdf.cell(0, 5, f'Rapor Tarihi: {datetime.now().strftime("%d.%m.%Y %H:%M")}', 0, 1, 'C')
    if mufredat_adi:
        pdf.cell(0, 5, f'Mufredat: {safe_text(mufredat_adi)}', 0, 1, 'C')
    pdf.ln(3)

    # Ayırıcı çizgi
    pdf.set_draw_color(0, 102, 204)
    pdf.set_line_width(0.5)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)

    # ===== ÖZET BİLGİLER =====
    pdf.set_font('Helvetica', 'B', 12)
    pdf.cell(0, 8, 'Genel Ozet', 0, 1)
    pdf.ln(2)

    pdf.set_font('Helvetica', '', 10)
    ozet_items = [
        ('Toplam Mufredat AKTS', str(summary['toplam_mufredat_akts'])),
        ('Basarili AKTS', str(summary['basarili_akts'])),
        ('AGNO', str(summary['agno'])),
        ('Toplam Ders Sayisi', str(summary['toplam_ders'])),
        ('Basarili Ders', str(summary['basarili_ders_sayisi'])),
        ('Basarisiz Ders', str(summary['basarisiz_ders_sayisi'])),
        ('Eksik Ders', str(summary['eksik_ders_sayisi'])),
        ('Devam Eden Ders', str(summary['devam_eden_sayisi'])),
        ('Supheli Eslesme', str(summary['supheli_sayisi'])),
    ]

    for label, value in ozet_items:
        pdf.set_font('Helvetica', 'B', 10)
        pdf.cell(60, 6, f'{label}:', 0, 0)
        pdf.set_font('Helvetica', '', 10)
        pdf.cell(0, 6, value, 0, 1)

    pdf.ln(3)
    pdf.set_font('Helvetica', 'B', 11)
    mezuniyet_text = safe_text(summary['mezuniyet_durumu'])
    pdf.cell(0, 8, f'Mezuniyet Durumu: {mezuniyet_text}', 0, 1)
    pdf.ln(3)

    # ===== İNGİLİZCE DERS ORANI =====
    ing_oran = summary.get('ingilizce_oran', 0)
    ing_akts = summary.get('ingilizce_toplam_akts', summary.get('ingilizce_basarili_akts', 0))
    ing_yeterli = summary.get('ingilizce_yeterli', False)
    basarili_akts = summary.get('basarili_akts', 0)

    pdf.set_font('Helvetica', 'B', 11)
    pdf.cell(0, 8, 'Ingilizce Ders Orani', 0, 1)
    pdf.set_font('Helvetica', '', 10)
    pdf.cell(60, 6, 'Ingilizce AKTS (Bas.+Devam):', 0, 0)
    pdf.cell(0, 6, f'{int(ing_akts)}', 0, 1)
    pdf.cell(60, 6, 'Ingilizce Oran:', 0, 0)
    pdf.cell(0, 6, f'%{ing_oran}', 0, 1)
    pdf.set_font('Helvetica', 'B', 10)
    if ing_yeterli:
        pdf.set_text_color(0, 128, 0)
        pdf.cell(0, 6, 'Durum: Yeterli (>= %30)', 0, 1)
    else:
        gereken = int(basarili_akts * 0.30)
        eksik = max(0, gereken - int(ing_akts))
        pdf.set_text_color(200, 0, 0)
        pdf.cell(0, 6, f'Durum: Yetersiz (< %30) - Eksik: ~{eksik} AKTS', 0, 1)
    pdf.set_text_color(0, 0, 0)
    pdf.ln(3)

    # Ayırıcı çizgi
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)

    # ===== DERS DETAYLARI =====
    # Dönemlere göre grupla
    donemler = {}
    for r in results:
        d = r['Donem']
        if d not in donemler:
            donemler[d] = []
        donemler[d].append(r)

    for donem in sorted(donemler.keys()):
        dersler = donemler[donem]

        # Dönem başlığı
        pdf.set_font('Helvetica', 'B', 11)
        donem_text = f'{donem}. Donem' if isinstance(donem, (int, float)) else safe_text(str(donem))
        pdf.set_fill_color(230, 240, 255)
        pdf.cell(0, 8, f'  {donem_text}', 0, 1, fill=True)
        pdf.ln(2)

        # Tablo başlığı
        col_widths = [25, 65, 20, 15, 45, 20]
        headers = ['Ders Kodu', 'Ders Adi', 'AKTS', 'Not', 'Durum', 'Sonuc']

        pdf.set_font('Helvetica', 'B', 8)
        pdf.set_fill_color(0, 102, 204)
        pdf.set_text_color(255, 255, 255)
        for i, h in enumerate(headers):
            pdf.cell(col_widths[i], 6, h, 1, 0, 'C', fill=True)
        pdf.ln()
        pdf.set_text_color(0, 0, 0)

        # Ders satırları
        for r in dersler:
            pdf.set_font('Helvetica', '', 7)

            # Arka plan rengi duruma göre
            if r['Durum'] == 'Basarisiz' or r['Durum'] == 'Başarısız':
                pdf.set_fill_color(255, 220, 220)
                fill = True
            elif r['Durum'] == 'Eksik':
                pdf.set_fill_color(255, 240, 200)
                fill = True
            elif r['Durum'] in ('Şüpheli Eşleşme', 'Supheli Eslesme'):
                pdf.set_fill_color(255, 255, 200)
                fill = True
            elif r['Durum'] == 'Devam Ediyor':
                pdf.set_fill_color(220, 235, 255)
                fill = True
            else:
                pdf.set_fill_color(220, 255, 220)
                fill = True

            ders_kodu = safe_text(str(r['Mufredat_Kodu']))[:15]
            ders_adi = safe_text(str(r['Mufredat_Adi']))
            if r.get('Ingilizce', False):
                ders_adi = ders_adi[:30] + ' (EN)'
            else:
                ders_adi = ders_adi[:35]
            akts = str(int(r['Mufredat_AKTS'])) if r['Mufredat_AKTS'] == int(r['Mufredat_AKTS']) else str(r['Mufredat_AKTS'])
            notu = safe_text(str(r.get('Transkript_Notu', '')))
            durum = safe_text(str(r['Durum']))[:20]
            sonuc = safe_text(str(r['Ikon']))

            pdf.cell(col_widths[0], 5, ders_kodu, 1, 0, 'L', fill)
            pdf.cell(col_widths[1], 5, ders_adi, 1, 0, 'L', fill)
            pdf.cell(col_widths[2], 5, akts, 1, 0, 'C', fill)
            pdf.cell(col_widths[3], 5, notu, 1, 0, 'C', fill)
            pdf.cell(col_widths[4], 5, durum, 1, 0, 'C', fill)
            pdf.cell(col_widths[5], 5, sonuc, 1, 0, 'C', fill)
            pdf.ln()

            # Eşleşen transkript dersi bilgisi (varsa ve farklıysa)
            if r['Transkript_Adi'] and r['Transkript_Adi'] != r['Mufredat_Adi']:
                pdf.set_font('Helvetica', 'I', 6)
                pdf.set_text_color(100, 100, 100)
                tr_text = f"  -> Transkript: {safe_text(r['Transkript_Kodu'])} {safe_text(r['Transkript_Adi'])}"
                pdf.cell(sum(col_widths), 4, tr_text, 0, 1)
                pdf.set_text_color(0, 0, 0)

        pdf.ln(3)

    # ===== EKSİK DERSLER LİSTESİ =====
    eksik_dersler = [r for r in results if r['Durum'] == 'Eksik']
    if eksik_dersler:
        pdf.ln(5)
        pdf.set_font('Helvetica', 'B', 12)
        pdf.set_text_color(200, 0, 0)
        pdf.cell(0, 8, 'Eksik Dersler', 0, 1)
        pdf.set_text_color(0, 0, 0)
        pdf.set_font('Helvetica', '', 9)
        for r in eksik_dersler:
            pdf.cell(0, 5, f"  - {safe_text(r['Mufredat_Kodu'])} {safe_text(r['Mufredat_Adi'])} ({r['Mufredat_AKTS']} AKTS)", 0, 1)

    # ===== BAŞARISIZ DERSLER =====
    basarisiz_dersler = [r for r in results if r['Durum'] == 'Başarısız']
    if basarisiz_dersler:
        pdf.ln(5)
        pdf.set_font('Helvetica', 'B', 12)
        pdf.set_text_color(200, 0, 0)
        pdf.cell(0, 8, 'Basarisiz Dersler', 0, 1)
        pdf.set_text_color(0, 0, 0)
        pdf.set_font('Helvetica', '', 9)
        for r in basarisiz_dersler:
            pdf.cell(0, 5,
                f"  - {safe_text(r['Mufredat_Kodu'])} {safe_text(r['Mufredat_Adi'])} "
                f"(Not: {safe_text(r['Transkript_Notu'])})", 0, 1)

    # PDF çıktısını byte olarak döndür
    return bytes(pdf.output())
