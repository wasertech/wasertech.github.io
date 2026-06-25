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
        self.set_auto_page_break(auto=True, margin=5)
        self.add_font('DejaVuSans', '', 'static/fonts/DejaVuSans.ttf')
        self.add_font('DejaVuSans', 'B', 'static/fonts/DejaVuSans-Bold.ttf')
        self.add_font('DejaVuSans', 'I', 'static/fonts/DejaVuSans-Oblique.ttf')
        self.add_font('DejaVuSans', 'BI', 'static/fonts/DejaVuSans-BoldOblique.ttf')

    def draw_line(self, x_start, x_end, y_pos):
        self.set_line_width(0.1)
        self.set_draw_color(180, 180, 180)
        self.line(x_start, y_pos, x_end, y_pos)
        self.set_draw_color(0, 0, 0)

    def print_section_header(self, text, width=0, margin_top=1.8, x_pos=15):
        self.set_x(x_pos)
        if margin_top > 0: self.ln(margin_top)
        self.set_x(x_pos)
        self.set_font('DejaVuSans', 'B', 9.2)
        self.set_text_color(60, 60, 60)
        actual_width = width if width > 0 else (210 - 15 - x_pos)
        self.cell(actual_width, 4.5, text.upper(), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.draw_line(x_pos, x_pos + actual_width, self.get_y() - 0.5)
        self.ln(1.0) 
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
    pdf.set_margins(12, 10, 12)
    content_width = 186

    # --- Header ---
    pdf.set_font('DejaVuSans', 'B', 16)
    pdf.cell(0, 7, 'DANNY WASER', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    
    pdf.set_font('DejaVuSans', 'B', 9.5)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 4, "AI ENGINEER & FULL-STACK DEVELOPER", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    
    pdf.set_font('DejaVuSans', '', 7.5)
    pdf.set_text_color(0, 0, 0)
    birth_date_str = data['contact'].get('birthDate')
    age_str = ''
    if birth_date_str:
        birth_date = datetime.date.fromisoformat(birth_date_str)
        today = datetime.date.today()
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        age_str = f"{'YEARS OLD' if lang == 'en' else 'ANS'}"
        info = f"{'SWISS CITIZEN' if lang == 'en' else 'CITOYEN SUISSE'} | {age} {age_str} | Lausanne, CH"
    else:
        info = f"{'SWISS CITIZEN' if lang == 'en' else 'CITOYEN SUISSE'} | Lausanne, CH"
    pdf.cell(0, 3.5, info, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    
    # Links
    links = []
    if data['contact'].get('email'): links.append((data['contact']['email'], f"mailto:{data['contact']['email']}"))
    if data['contact'].get('phone'): links.append((data['contact']['phone'], f"tel:{data['contact']['phone']}"))
    if data['contact'].get('website'): links.append(('waser.tech', data['contact']['website']))
    if data['contact'].get('linkedin'): links.append(('LinkedIn', data['contact']['linkedin']))
    if data['contact'].get('github'): links.append(('GitHub', data['contact']['github']))

    pdf.set_font('DejaVuSans', '', 7.5)
    for i, (text, url) in enumerate(links):
        pdf.set_text_color(0, 0, 150)
        pdf.write(3.5, text, url)
        pdf.set_text_color(0, 0, 0)
        if i < len(links) - 1: pdf.write(3.5, ' | ')
    pdf.ln(4.5)

    # Photo
    img_path = "static/images/portrait_thumb.png"
    crop_and_resize_image('static/images/portrait.webp', img_path, target_width_mm=22)
    if os.path.exists(img_path): pdf.image(img_path, x=175, y=10, w=22)

    # --- Profile ---
    pdf.print_section_header(data['sections']['profile'][lang], margin_top=0.5)
    pdf.set_font('DejaVuSans', '', 9)
    pdf.multi_cell(0, 4, data['profile'][lang]['content'].strip())

    # --- Professional Experience ---
    pdf.print_section_header(data['sections']['professional_experience'][lang], margin_top=1.8) 
    for exp in sorted(data['experiences'], key=date_key, reverse=True):
        pdf.set_font('DejaVuSans', 'B', 9.5)
        pdf.cell(145, 4.5, exp[lang]['title'])
        pdf.set_font('DejaVuSans', 'I', 8.5)
        pdf.cell(35, 4.5, exp['date'], new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='R')
        
        pdf.set_font('DejaVuSans', 'B', 8.5)
        pdf.set_text_color(80, 80, 80)
        pdf.cell(0, 3.8, exp[lang]['company'], new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_text_color(0, 0, 0)
        
        for line in exp[lang]['details'].strip().split('\n'):
            line = line.strip()
            if not line: continue
            if line.startswith('- '): line = line[2:]
            pdf.set_x(18)
            pdf.set_font('DejaVuSans', '', 8.8)
            pdf.write(3.5, '• ') 
            orig_l_margin = pdf.l_margin
            pdf.set_left_margin(21)
            parts = re.split(r'(\[.*?\]\(.*?\))', line)
            for part in parts:
                match = re.match(r'\[(.*?)\]\((.*?)\)', part)
                if match:
                    pdf.set_text_color(0, 0, 150)
                    pdf.write(3.5, match.group(1), match.group(2))
                    pdf.set_text_color(0, 0, 0)
                else: pdf.write(3.5, part)
            pdf.ln(3.5)
            pdf.set_left_margin(orig_l_margin)
        pdf.ln(0.6)

    # --- Key Projects ---
    pdf.print_section_header(data['sections']['software'][lang] if 'software' in data['sections'] else "KEY PROJECTS", margin_top=1.8) 
    for project in data['portfolio']:
        if not project.get('pdf_include', False): continue
        pdf.set_font('DejaVuSans', 'B', 8.8)
        pdf.set_text_color(0, 0, 150)
        pdf.write(4.0, project['name'], project['url']) 
        pdf.set_text_color(0, 0, 0)
        pdf.set_font('DejaVuSans', '', 8.8)
        pdf.write(4.0, f": {project[lang]['description']}") 
        pdf.ln(4.0) 

    # --- Skills ---
    pdf.print_section_header(data['sections']['technical_skills'][lang], margin_top=1.8) 
    grouped = {}
    for sk in data['skills']:
        cat = sk.get('category', 'Other')
        if cat not in grouped: grouped[cat] = []
        grouped[cat].append(sk[lang])
    
    for cat, sks in grouped.items():
        pdf.set_font('DejaVuSans', 'B', 8.8)
        pdf.write(4.0, f"{cat}: ") 
        pdf.set_font('DejaVuSans', '', 8.8)
        pdf.write(4.0, ', '.join(sks)) 
        pdf.ln(4.0) 

    # --- Education & Certification ---
    pdf.print_section_header(f"{data['sections']['certification'][lang]} / {data['sections']['education'][lang]}", margin_top=1.8) 
    pdf.set_font('DejaVuSans', '', 8.8)
    for cert in data['certifications']:
        pdf.write(4.0, "• ") 
        pdf.set_font('DejaVuSans', 'B', 8.8)
        pdf.set_text_color(0, 0, 150)
        pdf.write(4.0, cert[lang]['title'], cert.get('url', ''))
        pdf.set_text_color(0, 0, 0)
        pdf.set_font('DejaVuSans', 'I', 8.8)
        pdf.write(4.0, f" ({cert[lang]['issuer']}, {cert['start_date']}-{cert['end_date']})")
        pdf.ln(4.0)
    
    for edu in data['education']:
        if not edu.get('pdf_include', True): continue
        pdf.set_font('DejaVuSans', '', 8.8)
        pdf.write(4.0, f"• {edu[lang]['title']} ")
        pdf.set_font('DejaVuSans', 'I', 8.8)
        pdf.write(4.0, f"({edu[lang]['institution']}, {edu['date']})")
        pdf.ln(4.0)

    # --- Languages ---
    pdf.print_section_header(data['sections']['languages'][lang], margin_top=2.5) 
    pdf.set_font('DejaVuSans', '', 9)
    pdf.cell(0, 4.2, ', '.join([f"{l[lang]} ({l['level']})" for l in data['languages']]), new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # --- Personal Interests ---
    pdf.print_section_header((data['sections']['personal_interests'][lang] if 'personal_interests' in data['sections'] else "INTERESTS"), margin_top=2.5) 
    pdf.set_font('DejaVuSans', '', 9)
    pdf.multi_cell(0, 4, ', '.join([i[lang] for i in data['interests']]))

    # --- Page count enforcement: CV must fit on a single page ---
    if pdf.page_no() > 1:
        raise RuntimeError(f"CV ({lang.upper()}) exceeds 1 page ({pdf.page_no()} pages) — reduce content!")

    pdf.output(f"static/CV_{lang.upper()}.pdf")

if __name__ == '__main__':
    generate_pdf('en')
    generate_pdf('fr')
