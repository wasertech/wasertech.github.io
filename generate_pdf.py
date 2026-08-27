import json
from fpdf import FPDF
from fpdf.enums import XPos, YPos, MethodReturnValue
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

    def footer(self):
        """Footer: name + title left, page number right."""
        if self.page_no() == 1:
            return  # no footer on first page
        self.set_y(-12)
        self.set_font('DejaVuSans', '', 7.5)
        self.set_text_color(120, 120, 120)
        y = self.get_y()
        # Nom à gauche
        self.set_xy(self.l_margin, y)
        lang = getattr(self, 'lang', 'en')
        footer_titles = {
            'en': 'Danny Waser  |  AI/ML Engineer',
            'fr': 'Danny Waser  |  Ingénieur AI/ML',
        }
        self.cell(0, 5, footer_titles.get(lang, footer_titles['en']), new_x=XPos.RIGHT, new_y=YPos.TOP, align='L')
        # Numéro de page à droite, sur la MÊME ligne de base que le nom
        self.set_xy(self.w - self.r_margin - 12, y)
        self.cell(12, 5, f'{self.page_no()}', new_x=XPos.LMARGIN, new_y=YPos.TOP, align='R')
        self.set_text_color(0, 0, 0)

    def section_header(self, text, margin_top=4):
        """Section title with underline."""
        if margin_top > 0:
            self.ln(margin_top)
        self.set_font('DejaVuSans', 'B', 9.5)
        self.set_text_color(50, 50, 50)
        w = self.w - self.l_margin - self.r_margin
        self.set_draw_color(70, 70, 70)
        self.cell(w, 5, text.upper(), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.line(self.l_margin, self.get_y(), self.l_margin + w, self.get_y())
        self.ln(2)
        self.set_text_color(0, 0, 0)

    def write_line_with_links(self, text, x_start, font_size=8.5, leading=4):
        """Render text with [label](url) links in blue (like every other link).

        Continuation lines must wrap to the text indent (x_start+4), NOT to the
        global left margin - otherwise multi-line bullets misalign (see bug where
        bullets with links wrapped to x=14 while bullets without links wrapped to x=20).

        Manual word-level wrapping: a word or link label that does not fit on the
        current line is moved WHOLE to the next line. fpdf2's write() would split
        it mid-word (e.g. '#2205' -> '#22' + '05'), which is forbidden.
        """
        prev_lm = self.l_margin
        indent = x_start + 4
        max_x = self.w - self.r_margin
        self.set_left_margin(indent)
        self.set_x(x_start)
        self.set_font('DejaVuSans', '', font_size)
        self.cell(3, leading, '•')
        self.set_x(indent)
        parts = re.split(r'(\[[^\]]+\]\([^)]+\))', text.strip())
        # Build flat token list: [is_link, text, url, suffix]. Normal text is
        # split on spaces (spaces kept as their own tokens) so we can wrap
        # word by word.
        tokens = []
        for part in parts:
            if not part:
                continue
            m = re.match(r'\[([^\]]+)\]\(([^)]+)\)', part)
            if m:
                tokens.append([True, m.group(1), m.group(2), ''])
            else:
                tokens.extend([False, w, None, ''] for w in re.split(r'( +)', part) if w)
        # Post-process: never let a line start with ')' (or other closing
        # punctuation). (a) After a link, absorb trailing punctuation/space
        # tokens (e.g. ') : ') into the link token so the link + its closing
        # paren and colon move together as one unit. (b) A lone ')' token
        # elsewhere gets merged into the preceding word.
        i = 0
        while i < len(tokens):
            if tokens[i][0] is True:
                j = i + 1
                while j < len(tokens) and not tokens[j][0] and tokens[j][1] and all(c in ' ):,.;' for c in tokens[j][1]):
                    tokens[i][3] += tokens[j][1]
                    j += 1
                if j > i + 1:
                    del tokens[i+1:j]
            elif tokens[i][1] and tokens[i][1].startswith(')') and i > 0:
                prev = tokens[i-1]
                if prev[0] is True:
                    prev[3] += tokens[i][1]
                elif prev[1].strip():
                    prev[1] += tokens[i][1]
                else:
                    i += 1
                    continue
                del tokens[i]
                continue
            i += 1
        # Group consecutive non-link tokens into words+space units so we can
        # check the WHOLE next word before writing - fpdf2's write() with
        # wrapmode=WORD will split a word mid-way ('sur' -> 'su' + 'r') when
        # it sits at the right margin, and we must never let that happen.
        # Strategy: before writing each word, check if it fits; if not, ln()
        # first. write() then never receives text that crosses the margin.
        first = True
        i = 0
        while i < len(tokens):
            is_link, txt, url, suffix = tokens[i]
            if is_link:
                # Link label + trailing punctuation: must fit whole. Wrap
                # before if it doesn't.
                if not first and self.get_x() + self.get_string_width(txt) + self.get_string_width(suffix) > max_x:
                    self.ln(leading)
                self.set_text_color(0, 0, 150)
                self.write(leading, txt, url)
                self.set_text_color(0, 0, 0)
                if suffix:
                    self.write(leading, suffix)
                first = False
                i += 1
                continue
            # Non-link: collect consecutive text tokens (word + following spaces)
            chunk = ''
            while i < len(tokens) and not tokens[i][0]:
                chunk += tokens[i][1]
                i += 1
            if not chunk:
                continue
            # If the whole chunk doesn't fit, wrap before it.
            if not first and self.get_x() + self.get_string_width(chunk) > max_x:
                self.ln(leading)
            # Write the chunk; it fits so write() cannot split it.
            self.write(leading, chunk)
            first = False
        self.ln(leading)
        self.set_left_margin(prev_lm)
        self.set_x(prev_lm)

    def body_text(self, text, font_size=8.5, leading=3.9):
        """Render text with *italic* markers and [link](url) links."""
        self.set_font('DejaVuSans', '', font_size)
        for para in text.strip().split('\n\n'):
            # Split on *...* (italic) keeping links intact
            parts = re.split(r'(\*[^*]+\*)', para)
            for part in parts:
                if not part:
                    continue
                if part.startswith('*') and part.endswith('*') and len(part) > 2:
                    self.set_font('DejaVuSans', 'I', font_size)
                    self.write(leading, part[1:-1])
                    self.set_font('DejaVuSans', '', font_size)
                else:
                    self.write(leading, part)
            self.ln(leading)


def crop_and_resize_image(image_path, output_path, target_width_mm=25, dpi=300):
    if not os.path.exists(image_path):
        return
    img = Image.open(image_path)
    width, height = img.size
    target_pixel_width = int(target_width_mm / 25.4 * dpi)
    size = (target_pixel_width, target_pixel_width)
    new_edge = min(width, height)
    left = (width - new_edge) / 2
    top = (height - new_edge) / 2 - (height * 0.15)
    top = max(0, top)
    right = (width + new_edge) / 2
    bottom = top + new_edge
    img = img.crop((left, top, right, bottom)).resize(size, Image.Resampling.LANCZOS)
    img.save(output_path)


def date_key(experience):
    date_str = experience['date'].split(' à ')[0]
    for fmt in ('%m.%Y', '%b %Y', '%B %Y'):
        try:
            return datetime.datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    return datetime.datetime.min


# Output file names (user requirement 2026-08-27: CV_Danny_Waser_AI_ML_Engineer.pdf EN / equivalent FR)
OUTPUT_NAMES = {
    'en': 'CV_Danny_Waser_AI_ML_Engineer.pdf',
    'fr': 'CV_Danny_Waser_Ingenieur_AI_ML.pdf',
}

# Category localization FR -> EN for TECHNICAL SKILLS (page 1)
CATEGORY_EN = {
    'Administration systèmes': 'System Administration',
    'Applications serveur': 'Server Applications',
    'Base de données': 'Databases',
    'BI & Data science': 'BI & Data Science',
    'Bureautique / Gestion': 'Office & Management',
    'Interface de programmation (API)': 'Programming Interfaces (API)',
    'Langages informatiques': 'Programming Languages',
    'Matériel & Equipement': 'Hardware & Equipment',
    'Réseaux, protocoles & Télécommunications': 'Networks, Protocols & Telecom',
    'Sécurité': 'Security',
    'Test & Qualité': 'Testing & Quality',
    'Visioconférence': 'Video Conferencing',
    'Gouvernance': 'Governance',
    'Processus': 'Processes',
    'Projet': 'Projects',
    'Test': 'Testing',
    'Langues': 'Languages',
    'Web Scraping & Automatisation': 'Web Scraping & Automation',
    '3D & Game Development': '3D & Game Development',
    'Environnement de développement (EDI)': 'Development Environment (IDE)',
    'ERP/PGI': 'ERP/PMIS',
    'GED': 'Document Management (EDM)',
    'Modélisation': 'Modeling',
    'Sauvegarde & Stockage': 'Backup & Storage',
    'Business analyse': 'Business Analysis',
    'Référencement': 'SEO & Referencing',
}

# Professional competencies (e-CF nomenclature) localization FR -> EN
COMPETENCES_EN = {
    'Data Science & Analyse': {
        '__label__': 'Data Science & Analysis',
        'Exploration et préparation des données': ('Data exploration and preparation',
                                                   'multi-source collection, preparation, truthfulness checking, visualization'),
        'Analyses prescriptives et prédictives': ('Prescriptive and predictive analytics',
                                                  'machine learning, predictive models, algorithms, decision support'),
        'Gouvernance et conformité des données': ('Data governance and compliance',
                                                  'heterogeneous data, ethical aspects, personal data protection'),
        'Cycle de vie des données': ('Data lifecycle',
                                     'analysis tools, results interpretation, new data sources'),
    },
    'Développement & Architecture': {
        '__label__': 'Development & Architecture',
        'Conception et développement d\'applications': ('Application design and development',
                                                        'development, debugging, documentation, integration, commissioning'),
        'Conception de l\'architecture': ('Architecture design',
                                          'interoperability, scalability, security, vulnerability management'),
        'Conception des applications': ('Application design',
                                        'data structures, modeling languages, iterative approach'),
        'Déploiement de la solution': ('Solution deployment',
                                       'installation, securing, component interoperability, commissioning'),
        'Tests et conformité': ('Testing and compliance',
                                'test procedures, specification compliance, audit trail'),
        'Intégration des composants': ('Component integration',
                                       'configuration management, compatibility, system integrity'),
    },
    'Gestion & Innovation': {
        '__label__': 'Management & Innovation',
        'Gestion des projets et du portefeuille de projets': ('Project and portfolio management',
                                                              'planning, resources and budget, cost-delay optimization, delivery'),
        'Alignement stratégique métier': ('Strategic business alignment',
                                          'business needs, enterprise architecture, process efficiency, strategic decisions'),
        'Innovation': ('Innovation',
                       'creative solutions, new concepts, innovative mindset'),
        'Amélioration des processus': ('Process improvement',
                                       'continuous learning, competitiveness optimization, evidence-based recommendations'),
        'Gestion de la relation client': ('Customer relationship management',
                                          'multidisciplinary teams, communication, partners'),
        'Identification des besoins': ('Needs identification',
                                       'customer listening, business requirements, user-centered design'),
    },
}

AVAILABILITY = {
    'en': 'Availability: immediate',
    'fr': 'Disponibilité : immédiate',
}


def generate_pdf(lang):
    with open('static/cv_data.json', 'r') as f:
        data = json.load(f)

    pdf = PDF(orientation='P', unit='mm', format='A4')
    pdf.set_margins(14, 10, 14)
    pdf.lang = lang  # used by footer for localized title
    pdf.add_page()

    L = pdf.l_margin
    R = pdf.r_margin
    PW = pdf.w

    # ════════════════════════════════════════
    # HEADER
    # ════════════════════════════════════════

    # Photo
    img_path = 'static/images/portrait_thumb.png'
    crop_and_resize_image('static/images/portrait.webp', img_path, target_width_mm=20)
    if os.path.exists(img_path):
        pdf.image(img_path, x=PW - R - 20, y=12, w=20)

    # Name
    pdf.set_font('DejaVuSans', 'B', 18)
    pdf.cell(0, 8, 'DANNY WASER', new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # Title (localized)
    pdf.set_font('DejaVuSans', 'B', 9.5)
    pdf.set_text_color(100, 100, 100)
    titles = {
        'en': 'AI/ML ENGINEER  |  AI SYSTEMS, LLM & AUTOMATION',
        'fr': 'INGÉNIEUR AI/ML  |  SYSTÈMES AI, LLM & AUTOMATISATION',
    }
    pdf.cell(0, 4.5, titles.get(lang, titles['en']), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_text_color(0, 0, 0)

    # Contact
    pdf.set_font('DejaVuSans', '', 7.8)
    contact = data['contact']
    info_parts = [contact.get('phone', ''), contact.get('email', ''), 'Lausanne, CH']
    pdf.cell(0, 3.5, '  |  '.join(p for p in info_parts if p), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    # Disponibilité - coach: "Disponibilité" (cv_recommendations ligne 8)
    pdf.set_font('DejaVuSans', 'I', 7.5)
    pdf.cell(0, 3.5, AVAILABILITY.get(lang, AVAILABILITY['en']), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font('DejaVuSans', '', 7.8)

    # Links
    links = []
    if contact.get('github'):  links.append(('GitHub', contact['github']))
    if contact.get('linkedin'):  links.append(('LinkedIn', contact['linkedin']))
    if contact.get('huggingface'):  links.append(('HF', contact['huggingface']))
    if contact.get('website'):  links.append(('waser.tech', contact['website']))

    pdf.set_font('DejaVuSans', '', 7.8)
    for i, (text, url) in enumerate(links):
        pdf.set_text_color(0, 0, 150)
        pdf.write(3.5, text, url)
        pdf.set_text_color(0, 0, 0)
        if i < len(links) - 1:
            pdf.write(3.5, '  |  ')
    pdf.ln(4.5)

    # ════════════════════════════════════════
    # PROFILE
    # ════════════════════════════════════════
    pdf.section_header(data['sections']['profile'][lang], margin_top=0)
    pdf.body_text(data['profile'][lang]['content'].strip())

    # ════════════════════════════════════════
    # PROFESSIONAL COMPETENCIES - 5 domains (Lab4Tech), separate section
    # ════════════════════════════════════════
    competences = data.get('competences_pro', [])
    if competences:
        pdf.section_header(data['sections']['professional_competencies'][lang], margin_top=2.5)
        for dom in competences:
            comps = sorted(dom['competences'], key=lambda c: -c['niveau_max'])[:3]
            dom_en = COMPETENCES_EN.get(dom['nom'], {})
            # Nomenclature e-CF : termes exacts comme mots-clés (sans les codes A.1, D.4...)
            pdf.set_font('DejaVuSans', 'B', 7.2)
            dom_label = dom_en.get('__label__', dom['nom']) if lang == 'en' else dom['nom']
            pdf.multi_cell(PW - L - R, 3.0, dom_label.upper() + ':', align='L',
                           new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.set_font('DejaVuSans', '', 7.0)
            for c in comps:
                nom = c.get('nom', c.get('titre', ''))
                termes = c.get('termes', '')
                if lang == 'en' and nom in dom_en:
                    nom, termes = dom_en[nom]
                line = f"  •  {nom}" + (f" : {termes}" if termes else "")
                pdf.multi_cell(PW - L - R, 2.8, line, align='L',
                               new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.ln(0.3)

    # ════════════════════════════════════════
    # SKILLS - compact by category (page 1 RH)
    # ════════════════════════════════════════
    pdf.section_header(data['sections']['technical_skills'][lang], margin_top=3)

    grouped = {}
    for sk in data['skills']:
        cat = sk.get('category', 'Other')
        if cat not in grouped:
            grouped[cat] = []
        grouped[cat].append(sk[lang])

    # Ordre d'affichage des catégories (Lab4Tech + parcours)
    category_order = [
        # Techniques
        'Administration systèmes', 'Applications serveur', 'Base de données',
        'BI & Data science', 'Blockchain', 'Bureautique / Gestion', 'Cloud',
        'CMS', 'CRM', 'Data Science', 'Design Patterns', 'DevOps', 'Environnement de développement (EDI)',
        'ERP/PGI', 'Framework', 'GED', 'Machine Learning', 'Interface de programmation (API)',
        'ITSM & Services', 'Langages informatiques', 'Matériel & Equipement',
        'Modélisation', 'OS', 'Réseaux, protocoles & Télécommunications',
        'Sauvegarde & Stockage', 'Sécurité', 'Test & Qualité', 'Virtualisation',
        'Visioconférence', 'Web Service', 'Web Scraping & Automatisation',
        '3D & Game Development',
        # Méthodologiques
        'Business analyse', 'Gouvernance', 'Innovation', 'Processus', 'Projet',
        'Référencement', 'Test',
    ]

    # Build all blocks: (title, text)
    blocks = []
    for cat in category_order:
        if cat not in grouped:
            continue
        cat_display = CATEGORY_EN.get(cat, cat) if lang == 'en' else cat
        blocks.append((cat_display, ', '.join(grouped[cat])))

    # Rendu 2 colonnes équilibré - multi_cell uniquement (pas de cell)
    col_gap = 5
    col_w = (PW - L - R - col_gap) / 2
    y_bottom = 288
    y = [pdf.get_y(), pdf.get_y()]
    x = [L, L + col_w + col_gap]

    pdf.set_auto_page_break(auto=False)
    for title, text in blocks:
        # Mesure exacte de la hauteur (dry_run) - pas d'estimation approximative
        pdf.set_font('DejaVuSans', 'B', 7.6)
        pdf.set_left_margin(x[0])
        h_title = pdf.multi_cell(col_w, 3.4, title + ':', dry_run=True, output=MethodReturnValue.HEIGHT)
        pdf.set_font('DejaVuSans', '', 7.4)
        h_text = pdf.multi_cell(col_w, 3.1, text, dry_run=True, output=MethodReturnValue.HEIGHT)
        pdf.set_left_margin(L)
        h_est = h_title + h_text + 0.5
        c = 0 if y[0] <= y[1] else 1
        if y[c] + h_est > y_bottom:
            pdf.add_page()
            y = [pdf.get_y(), pdf.get_y()]
        pdf.set_xy(x[c], y[c])
        pdf.set_left_margin(x[c])
        pdf.set_font('DejaVuSans', 'B', 7.6)
        pdf.multi_cell(col_w, 3.4, title + ':', new_x=XPos.LEFT, new_y=YPos.NEXT)
        pdf.set_font('DejaVuSans', '', 7.4)
        pdf.set_x(x[c])
        pdf.multi_cell(col_w, 3.1, text)
        pdf.set_left_margin(L)
        y[c] = pdf.get_y() + 1.0
    pdf.set_auto_page_break(auto=True, margin=10)
    pdf.set_y(max(y))

    # ════════════════════════════════════════
    # CERTIFICATIONS - page 1, section dédiée
    # ════════════════════════════════════════
    certs = data.get('certifications', [])
    if certs:
        pdf.section_header(data['sections']['certifications'][lang], margin_top=3)
        for cert in certs:
            title = cert.get(lang, {}).get('title', '')
            issuer = cert.get(lang, {}).get('issuer', '')
            sd = cert.get('start_date', '')
            ed = cert.get('end_date', '')
            period = f"{sd} {'to' if lang == 'en' else 'à'} {ed}" if sd and ed and sd != ed else (sd or ed)
            url = cert.get('url', '')
            pdf.set_font('DejaVuSans', 'B', 8.5)
            if url:
                pdf.set_text_color(0, 0, 150)
                pdf.write(4, title, url)
                pdf.set_text_color(0, 0, 0)
            else:
                pdf.write(4, title)
            pdf.set_font('DejaVuSans', '', 8.3)
            extra = '  |  '.join(p for p in [issuer, period] if p)
            if extra:
                pdf.write(4, f"  ({extra})")
            pdf.ln(4)

    # ════════════════════════════════════════
    # LANGUAGES - page 1 (requis RH si EN/FR demandé)
    # ════════════════════════════════════════
    pdf.section_header(data['sections']['languages'][lang], margin_top=3)
    pdf.set_font('DejaVuSans', '', 8.5)
    lang_items = [f"{l[lang]} ({l['level']})" for l in data['languages']]
    pdf.cell(0, 4.2, '  |  '.join(lang_items), new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # ════════════════════════════════════════
    # PROFESSIONAL EXPERIENCE - page 2+ (Recruteur)
    # ════════════════════════════════════════
    pdf.add_page()
    pdf.section_header(data['sections']['professional_experience'][lang], margin_top=0)

    for exp in sorted(data['experiences'], key=date_key, reverse=True):
        # Company (left) + Date (right, numeric) - coach: société à gauche, date à droite
        pdf.set_font('DejaVuSans', 'B', 9.5)
        pdf.cell(120, 4.8, exp[lang]['company'])
        pdf.set_font('DejaVuSans', 'I', 8.3)
        exp_date = exp['date'].replace(' à ', ' to ') if lang == 'en' else exp['date']
        pdf.cell(PW - L - 120 - R, 4.8, exp_date,
                 new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='R')

        # Role / Title
        pdf.set_font('DejaVuSans', 'B', 8.5)
        pdf.set_text_color(90, 90, 90)
        pdf.cell(0, 3.8, exp[lang]['title'], new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_text_color(0, 0, 0)
        pdf.ln(1.5)

        # Bullet points
        for line in exp[lang]['details'].strip().split('\n'):
            line = line.strip()
            if not line:
                continue
            if line.startswith('- '):
                line = line[2:].strip()
            # Check if line has links
            if re.search(r'\[.+?\]\(.+?\)', line):
                pdf.write_line_with_links(line, L + 2)
            else:
                pdf.set_x(L + 2)
                pdf.set_font('DejaVuSans', '', 8.5)
                pdf.cell(3, 4, '•')
                pdf.set_x(L + 6)
                pdf.set_left_margin(L + 6)
                pdf.multi_cell(PW - L - R - 6, 4, line, align='J')
                pdf.set_left_margin(L)
        pdf.ln(2)

    # ════════════════════════════════════════
    # EDUCATION
    # ════════════════════════════════════════
    pdf.section_header(data['sections']['education'][lang], margin_top=3)
    for edu in data['education']:
        if not edu.get('pdf_include', True):
            continue
        pdf.set_font('DejaVuSans', '', 8.5)
        pdf.cell(3, 4, '•')
        pdf.set_font('DejaVuSans', 'B', 8.5)
        pdf.cell(0, 4, f"  {edu[lang]['title']}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_font('DejaVuSans', 'I', 8.3)
        edu_date = edu['date'].replace(' à ', ' to ') if lang == 'en' else edu['date']
        pdf.set_x(L + 7)
        pdf.cell(0, 3.5, f"{edu[lang]['institution']}  |  {edu_date}",
                 new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(1)

    # ════════════════════════════════════════
    # KEY PROJECTS - page 3 (tout en bas)
    # ════════════════════════════════════════
    pdf.add_page()
    pdf.section_header(data['sections']['portfolio'][lang], margin_top=0)
    for project in data['portfolio']:
        if not project.get('pdf_include', False):
            continue
        pdf.set_font('DejaVuSans', 'B', 8.5)
        pdf.set_text_color(0, 0, 150)
        pdf.write(4, project['name'], project['url'])
        pdf.set_text_color(0, 0, 0)
        pdf.set_font('DejaVuSans', '', 8.3)
        pdf.write(4, f"  |  {project[lang]['description']}")
        pdf.ln(4)
    pdf.ln(1)

    # ════════════════════════════════════════
    # OPEN SOURCE CONTRIBUTIONS
    # ════════════════════════════════════════
    pdf.section_header(data['sections']['contributions'][lang], margin_top=2)

    # Manual contributions
    for c in data['contributions']['manual']:
        if not c.get('pdf_include', True):
            continue
        pdf.set_font('DejaVuSans', 'B', 8.3)
        pdf.cell(3, 4, '•')
        url = c.get('url', '')
        if url:
            pdf.set_text_color(0, 0, 150)
            pdf.write(4, c.get('project', ''), url)
            pdf.set_text_color(0, 0, 0)
        else:
            pdf.write(4, c.get('project', ''))
        pdf.set_font('DejaVuSans', '', 8.3)
        # Title localized (fr for CV_FR, en for CV_EN), linked if title_url provided
        title = c.get(lang, {}).get('title', '') or c.get('en', {}).get('title', '')
        title_url = c.get('title_url', '')
        if title:
            pdf.ln(3.5)
            pdf.set_x(L + 7)
            pdf.set_font('DejaVuSans', 'I', 8)
            if title_url:
                pdf.set_text_color(0, 0, 150)
                pdf.write(3.5, title, title_url)
                pdf.set_text_color(0, 0, 0)
            else:
                pdf.write(3.5, title)
        pdf.ln(4)

    # GitHub contributions (all repos)
    for c in data['contributions']['github']:
        pdf.set_font('DejaVuSans', 'B', 8.3)
        pdf.cell(3, 4, '•')
        pdf.set_font('DejaVuSans', 'B', 8.3)
        pdf.set_text_color(0, 0, 150)
        name = c.get('project', '')
        url = c.get('url', '#')
        pdf.write(4, name, url)
        pdf.set_text_color(0, 0, 0)
        pr_count = c.get('pr_count', 0)
        stars = c.get('stars', 0)
        pdf.set_font('DejaVuSans', '', 8.3)
        pdf.write(4, f"  |  {pr_count} PR{'s' if pr_count > 1 else ''} ({stars:,} stars)")
        pdf.ln(3.8)

        # All PRs, sorted by size (largest first)
        prs = c.get('prs', [])
        for pr in prs:
            pdf.set_x(L + 7)
            pdf.set_font('DejaVuSans', 'I', 7.8)
            pdf.set_text_color(0, 0, 150)
            pr_title = pr.get('title', '')
            pr_url = pr.get('url', '#')
            # Strip unsupported glyphs (emoji, etc.) not in DejaVuSans
            pr_title = ''.join(ch for ch in pr_title if ord(ch) <= 0xFFFF)
            # Collapse double spaces left by stripped glyphs
            pr_title = ' '.join(pr_title.split())
            # Title, truncated to fit - leaving room for size indicator
            pdf.write(3.5, pr_title[:70], pr_url)
            pdf.set_text_color(0, 0, 0)
            # Size indicator (+add/-del)
            pr_size = pr.get('size', 0)
            if pr_size > 0:
                pdf.set_font('DejaVuSans', '', 7.8)
                pdf.write(3.5, f"  (+{pr.get('additions', 0)}/−{pr.get('deletions', 0)})")
            pdf.ln(3.5)

        pdf.ln(0.5)

    # ════════════════════════════════════════
    # INTERESTS
    # ════════════════════════════════════════
    sec = data['sections'].get('personal_interests', {})
    hdr = sec.get(lang, 'INTERESTS') if isinstance(sec, dict) else 'INTERESTS'
    pdf.section_header(hdr, margin_top=2.5)
    pdf.set_font('DejaVuSans', '', 8.5)
    interests = [i[lang] for i in data['interests']]
    pdf.cell(0, 4.2, ', '.join(interests), new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # Portfolio = vitrine complète (réservoir de compétences).
    # La contrainte "3 pages" s'applique aux CV sur mesure filtrés par annonce
    # (generate_cv.py), pas ici. On avertit au-delà de 4 pages sans bloquer.
    if pdf.page_no() > 4:
        print(f"[warn] CV portfolio ({lang.upper()}) = {pdf.page_no()} pages (vitrine complète, OK)")

    # Coach: "Vérifier le titre affiché dans l'onglet du PDF. Typiquement : 'CV Prénom NOM'"
    pdf.set_title(f"CV Danny Waser - {titles.get(lang, titles['en'])}")
    pdf.set_author("Danny Waser")
    pdf.set_subject("Curriculum Vitae - AI/ML Engineer")
    pdf.set_keywords("AI/ML, AI Systems, LLM, Applied AI, Automation, MLOps, CV")
    pdf.set_creator("portfolio-cv-pipeline")

    pdf.output(f"static/{OUTPUT_NAMES[lang]}")


if __name__ == '__main__':
    generate_pdf('en')
    generate_pdf('fr')