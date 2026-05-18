import json
from fpdf import FPDF
from fpdf.enums import XPos, YPos
import os
import datetime
from PIL import Image
import re

class PDF(FPDF):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_auto_page_break(auto=True, margin=10)
        self.add_font('DejaVuSans', '', 'static/fonts/DejaVuSans.ttf')
        self.add_font('DejaVuSans', 'B', 'static/fonts/DejaVuSans-Bold.ttf')
        self.add_font('DejaVuSans', 'I', 'static/fonts/DejaVuSans-Oblique.ttf')
        self.add_font('DejaVuSans', 'BI', 'static/fonts/DejaVuSans-BoldOblique.ttf')

    def draw_line(self, x_start, x_end, y_pos):
        self.set_line_width(0.1)
        self.set_draw_color(180, 180, 180)
        self.line(x_start, y_pos, x_end, y_pos)
        self.set_draw_color(0, 0, 0)

    def print_section_header(self, text, width=0, margin_top=2, x_pos=15):
        self.set_x(x_pos)
        if margin_top > 0: self.ln(margin_top)
        self.set_x(x_pos)
        self.set_font('DejaVuSans', 'B', 9.5)
        self.set_text_color(60, 60, 60)
        actual_width = width if width > 0 else (210 - 15 - x_pos)
        self.cell(actual_width, 5, text.upper(), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.draw_line(x_pos, x_pos + actual_width, self.get_y() - 0.5)
        self.ln(1.2) # Reduced from 1.5
        self.set_text_color(0, 0, 0)

def crop_and_resize_image(image_path, output_path, target_width_mm=25, dpi=300):
    if not os.path.exists(image_path): return
    img = Image.open(image_path)
    width, height = img.size
    target_pixel_width = int(target_width_mm / 25.4 * dpi)
    size = (target_pixel_width, target_pixel_width)
    new_edge = min(width, height)
    left = (width - new_edge)/2
    top = (height - new_edge)/2 - (height * 0.15)
    top = max(0, top)
    right = (width + new_edge)/2
    bottom = top + new_edge
    img = img.crop((left, top, right, bottom)).resize(size, Image.Resampling.LANCZOS)
    img.save(output_path)

def date_key(experience):
    date_str = experience['date'].split(' - ')[0].replace('.', '')
    for fmt in ('%b %Y', '%B %Y'):
        try: return datetime.datetime.strptime(date_str, fmt)
        except ValueError: continue
    return datetime.datetime.min

def generate_pdf(lang):
    with open('static/cv_data.json', 'r') as f:
        data = json.load(f)

    pdf = PDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_margins(15, 12, 15)
    content_width = 180

    # --- Header ---
    pdf.set_font('DejaVuSans', 'B', 18)
    pdf.cell(0, 8, 'DANNY WASER', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    
    pdf.set_font('DejaVuSans', 'B', 10)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 5, "AI ENGINEER & FULL-STACK DEVELOPER", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    
    pdf.set_font('DejaVuSans', '', 8)
    pdf.set_text_color(0, 0, 0)
    info = f"{'SWISS CITIZEN' if lang == 'en' else 'CITOYEN SUISSE'} | {'26 YEARS OLD' if lang == 'en' else '26 ANS'} | Lausanne, CH"
    pdf.cell(0, 4, info, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    
    # Links
    links = []
    if data['contact'].get('email'): links.append((data['contact']['email'], f"mailto:{data['contact']['email']}"))
    if data['contact'].get('phone'): links.append((data['contact']['phone'], f"tel:{data['contact']['phone']}"))
    if data['contact'].get('website'): links.append(('waser.tech', data['contact']['website']))
    if data['contact'].get('linkedin'): links.append(('LinkedIn', data['contact']['linkedin']))
    if data['contact'].get('github'): links.append(('GitHub', data['contact']['github']))

    pdf.set_font('DejaVuSans', '', 8)
    for i, (text, url) in enumerate(links):
        pdf.set_text_color(0, 0, 150)
        pdf.write(4, text, url)
        pdf.set_text_color(0, 0, 0)
        if i < len(links) - 1: pdf.write(4, ' | ')
    pdf.ln(5.5)

    # Photo
    img_path = "static/images/portrait_thumb.png"
    crop_and_resize_image('static/images/portrait.webp', img_path, target_width_mm=25)
    if os.path.exists(img_path): pdf.image(img_path, x=170, y=12, w=25)

    # --- Profile ---
    pdf.print_section_header(data['sections']['profile'][lang], margin_top=0.5)
    pdf.set_font('DejaVuSans', '', 9)
    pdf.multi_cell(0, 3.8, data['profile'][lang]['content'].strip())

    # --- Professional Experience ---
    pdf.print_section_header(data['sections']['professional_experience'][lang], margin_top=2) # Reduced from 3
    for exp in sorted(data['experiences'], key=date_key, reverse=True):
        pdf.set_font('DejaVuSans', 'B', 9.5)
        pdf.cell(140, 4.5, exp[lang]['title'])
        pdf.set_font('DejaVuSans', 'I', 8.5)
        pdf.cell(40, 4.5, exp['date'], new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='R')
        
        pdf.set_font('DejaVuSans', 'B', 8.5)
        pdf.set_text_color(80, 80, 80)
        pdf.cell(0, 4, exp[lang]['company'], new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_text_color(0, 0, 0)
        
        for line in exp[lang]['details'].strip().split('\n'):
            line = line.strip()
            if not line: continue
            if line.startswith('- '): line = line[2:]
            pdf.set_x(20)
            pdf.set_font('DejaVuSans', '', 9)
            pdf.write(3.5, '• ') # Reduced from 3.8
            orig_l_margin = pdf.l_margin
            pdf.set_left_margin(23)
            parts = re.split(r'(\[.*?\]\(.*?\))', line)
            for part in parts:
                match = re.match(r'\[(.*?)\]\((.*?)\)', part)
                if match:
                    pdf.set_text_color(0, 0, 150)
                    pdf.write(3.5, match.group(1), match.group(2))
                    pdf.set_text_color(0, 0, 0)
                else: pdf.write(3.5, part)
            pdf.ln(3.5) # Reduced from 3.8
            pdf.set_left_margin(orig_l_margin)
        pdf.ln(0.8) # Reduced from 1

    # --- Key Projects ---
    pdf.print_section_header(data['sections']['software'][lang] if 'software' in data['sections'] else "KEY PROJECTS", margin_top=2) # Reduced from 3
    for project in data['portfolio']:
        if not project.get('pdf_include', False): continue
        pdf.set_font('DejaVuSans', 'B', 9)
        pdf.set_text_color(0, 0, 150)
        pdf.write(4, project['name'], project['url']) # Reduced from 4.2
        pdf.set_text_color(0, 0, 0)
        pdf.set_font('DejaVuSans', '', 9)
        pdf.write(4, f": {project[lang]['description']}") # Reduced from 4.2
        pdf.ln(4.2) # Reduced from 4.5

    # --- Skills ---
    pdf.print_section_header(data['sections']['technical_skills'][lang], margin_top=2) # Reduced from 3
    grouped = {}
    for sk in data['skills']:
        cat = sk.get('category', 'Other')
        if cat not in grouped: grouped[cat] = []
        grouped[cat].append(sk[lang])
    
    for cat, sks in grouped.items():
        pdf.set_font('DejaVuSans', 'B', 9)
        pdf.write(4, f"{cat}: ") # Reduced from 4.2
        pdf.set_font('DejaVuSans', '', 9)
        pdf.write(4, ', '.join(sks)) # Reduced from 4.2
        pdf.ln(4.2) # Reduced from 4.5

    # --- Education & Certification ---
    pdf.print_section_header(f"{data['sections']['certification'][lang]} / {data['sections']['education'][lang]}", margin_top=2) # Reduced from 3
    pdf.set_font('DejaVuSans', '', 9)
    for cert in data['certifications']:
        pdf.write(4, "• ") # Reduced from 4.2
        pdf.set_font('DejaVuSans', 'B', 9)
        pdf.set_text_color(0, 0, 150)
        pdf.write(4, cert[lang]['title'], cert.get('url', ''))
        pdf.set_text_color(0, 0, 0)
        pdf.set_font('DejaVuSans', 'I', 9)
        pdf.write(4, f" ({cert[lang]['issuer']}, {cert['start_date']}-{cert['end_date']})")
        pdf.ln(4.2)
    
    for edu in data['education']:
        if not edu.get('pdf_include', True): continue
        pdf.set_font('DejaVuSans', '', 9)
        pdf.write(4, f"• {edu[lang]['title']} ")
        pdf.set_font('DejaVuSans', 'I', 9)
        pdf.write(4, f"({edu[lang]['institution']}, {edu['date']})")
        pdf.ln(4.2)

    # --- Languages ---
    pdf.print_section_header(data['sections']['languages'][lang], margin_top=2) # Reduced from 3
    pdf.set_font('DejaVuSans', '', 9)
    pdf.cell(0, 4.2, ', '.join([f"{l[lang]} ({l['level']})" for l in data['languages']]), new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # --- Personal Interests ---
    pdf.print_section_header((data['sections']['personal_interests'][lang] if 'personal_interests' in data['sections'] else "INTERESTS"), margin_top=2) # Reduced from 3
    pdf.set_font('DejaVuSans', '', 9)
    pdf.multi_cell(0, 4, ', '.join([i[lang] for i in data['interests']]))

    pdf.output(f"static/CV_{lang.upper()}.pdf")

if __name__ == '__main__':
    generate_pdf('en')
    generate_pdf('fr')
