from fpdf import FPDF
from fpdf.enums import XPos, YPos
from datetime import date
import os
import json
import sys
import toml

base_path = "/home/waser/Projets/curriculum/contacts"
font_path = "/home/waser/Projets/curriculum/static/fonts"
cv_data_path = "/home/waser/Projets/curriculum/static/cv_data.json"

# Load sender data
with open(cv_data_path, 'r') as f:
    cv_data = json.load(f)

contact = cv_data['contact']
sender_info = {
    "name": "Danny Waser",
    "title": "Data Scientist & AI Developer",
    "address": contact['address'],
    "phone": contact['phone'],
    "email": contact['email'],
    "website": "waser.tech"
}

today = date.today()
months_fr = {
    1: "janvier", 2: "février", 3: "mars", 4: "avril",
    5: "mai", 6: "juin", 7: "juillet", 8: "août",
    9: "septembre", 10: "octobre", 11: "novembre", 12: "décembre"
}
months_en = {
    1: "January", 2: "February", 3: "March", 4: "April",
    5: "May", 6: "June", 7: "July", 8: "August",
    9: "September", 10: "October", 11: "November", 12: "December"
}
today_str_fr = f"{today.day} {months_fr[today.month]} {today.year}"
today_str_en = f"{today.day} {months_en[today.month]} {today.year}"

class LetterPDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)
        self.add_font("DejaVuSans", "", font_path + "/DejaVuSans.ttf")
        self.add_font("DejaVuSans", "B", font_path + "/DejaVuSans-Bold.ttf")
        self.add_font("DejaVuSans", "I", font_path + "/DejaVuSans-Oblique.ttf")
        self.set_margins(20, 15, 20)

    def add_sender(self, info):
        self.set_font("DejaVuSans", "B", 11)
        self.set_text_color(0, 0, 0)
        self.cell(0, 6, info["name"], new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        
        self.set_font("DejaVuSans", "", 9)
        self.set_text_color(80, 80, 80)
        self.cell(0, 5, info["title"], new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.cell(0, 5, info["address"], new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.cell(0, 5, info["phone"], new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        
        self.set_text_color(60, 60, 180)
        self.cell(0, 5, info["email"], new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.cell(0, 5, info["website"], new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_text_color(0, 0, 0)

    def add_date(self, date_str, lang="fr"):
        self.set_font("DejaVuSans", "", 11)
        self.set_y(15) # Top margin
        if lang == "en":
            self.cell(0, 6, "Lausanne, " + date_str, align="R", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        else:
            self.cell(0, 6, "Lausanne, le " + date_str, align="R", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    def add_recipient(self, lines):
        self.set_y(42) # Position for recipient block
        self.set_font("DejaVuSans", "", 11)
        # Move to the right for windowed envelopes
        for line in lines:
            self.set_x(110)
            self.multi_cell(80, 5.5, line)

    def add_subject(self, title, lang="fr"):
        self.set_y(80)
        self.set_font("DejaVuSans", "B", 11)
        if lang == "en":
            self.multi_cell(0, 5.5, "Subject: Application for " + title)
        else:
            self.multi_cell(0, 5.5, "Objet : Candidature au poste de " + title)
        
        # Horizontal line
        self.ln(1)
        self.set_draw_color(200, 200, 200)
        self.set_line_width(0.2)
        self.line(20, self.get_y(), 190, self.get_y())
        self.ln(6)

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 gen_letters.py <path_to_contact_toml_1> [path_to_contact_toml_2 ...]")
        print("Or:    python3 gen_letters.py <directory_containing_contact_toml>")
        sys.exit(1)

    toml_paths = sys.argv[1:]
    resolved_paths = []
    
    for p in toml_paths:
        if os.path.isdir(p):
            toml_file = os.path.join(p, "contact.toml")
            if os.path.exists(toml_file):
                resolved_paths.append(toml_file)
            else:
                print(f"Error: Directory '{p}' does not contain contact.toml")
                sys.exit(1)
        elif os.path.isfile(p):
            resolved_paths.append(p)
        else:
            print(f"Error: '{p}' is not a valid file or directory")
            sys.exit(1)

    for toml_path in resolved_paths:
        try:
            data = toml.load(toml_path)
        except Exception as e:
            print(f"Error reading '{toml_path}': {e}")
            continue

        contact_info = data.get('contact', {})
        cover_letter_info = data.get('cover_letter', {})

        if not contact_info or not cover_letter_info:
            print(f"Error: '{toml_path}' must contain [contact] and [cover_letter] sections.")
            continue

        # Build recipient lines
        company_lines = []
        if contact_info.get('entreprise'):
            company_lines.append(contact_info['entreprise'])
        if contact_info.get('personne_contactee'):
            company_lines.append(contact_info['personne_contactee'])
        if contact_info.get('case_postale'):
            company_lines.append(contact_info['case_postale'])

        street_line = ""
        if contact_info.get('rue'):
            street_line += contact_info['rue']
        if contact_info.get('numero'):
            if street_line:
                street_line += " "
            street_line += str(contact_info['numero'])
        if street_line:
            company_lines.append(street_line)

        npa_lieu = ""
        if contact_info.get('npa'):
            npa_lieu += str(contact_info['npa'])
        if contact_info.get('lieu'):
            if npa_lieu:
                npa_lieu += " "
            npa_lieu += contact_info['lieu']
        if npa_lieu:
            company_lines.append(npa_lieu)

        pays = contact_info.get('pays', '')
        if pays and pays.lower() not in ["suisse", "switzerland", "ch"]:
            company_lines.append(pays)

        title = contact_info.get('poste', 'AI Developer')
        body_paras = cover_letter_info.get('body', [])
        lang = cover_letter_info.get('langue', 'fr')

        dir_path = os.path.dirname(toml_path)
        pdf_path = os.path.join(dir_path, "COVER_LETTER.pdf")

        pdf = LetterPDF()
        pdf.add_page()

        # === DATE ===
        today_str = today_str_en if lang == "en" else today_str_fr
        pdf.add_date(today_str, lang=lang)

        # === SENDER ===
        pdf.set_y(15)
        pdf.add_sender(sender_info)

        # === RECIPIENT ===
        pdf.add_recipient(company_lines)

        # === SUBJECT ===
        pdf.add_subject(title, lang=lang)

        # === SALUTATION ===
        pdf.set_font("DejaVuSans", "", 11)
        salutation = "Dear Sir or Madam," if lang == "en" else "Madame, Monsieur,"
        pdf.cell(0, 8, salutation, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(2)

        # === BODY (JUSTIFIED) ===
        for para in body_paras:
            pdf.multi_cell(0, 5.5, para.strip(), align="J")
            pdf.ln(2.5)

        # === CLOSING ===
        pdf.ln(2)
        closing = "Sincerely," if lang == "en" else "Je vous prie d'agréer, Madame, Monsieur, l'expression de mes salutations distinguées."
        pdf.multi_cell(0, 5.5, closing)

        # === SIGNATURE ===
        pdf.ln(5)
        pdf.set_font("DejaVuSans", "", 11)
        pdf.cell(0, 7, "Danny Waser", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        try:
            pdf.output(pdf_path)
            print(f"[OK] Generated {pdf_path}")
        except Exception as e:
            print(f"Error generating PDF '{pdf_path}': {e}")

if __name__ == "__main__":
    main()
