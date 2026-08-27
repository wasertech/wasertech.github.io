#!/usr/bin/env python3
"""
generate_cv.py - CV sur mesure par postulation (méthode Lab4Tech)

Lit le brief produit par match_skills.py + les données du projet
(data/experiences, data/profile, data/education, data/languages,
data/certifications) et génère un PDF ciblé:

  PAGE 1 (lecture RH 10-15s):
    - Nom + positionnement (titre du poste visé)
    - Contact + disponibilité
    - Pitch orienté "réponse au besoin" (3-4 lignes)
    - Compétences (mots-clés / phrases courtes): métier, techniques,
      méthodologiques, linguistiques, soft skills (3-4 max, liées à l'offre)
    - Formation (diplômes + certifications)
    - "Références sur demande"

  PAGE 2+ (lecture recruteur):
    - Expériences en antéchronologie, chiffrées (contexte → rôle → résultat)
    - Contributions open source (si pertinentes)

Usage:
    python generate_cv.py contacts/<entreprise>/offre.md \
        --contact contacts/<entreprise>/contact.toml \
        [--out contacts/<entreprise>/CV_Poste.pdf]

Règles Lab4Tech appliquées:
    - 3 pages max (5 OK pour SSII - non implémenté, 3 par défaut)
    - Page 1 = page RH, lecture rapide
    - Compétences en phrases courtes et spécifiques
    - Expériences chiffrées, réorganisées selon les compétences de l'offre
    - Pied de page: Nom + pagination
"""

import argparse
import json
import re
import sys
from pathlib import Path

try:
    import tomllib
except ImportError:
    import tomli as tomllib

from fpdf import FPDF
from fpdf.enums import XPos, YPos

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))
from match_skills import build_brief, load_evidence  # noqa: E402

# ──────────────────────────────────────────────────────────────
# Chargement des données
# ──────────────────────────────────────────────────────────────

def load_toml(path: Path) -> dict:
    with open(path, "rb") as f:
        return tomllib.load(f)


def load_experiences() -> list[dict]:
    """Charge toutes les expériences, triées par date (antéchronologie)."""
    exp_dir = PROJECT_ROOT / "data" / "experiences"
    exps = []
    for f in sorted(exp_dir.glob("*.toml")):
        data = load_toml(f)
        data["_file"] = f.name
        exps.append(data)
    # Tri: on extrait l'année de début pour trier décroissant
    def year_key(e):
        m = re.search(r"(19|20)\d{2}", e.get("date", ""))
        return int(m.group(0)) if m else 0
    exps.sort(key=year_key, reverse=True)
    return exps


def load_profile() -> dict:
    return load_toml(PROJECT_ROOT / "data" / "profile" / "profile.toml")


def load_education() -> list[dict]:
    return load_toml(PROJECT_ROOT / "data" / "education" / "education.toml").get("education", [])


def load_languages() -> list[dict]:
    return load_toml(PROJECT_ROOT / "data" / "languages" / "languages.toml").get("languages", [])


def load_certifications() -> list[dict]:
    cert_dir = PROJECT_ROOT / "data" / "certifications"
    certs = []
    for f in sorted(cert_dir.glob("*.toml")):
        certs.append(load_toml(f))
    return certs


def load_contact(contact_path: Path) -> dict:
    return load_toml(contact_path)


# ──────────────────────────────────────────────────────────────
# Construction du contenu ciblé
# ──────────────────────────────────────────────────────────────

def build_pitch(brief: dict, lang: str) -> str:
    """Pitch 3-4 lignes orienté 'réponse au besoin' depuis les top preuves."""
    top = brief["evidence"][:3]
    parts = []
    for ev in top:
        # Prendre la description (en/fr) - 1 phrase
        desc = ev.get(lang, ev.get("en", ""))
        # Garder la 1ère phrase
        first = re.split(r"(?<=[.!?])\s+", desc)[0]
        parts.append(first)
    return " ".join(parts)


def build_skill_blocks(brief: dict, lang: str) -> dict:
    """Groupe les top preuves en blocs de compétences (mots-clés / phrases courtes).

    Retourne:
      {
        "metier": [phrases],        # ce que je sais faire dans ce rôle
        "techniques": [phrases],    # technologiques
        "methodologiques": [phrases],
        "linguistiques": [phrases],
        "soft": [phrases],          # 3-4 max
      }
    """
    blocks = {
        "metier": [],
        "techniques": [],
        "methodologiques": [],
        "linguistiques": [],
        "soft": [],
    }

    for ev in brief["evidence"]:
        domain = ev.get("domain", "")
        skill = ev.get("skill", "")
        metrics = ev.get("metrics", [])
        # Phrase courte: skill + 1-2 metrics clés
        metric_str = " · ".join(metrics[:2]) if metrics else ""
        phrase = f"{skill}" + (f" ({metric_str})" if metric_str else "")

        # Chaque preuve va dans UN seul bloc (pas de duplication)
        if domain in ("GPU & Inference", "LLM & Agentic AI", "Speech AI"):
            blocks["metier"].append(phrase)
        elif domain in ("Data & ML",):
            blocks["metier"].append(phrase)
        elif domain in ("DevOps & Infrastructure",):
            blocks["techniques"].append(phrase)
        elif domain in ("Full-Stack",):
            blocks["techniques"].append(phrase)
        elif domain in ("Entrepreneurship",):
            blocks["soft"].append(phrase)
        elif domain in ("Open Source",):
            blocks["methodologiques"].append(phrase)
        elif domain in ("Languages",):
            blocks["linguistiques"].append(phrase)

    # Soft skills: max 4
    blocks["soft"] = blocks["soft"][:4]
    # Métier: max 5
    blocks["metier"] = blocks["metier"][:5]
    # Techniques: max 8
    blocks["techniques"] = blocks["techniques"][:8]
    # Méthodologiques: max 4
    blocks["methodologiques"] = blocks["methodologiques"][:4]

    return blocks


def select_experiences(brief: dict, lang: str) -> list[dict]:
    """Sélectionne et réorganise les expériences selon les compétences de l'offre.

    Règle Lab4Tech: réorganiser les activités selon les compétences exprimées
    dans l'offre, mettre l'accent sur les expériences récentes.
    """
    exps = load_experiences()
    top_tags = set()
    for ev in brief["evidence"][:6]:
        top_tags.update(ev.get("tags", []))

    scored = []
    for exp in exps:
        # Score: combien de tags de l'offre apparaissent dans les détails
        details = exp.get(lang, {}).get("details", "") + exp.get("en", {}).get("details", "")
        score = sum(1 for tag in top_tags if tag in details.lower())
        # Bonus si une preuve pointe vers cette expérience
        for ev in brief["evidence"][:6]:
            if ev.get("source", "") in exp.get("_file", ""):
                score += 3
        scored.append((score, exp))

    scored.sort(key=lambda x: (-x[0], x[1].get("_file", "")))
    return [exp for _, exp in scored]


# ──────────────────────────────────────────────────────────────
# Rendu PDF
# ──────────────────────────────────────────────────────────────

class CVPDF(FPDF):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_auto_page_break(auto=True, margin=12)
        self.add_font("DejaVuSans", "", "static/fonts/DejaVuSans.ttf")
        self.add_font("DejaVuSans", "B", "static/fonts/DejaVuSans-Bold.ttf")
        self.add_font("DejaVuSans", "I", "static/fonts/DejaVuSans-Oblique.ttf")
        self.add_font("DejaVuSans", "BI", "static/fonts/DejaVuSans-BoldOblique.ttf")
        self._name = ""

    def header(self):
        pass  # Pas de header automatique - on gère tout en body

    def footer(self):
        if self.page_no() == 1:
            return
        self.set_y(-10)
        self.set_font("DejaVuSans", "", 7)
        self.set_text_color(120, 120, 120)
        self.cell(0, 5, f"{self._name}  |  {self.page_no()}/{{nb}}", align="C")

    def section_header(self, text, margin_top=4):
        if margin_top > 0:
            self.ln(margin_top)
        self.set_font("DejaVuSans", "B", 9.5)
        self.set_text_color(50, 50, 50)
        w = self.w - self.l_margin - self.r_margin
        self.set_draw_color(70, 70, 70)
        self.cell(w, 5, text.upper(), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.line(self.l_margin, self.get_y(), self.l_margin + w, self.get_y())
        self.ln(2)
        self.set_text_color(0, 0, 0)

    def bullet(self, text, indent=4, font_size=8.5, leading=4.2):
        """Bulle avec texte (pas de liens - on les retire)."""
        # Retirer les liens markdown [label](url) → garder le label
        text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
        x = self.l_margin + indent
        max_w = self.w - self.r_margin - x
        self.set_font("DejaVuSans", "", font_size)
        self.set_text_color(0, 0, 0)
        self.set_x(self.l_margin)
        self.cell(indent, leading, "•")
        self.set_x(x)
        self.multi_cell(max_w, leading, text, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    def bullet_bold(self, bold_part, rest, indent=4, font_size=8.5, leading=4.2):
        """Bulle avec début en gras."""
        x = self.l_margin + indent
        self.set_x(self.l_margin)
        self.cell(indent, leading, "•")
        self.set_x(x)
        self.set_font("DejaVuSans", "B", font_size)
        self.set_text_color(0, 0, 0)
        self.write(leading, bold_part)
        if rest:
            self.set_font("DejaVuSans", "", font_size)
            self.write(leading, rest)
        self.ln(leading)

    def check_space(self, needed=15):
        """Force un saut de page si pas assez de place."""
        if self.get_y() + needed > self.h - self.b_margin:
            self.add_page()

    def write_line_with_links(self, text, x_start, font_size=8.5, leading=4):
        """Bulle avec texte + liens [label](url) cliquables, retour à la ligne auto."""
        self.set_x(x_start)
        self.set_font("DejaVuSans", "", font_size)
        self.cell(3, leading, "•")
        self.set_x(x_start + 4)
        max_w = self.w - self.r_margin - self.get_x()

        parts = re.split(r"(\[.+?\]\(.+?\))", text)
        segments = []
        for p in parts:
            m = re.match(r"\[(.+?)\]\((.+?)\)", p)
            if m:
                segments.append(("link", m.group(1), m.group(2)))
            else:
                segments.append(("text", p))
        self._render_segments(segments, max_w, leading, font_size)

    def _render_segments(self, segments, max_w, leading, font_size):
        """Rend du texte mêlant segments texte/lien avec retour à la ligne."""
        line = ""
        line_w = 0.0

        def flush_line():
            nonlocal line, line_w
            if line:
                self.set_font("DejaVuSans", "", font_size)
                self.set_text_color(0, 0, 0)
                self.write(leading, line)
                line = ""
                line_w = 0.0

        for i, (seg_type, *args) in enumerate(segments):
            if seg_type == "text":
                for w in args[0].split(" "):
                    if not w:
                        continue
                    ww = self.get_string_width(" " + w) if line else self.get_string_width(w)
                    if line_w + ww > max_w:
                        flush_line()
                        self.ln(leading)
                        self.set_x(self.l_margin + 4)
                        line_w = 0.0
                        line = w
                        line_w = self.get_string_width(w)
                    else:
                        if line:
                            line += " "
                            line_w += self.get_string_width(" ")
                        line += w
                        line_w += self.get_string_width(w)
            elif seg_type == "link":
                label, url = args
                # Pas d'espace si le texte précédent se termine par "("
                need_space = line_w > 0 and not line.rstrip().endswith("(")
                flush_line()
                ww = self.get_string_width(" " + label) if need_space else self.get_string_width(label)
                if need_space and ww > max_w:
                    self.ln(leading)
                    self.set_x(self.l_margin + 4)
                    need_space = False
                if need_space:
                    self.write(leading, " ")
                self.set_font("DejaVuSans", "", font_size)
                self.set_text_color(0, 0, 150)
                self.write(leading, label, url)
                self.set_text_color(0, 0, 0)
                # Espace après le lien, sauf si le texte suivant commence par une ponctuation
                nxt = segments[i + 1] if i + 1 < len(segments) else None
                if not (nxt and nxt[0] == "text" and nxt[1].lstrip()[:1] in ",.;:)]"):
                    self.write(leading, " ")
                line_w = 0.0

        flush_line()
        self.ln(leading)


def render_cv(brief: dict, contact: dict, out_path: Path, lang: str):
    """Génère le PDF du CV sur mesure."""
    pdf = CVPDF(format="A4")
    pdf._name = "Danny Waser"
    pdf.add_page()
    pdf.set_margins(14, 10, 14)

    # ── HEADER ──
    pdf.set_font("DejaVuSans", "B", 18)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 8, "Danny Waser", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # Positionnement = titre du poste visé
    poste = contact.get("contact", {}).get("poste", "")
    entreprise = contact.get("contact", {}).get("entreprise", "")
    if poste:
        pdf.set_font("DejaVuSans", "", 10)
        pdf.set_text_color(80, 80, 80)
        pdf.cell(0, 5, poste + (f"  |  {entreprise}" if entreprise else ""), new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # Contact
    pdf.ln(2)
    pdf.set_font("DejaVuSans", "", 7.8)
    pdf.set_text_color(60, 60, 60)
    contact_line = "  |  ".join(filter(None, [
        contact.get("contact", {}).get("courriel", ""),
        contact.get("contact", {}).get("telephone", ""),
        contact.get("contact", {}).get("lieu", ""),
    ]))
    if contact_line:
        pdf.cell(0, 4, contact_line, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    # Liens
    links_line = "  |  ".join(filter(None, [
        "github.com/wasertech",
        "huggingface.co/wasertech",
        "wasertech.github.io",
    ]))
    pdf.cell(0, 4, links_line, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # ── PITCH (réponse au besoin) ──
    pdf.section_header("Profil" if lang == "fr" else "Profile")
    pitch = build_pitch(brief, lang)
    pdf.set_font("DejaVuSans", "", 8.8)
    pdf.set_text_color(0, 0, 0)
    pdf.multi_cell(0, 4.4, pitch)

    # ── COMPÉTENCES ──
    blocks = build_skill_blocks(brief, lang)

    if blocks["metier"]:
        pdf.section_header("Compétences métier" if lang == "fr" else "Core Competencies")
        for phrase in blocks["metier"]:
            pdf.bullet(phrase)

    if blocks["techniques"]:
        pdf.section_header("Compétences techniques" if lang == "fr" else "Technical Skills")
        for phrase in blocks["techniques"]:
            pdf.bullet(phrase)

    if blocks["methodologiques"]:
        pdf.section_header("Compétences méthodologiques" if lang == "fr" else "Methodological Skills")
        for phrase in blocks["methodologiques"]:
            pdf.bullet(phrase)

    # ── CERTIFICATIONS (section dédiée page 1, avant Langues) ──
    certs = load_certifications()
    if certs:
        pdf.section_header("Certifications" if lang == "fr" else "Certifications")
        for c in certs:
            c_data = c.get(lang, c.get("en", {}))
            period = c.get("start_date", "")
            if c.get("end_date") and c["end_date"] != c.get("start_date"):
                period = f"{c['start_date']} - {c['end_date']}"
            pdf.bullet_bold(c_data.get("title", ""),
                            f"  |  {c_data.get('issuer', '')}  ({period})")

    # Langues
    langs = load_languages()
    if langs:
        pdf.section_header("Langues" if lang == "fr" else "Languages")
        lang_str = "  ·  ".join(f"{l.get(lang, l.get('en', ''))} ({l.get('level', '')})" for l in langs)
        pdf.set_font("DejaVuSans", "", 8.5)
        pdf.cell(0, 4.2, lang_str, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    if blocks["soft"]:
        pdf.section_header("Soft Skills" if lang == "en" else "Compétences transversales")
        for phrase in blocks["soft"]:
            pdf.bullet(phrase)

    # ── FORMATION (page 2+, pas pertinente pour le domaine) ──
    # Rendu APRÈS le add_page() des expériences - voir bloc plus bas

    # Références
    pdf.ln(3)
    pdf.set_font("DejaVuSans", "I", 8)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 4, "Références sur demande" if lang == "fr" else "References available upon request")

    # ── PAGE 2: EXPÉRIENCES ──
    pdf.add_page()
    exps = select_experiences(brief, lang)
    pdf.section_header("Expérience professionnelle" if lang == "fr" else "Professional Experience", margin_top=0)

    for exp in exps:
        e_data = exp.get(lang, exp.get("en", {}))
        title = e_data.get("title", "")
        company = e_data.get("company", "")
        date = exp.get("date", "")
        details = e_data.get("details", "")

        # En-tête de l'expérience
        pdf.check_space(20)
        pdf.set_font("DejaVuSans", "B", 9)
        pdf.set_text_color(0, 0, 0)
        # Company à gauche, date à droite
        pdf.cell(pdf.w - pdf.l_margin - pdf.r_margin - 40, 4.5, f"{company}", align="L")
        pdf.cell(40, 4.5, date, align="R", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_font("DejaVuSans", "I", 8.2)
        pdf.set_text_color(80, 80, 80)
        pdf.cell(0, 4, title, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(1)

        # Détails (bulles uniformes, liens cliquables)
        for line in details.strip().split("\n"):
            line = line.strip()
            if not line:
                continue
            # Retirer le tiret de début
            line = re.sub(r"^[-•]\s*", "", line)
            if re.search(r"\[.+?\]\(.+?\)", line):
                pdf.write_line_with_links(line, pdf.l_margin, font_size=8.2, leading=4)
            else:
                pdf.bullet(line, font_size=8.2, leading=4)
        pdf.ln(2)

    # ── FORMATION (page 2+, pas pertinente pour le domaine) ──
    edu = [e for e in load_education() if e.get("pdf_include", True)]
    if edu:
        pdf.section_header("Formation" if lang == "fr" else "Education", margin_top=3)
        for e in edu:
            e_data = e.get(lang, e.get("en", {}))
            pdf.bullet_bold(e_data.get("title", ""),
                            f"  |  {e_data.get('institution', '')}, {e_data.get('location', '')}  ({e.get('date', '')})")

    # ── CONTRIBUTIONS OPEN SOURCE (si pertinentes) ──
    oss_relevant = [ev for ev in brief["evidence"] if ev.get("domain") == "Open Source"]
    if oss_relevant:
        pdf.check_space(25)
        pdf.section_header("Contributions open source" if lang == "fr" else "Open Source Contributions")
        for ev in oss_relevant[:3]:
            desc = ev.get(lang, ev.get("en", ""))
            metrics = " · ".join(ev.get("metrics", [])[:4])
            pdf.bullet(f"{ev.get('skill', '')}  |  {desc}  ({metrics})" if metrics else f"{ev.get('skill', '')}  |  {desc}")

    # ── LIMITE 3 PAGES ──
    if pdf.page_no() > 3:
        raise RuntimeError(f"CV dépasse 3 pages ({pdf.page_no()}) - réduire le contenu")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    pdf.output(str(out_path))
    return out_path


# ──────────────────────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────────────────────

def build_brief_generic(top_n: int = 10) -> dict:
    """Brief générique (portfolio): les preuves les plus fortes, sans offre.

    Utilisé pour le CV du portfolio - la version 'meilleure synthèse' qui
    résume le mieux le profil, indépendante de toute offre.
    """
    evidence = load_evidence()
    # Tri par poids puis par nombre de metrics (richesse de la preuve)
    evidence.sort(key=lambda e: (-e.get("weight", 3), -len(e.get("metrics", []))))
    top = evidence[:top_n]
    return {
        "offer_path": None,
        "language": "fr",
        "keywords_found": 0,
        "tag_map": {},
        "evidence": top,
        "all_scored": top,
        "generic": True,
    }


def main():
    parser = argparse.ArgumentParser(description="Générer un CV sur mesure")
    parser.add_argument("offer", nargs="?", help="Chemin vers offre.md (optionnel en mode --generic)")
    parser.add_argument("--contact", help="Chemin vers contact.toml")
    parser.add_argument("--out", help="Chemin de sortie PDF (défaut: CV_<poste>.pdf)")
    parser.add_argument("--top", type=int, default=8, help="Nombre de preuves top")
    parser.add_argument("--generic", action="store_true",
                        help="Mode portfolio: CV générique 'meilleure synthèse' (pas d'offre)")
    args = parser.parse_args()

    if args.generic:
        brief = build_brief_generic(args.top)
        lang = "fr"
        out_path = Path(args.out) if args.out else PROJECT_ROOT / "CV_Danny_Waser_Portfolio.pdf"
        contact = {"contact": {"poste": "AI Systems Engineer - LLM Inference & GPU",
                               "entreprise": "", "courriel": "danny@wasertech.ch",
                               "telephone": "+41 79 000 00 00", "lieu": "Lausanne, Suisse"}}
    else:
        if not args.offer:
            print("ERREUR: chemin de l'offre requis (ou --generic)", file=sys.stderr)
            sys.exit(1)
        offer_path = Path(args.offer)
        contact_path = Path(args.contact) if args.contact else None
        if not offer_path.exists():
            print(f"ERREUR: {offer_path} introuvable", file=sys.stderr)
            sys.exit(1)
        if not contact_path or not contact_path.exists():
            print(f"ERREUR: contact.toml requis (--contact)", file=sys.stderr)
            sys.exit(1)

        brief = build_brief(offer_path, args.top)
        contact = load_contact(contact_path)
        lang = brief["language"]

        # Nom de sortie
        if args.out:
            out_path = Path(args.out)
        else:
            poste = contact.get("contact", {}).get("poste", "CV")
            poste_safe = re.sub(r"[^a-zA-Z0-9]+", "_", poste).strip("_")[:40]
            out_path = offer_path.parent / f"CV_Danny_Waser_{poste_safe}.pdf"

    result = render_cv(brief, contact, out_path, lang)
    mode = "PORTFOLIO (générique)" if args.generic else f"SUR MESURE ({offer_path.parent.name})"
    print(f"✅ CV généré: {result}")
    print(f"   Mode: {mode} | Langue: {lang.upper()} | Preuves: {len(brief['evidence'])}")


if __name__ == "__main__":
    main()
