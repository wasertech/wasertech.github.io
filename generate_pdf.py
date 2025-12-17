import json
from fpdf import FPDF
import os
import datetime
from PIL import Image
import re

class PDF(FPDF):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_auto_page_break(auto=False, margin=0)
        self.add_font('DejaVuSans', '', 'static/fonts/DejaVuSans.ttf', uni=True)
        self.add_font('DejaVuSans', 'B', 'static/fonts/DejaVuSans-Bold.ttf', uni=True)
        self.add_font('DejaVuSans', 'I', 'static/fonts/DejaVuSans-Oblique.ttf', uni=True)
        self.add_font('DejaVuSans', 'BI', 'static/fonts/DejaVuSans-BoldOblique.ttf', uni=True)

    def draw_line(self, y_pos):
        self.set_line_width(0.4)
        self.line(15, y_pos, 210 - 15, y_pos) # Full page width, with margins

    def print_section_header(self, x, y, text, font_size=12, margin_bottom=5):
        self.set_xy(x, y)
        self.set_font('DejaVuSans', 'B', font_size)
        self.cell(0, 5, text.upper(), new_x='LMARGIN', new_y='NEXT')
        return self.get_y() + margin_bottom

    def print_text_block(self, x, y, width, text, font_size=9, line_height=4, style='', margin_bottom=3):
        self.set_xy(x, y)
        self.set_font('DejaVuSans', style, font_size)
        self.multi_cell(width, line_height, text)
        return self.get_y() + margin_bottom

def crop_and_resize_image(image_path, output_path, target_width_mm=40, dpi=300):
    img = Image.open(image_path)
    width, height = img.size
    
    # Calculate target pixel size
    target_pixel_width = int(target_width_mm / 25.4 * dpi)
    size = (target_pixel_width, target_pixel_width) # Square image

    # Crop the image to a square from the center, with an upward shift
    new_edge = min(width, height)
    left = (width - new_edge)/2
    
    # Shift the crop up. The "- height * 0.15" will move the crop window up.
    top_offset = height * 0.15 
    top = (height - new_edge)/2 - top_offset
    top = max(0, top) # Ensure we don't go out of bounds
    
    right = (width + new_edge)/2
    bottom = top + new_edge
    if bottom > height:
        bottom = height
        top = bottom - new_edge

    img = img.crop((left, top, right, bottom))
    
    # Resize to the desired size
    img = img.resize(size, Image.Resampling.LANCZOS)
    img.save(output_path)

def date_key(experience):
    date_str = experience['date'].split(' - ')[0]
    date_str = date_str.replace('.', '')
    return datetime.datetime.strptime(date_str, '%b %Y')

def generate_pdf(lang):
    with open('static/cv_data.json', 'r') as f:
        data = json.load(f)

    pdf = PDF(orientation='P', unit='mm', format='A4')
    pdf.add_page()

    # --- Header ---
    header_y = 10
    pdf.set_xy(15, header_y)
    pdf.set_font('DejaVuSans', 'B', 36)
    pdf.cell(0, 10, 'DANNY WASER', new_x='LMARGIN', new_y='NEXT')

    header_y = pdf.get_y()
    pdf.set_xy(15, header_y)
    pdf.set_font('DejaVuSans', '', 10)
    pdf.cell(0, 5, f"{'SWISS CITIZEN' if lang == 'en' else 'CITOYEN SUISSE'}    {'26 YEARS OLD' if lang == 'en' else '26 ANS'}", new_x='LMARGIN', new_y='NEXT')
    
    # Image needs to be placed after the text, but visually top right
    processed_image_path = "static/images/portrait_thumb.png"
    image_width_mm = 40 # This is the width in mm for the PDF
    image_dpi = 300 # DPI for rendering
    crop_and_resize_image('static/images/portrait.webp', processed_image_path, target_width_mm=image_width_mm, dpi=image_dpi)
    pdf.image(processed_image_path, x=155, y=10, w=image_width_mm)
    pdf.draw_line(55) # Move line below image

    # --- Columns Setup ---
    left_col_x = 15
    right_col_x = 85
    col_width_left = 65
    col_width_right = 110
    current_y_left = 60 # Starting Y for left column content
    current_y_right = 60 # Starting Y for right column content

    # --- Left Column Content ---
    # Profile
    current_y_left = pdf.print_section_header(left_col_x, current_y_left, data['sections']['profile'][lang])
    current_y_left = pdf.print_text_block(left_col_x, current_y_left, col_width_left, data['profile'][lang]['content'], margin_bottom=5)

    # Contact
    current_y_left = pdf.print_section_header(left_col_x, current_y_left, data['sections']['contact'][lang])
    contact_items = [
        data['contact']['address'],
        data['contact']['phone'],
        data['contact']['email'],
        data['contact']['website'],
        data['contact']['github'],
        data['contact']['gitlab'],
        data['contact']['linkedin']
    ]
    for item in contact_items:
        current_y_left = pdf.print_text_block(left_col_x, current_y_left, col_width_left, item, margin_bottom=0)
    current_y_left += 5 # Add extra margin after contact details

    # Technical Skills
    current_y_left = pdf.print_section_header(left_col_x, current_y_left, data['sections']['technical_skills'][lang])
    current_y_left = pdf.print_text_block(left_col_x, current_y_left, col_width_left, ', '.join([skill[lang] for skill in data['skills']]), margin_bottom=5)

    # Languages
    current_y_left = pdf.print_section_header(left_col_x, current_y_left, data['sections']['languages'][lang])
    for lang_item in data['languages']:
        current_y_left = pdf.print_text_block(left_col_x, current_y_left, col_width_left, f"- {lang_item[lang]} ({lang_item['level']})", margin_bottom=0)
    current_y_left += 5

    # Personal Interests
    current_y_left = pdf.print_section_header(left_col_x, current_y_left, data['sections']['personal_interests'][lang])
    current_y_left = pdf.print_text_block(left_col_x, current_y_left, col_width_left, ', '.join([interest[lang] for interest in data['interests']]), margin_bottom=5)
    
    # --- Right Column Content ---
    # Professional Experience
    current_y_right = pdf.print_section_header(right_col_x, current_y_right, data['sections']['professional_experience'][lang])
    for exp in sorted(data['experiences'], key=date_key, reverse=True):
        current_y_right = pdf.print_text_block(right_col_x, current_y_right, col_width_right, exp[lang]['title'], font_size=10, style='B', line_height=5)
        current_y_right = pdf.print_text_block(right_col_x, current_y_right, col_width_right, f"{exp[lang]['company']} | {exp['date']}", font_size=9, line_height=4, style='I', margin_bottom=2)
        
        pdf.set_xy(right_col_x, current_y_right)
        
        details = exp[lang]['details']
        
        if details.startswith('- '):
            details = details[2:]
        bullet_points = details.split('\n- ')
        
        for point in bullet_points:
            pdf.set_x(right_col_x)
            pdf.write(4, '• ')
            
            lines = point.split('\n')
            first_line = lines[0]
            rest_of_lines = '\n'.join(lines[1:])
            
            match = re.match(r'\[(.*?)\]\((.*?)\)', first_line)
            
            # Temporarily change left margin to avoid wrapping to page start
            pdf.set_left_margin(right_col_x + 4)
            
            if match:
                link_text = match.group(1)
                link_url = match.group(2)
                
                pdf.set_font('DejaVuSans', 'U', 9)
                pdf.set_text_color(0, 0, 255)
                pdf.write(4, link_text, link_url)
                pdf.set_font('DejaVuSans', '', 9)
                pdf.set_text_color(0, 0, 0)
            else:
                pdf.write(4, first_line)
            
            # Restore margins
            pdf.set_left_margin(15)
            pdf.ln(4)
            
            if rest_of_lines:
                pdf.set_x(right_col_x + 4)
                pdf.multi_cell(col_width_right - 4, 4, rest_of_lines)

        current_y_right = pdf.get_y() + 5

    # Certification
    current_y_right = pdf.print_section_header(right_col_x, current_y_right, data['sections']['certification'][lang])
    for cert in data['certifications']:
        current_y_right = pdf.print_text_block(right_col_x, current_y_right, col_width_right, cert[lang]['title'], font_size=10, style='B', line_height=5)
        current_y_right = pdf.print_text_block(right_col_x, current_y_right, col_width_right, f"{cert[lang]['issuer']} | {cert['start_date']} - {cert['end_date']}", font_size=9, line_height=4, style='I', margin_bottom=5)
        # Note: The certificate image is for the web, not printed in PDF

    pdf.output(f"static/CV_{lang.upper()}.pdf")
    print(f"static/CV_{lang.upper()}.pdf generated successfully.")

if __name__ == '__main__':
    generate_pdf('en')
    generate_pdf('fr')
