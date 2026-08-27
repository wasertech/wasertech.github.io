#!/usr/bin/env python3
"""
gen_letters.py - Lettre de motivation sur mesure (méthode Lab4Tech)

Même source de vérité que generate_cv.py: le réservoir de preuves
(data/evidence/evidence.toml) + le brief produit par match_skills.py.

Structure Lab4Tech (guide lettre motivation):
  OBJET  - identifier clairement le poste (référence si existante)
  VOUS   - intérêt pour l'entreprise/poste, actualité, montrer qu'on a compris
  MOI    - se positionner en fournisseur de compétences (preuves chiffrées)
  NOUS   - ce qu'on peut faire ensemble, inciter à se rencontrer

Usage:
    python gen_letters.py contacts/<entreprise>/offre.md \
        --contact contacts/<entreprise>/contact.toml \
        [--out contacts/<entreprise>/COVER_LETTER.pdf]

Règles Lab4Tech appliquées:
    - Objet = poste + référence
    - VOUS: personnalisation (actualité, activités du poste)
    - MOI: compétences = services, preuves chiffrées
    - NOUS: convergence, incitation à l'entretien
    - 1 page max
"""

import argparse
import re
import sys
from datetime import date
from pathlib import Path

try:
    import tomllib
except ImportError:
    import tomli as tomllib

from fpdf import FPDF
from fpdf.enums import XPos, YPos

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))
from match_skills import build_brief  # noqa: E402

MONTHS_FR = {1: "janvier", 2: "février", 3: "mars", 4: "avril", 5: "mai",
             6: "juin", 7: "juillet", 8: "août", 9: "septembre",
             10: "octobre", 11: "novembre", 12: "décembre"}
MONTHS_EN = {1: "January", 2: "February", 3: "March", 4: "April", 5: "May",
             6: "June", 7: "July", 8: "August", 9: "September",
             10: "October", 11: "November", 12: "December"}


def load_contact(contact_path: Path) -> dict:
    with open(contact_path, "rb") as f:
        return tomllib.load(f)


def today_str(lang: str) -> str:
    t = date.today()
    months = MONTHS_FR if lang == "fr" else MONTHS_EN
    return f"{t.day} {months[t.month]} {t.year}"


def extract_company_context(offer_text: str) -> dict:
    """Extrait le contexte entreprise/poste depuis l'offre (pour le bloc VOUS)."""
    text = offer_text
    # Titre du poste (1ère ligne ou "Head of" / "Engineer" / "Developer")
    title_m = re.search(r"(?:#|##)\s*(.+)", text)
    title = title_m.group(1).strip() if title_m else ""

    # Mots-clés métier présents dans l'offre
    keywords = []
    for kw in ["LLM", "inference", "GPU", "CUDA", "MLOps", "RAG", "agent",
               "agents", "Kubernetes", "Docker", "Python", "data", "ML",
               "platform", "serving", "quantization", "vLLM", "llama.cpp",
               "speech", "voice", "NLP", "fine-tuning", "SFT", "trading",
               "blockchain", "Solana", "analytics", "pipeline"]:
        if re.search(r"\b" + re.escape(kw) + r"\b", text, re.IGNORECASE):
            keywords.append(kw)
    return {"title": title, "keywords": keywords[:8]}


def build_letter(brief: dict, contact: dict, offer_text: str, lang: str) -> dict:
    """Construit les 3 blocs VOUS/MOI/NOUS de la lettre."""
    ctx = extract_company_context(offer_text)
    entreprise = contact.get("contact", {}).get("entreprise", "")
    poste = contact.get("contact", {}).get("poste", "")
    top = brief["evidence"][:4]

    # ── OBJET ──
    if lang == "fr":
        objet = f"Candidature au poste de {poste}"
    else:
        objet = f"Application for the {poste} position"

    # ── VOUS (intérêt, personnalisation) ──
    if lang == "fr":
        vous = (f"Votre entreprise {entreprise} et le poste de {poste} ont retenu "
                f"mon attention, car ils correspondent précisément à mon cœur de métier : "
                f"la conception et l'exploitation de systèmes d'IA en production. "
                f"Votre besoin en {', '.join(ctx['keywords'][:4]) if ctx['keywords'] else 'systèmes IA'} "
                f"est exactement le type de défi que je sais résoudre.")
    else:
        vous = (f"{entreprise}'s {poste} role caught my attention because it maps "
                f"directly to my core expertise: designing and operating production AI "
                f"systems. Your need for {', '.join(ctx['keywords'][:4]) if ctx['keywords'] else 'AI systems'} "
                f"is precisely the kind of challenge I know how to solve.")

    # ── MOI (compétences = services, preuves chiffrées) ──
    moi_parts = []
    for ev in top:
        desc = ev.get(lang, ev.get("en", ""))
        first = re.split(r"(?<=[.!?])\s+", desc)[0]
        moi_parts.append(first)
    if lang == "fr":
        moi = ("Concrètement, je vous apporte : " + " ".join(moi_parts) +
               " Je travaille de bout en bout, de l'architecture à la mise en production. "
               "Je livre des systèmes mesurables, pas des prototypes.")
    else:
        moi = ("Concretely, here is what I bring: " + " ".join(moi_parts) +
               " I work end-to-end, from architecture to production. "
               "I deliver measurable systems, not prototypes.")

    # ── NOUS (convergence, incitation) ──
    if lang == "fr":
        nous = (f"Je suis convaincu que nous pouvons, ensemble, transformer ce besoin en "
                f"un système fiable et performant. Je serais ravi de vous exposer, en entretien, "
                f"comment je m'y prendrais concrètement pour {entreprise}.")
    else:
        nous = (f"I am convinced that, together, we can turn this need into a reliable, "
                f"high-performance system. I would welcome the chance to walk you through, "
                f"in an interview, exactly how I would approach this for {entreprise}.")

    return {"objet": objet, "vous": vous, "moi": moi, "nous": nous}


class LetterPDF(FPDF):
    def __init__(self):
        super().__init__(format="A4")
        self.set_auto_page_break(auto=True, margin=15)
        self.add_font("DejaVuSans", "", "static/fonts/DejaVuSans.ttf")
        self.add_font("DejaVuSans", "B", "static/fonts/DejaVuSans-Bold.ttf")
        self.add_font("DejaVuSans", "I", "static/fonts/DejaVuSans-Oblique.ttf")
        self.set_margins(20, 15, 20)

    def footer(self):
        pass


def render_letter(brief: dict, contact: dict, offer_text: str, out_path: Path, lang: str):
    letter = build_letter(brief, contact, offer_text, lang)
    pdf = LetterPDF()
    pdf.add_page()

    # En-tête expéditeur
    pdf.set_font("DejaVuSans", "B", 11)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 6, "Danny Waser", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font("DejaVuSans", "", 8.5)
    pdf.set_text_color(80, 80, 80)
    c = contact.get("contact", {})
    pdf.cell(0, 4.5, "  |  ".join(filter(None, [c.get("courriel", ""), c.get("telephone", ""), c.get("lieu", "")])),
             new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.cell(0, 4.5, "github.com/wasertech  |  huggingface.co/wasertech  |  wasertech.github.io",
             new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # Destinataire - À DROITE (format suisse, fenêtre d'enveloppe)
    pdf.ln(6)
    pdf.set_font("DejaVuSans", "", 9)
    pdf.set_text_color(0, 0, 0)
    # Bloc destinataire: rue+numéro, NPA+lieu (personne/entreprise en tête)
    recipient_lines = []
    if c.get("personne_contactee"):
        recipient_lines.append(c["personne_contactee"])
    if c.get("entreprise"):
        recipient_lines.append(c["entreprise"])
    rue = " ".join(filter(None, [c.get("rue", ""), str(c.get("numero", ""))])).strip()
    if rue:
        recipient_lines.append(rue)
    npa_lieu = " ".join(filter(None, [str(c.get("npa", "")), c.get("lieu", "")])).strip()
    if npa_lieu:
        recipient_lines.append(npa_lieu)
    pays = c.get("pays", "")
    if pays and pays.lower() not in ("suisse", "switzerland", "ch"):
        recipient_lines.append(pays)
    pdf.set_y(max(pdf.get_y(), 42))
    for line in recipient_lines:
        pdf.set_x(110)
        pdf.multi_cell(80, 5, line)

    # Date - à droite
    pdf.set_x(110)
    pdf.set_font("DejaVuSans", "", 9)
    pdf.cell(80, 5, today_str(lang), align="R")

    # Objet
    pdf.ln(6)
    pdf.set_font("DejaVuSans", "B", 10)
    pdf.cell(0, 5, letter["objet"], new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # Salutation
    pdf.ln(4)
    pdf.set_font("DejaVuSans", "", 9.5)
    if c.get("personne_contactee") and c["personne_contactee"].strip():
        if lang == "fr":
            salutation = f"Madame, Monsieur {c['personne_contactee'].split()[-1]},"
        else:
            salutation = f"Dear {c['personne_contactee'].split()[-1]},"
    else:
        salutation = "Madame, Monsieur," if lang == "fr" else "Dear Sir or Madam,"
    pdf.cell(0, 5, salutation, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # Corps: VOUS / MOI / NOUS
    pdf.ln(4)
    pdf.set_font("DejaVuSans", "", 9.5)
    pdf.set_text_color(0, 0, 0)
    for block in [letter["vous"], letter["moi"], letter["nous"]]:
        pdf.multi_cell(0, 5, block)
        pdf.ln(3)

    # Formule de politesse
    pdf.ln(2)
    pdf.set_font("DejaVuSans", "", 9.5)
    if lang == "fr":
        pdf.multi_cell(0, 5, "Dans l'attente de votre réponse, je vous prie d'agréer, Madame, Monsieur, l'expression de mes salutations distinguées.")
    else:
        pdf.multi_cell(0, 5, "I look forward to your response. Please accept my sincere regards.")

    # Signature
    pdf.ln(8)
    pdf.set_font("DejaVuSans", "B", 10)
    pdf.cell(0, 5, "Danny Waser", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # Limite 1 page
    if pdf.page_no() > 1:
        raise RuntimeError(f"Lettre dépasse 1 page ({pdf.page_no()}) - raccourcir")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    pdf.output(str(out_path))
    return out_path


def main():
    parser = argparse.ArgumentParser(description="Générer une lettre de motivation sur mesure")
    parser.add_argument("offer", help="Chemin vers offre.md")
    parser.add_argument("--contact", required=True, help="Chemin vers contact.toml")
    parser.add_argument("--out", help="Chemin de sortie PDF (défaut: COVER_LETTER.pdf)")
    parser.add_argument("--top", type=int, default=4, help="Nombre de preuves top")
    args = parser.parse_args()

    offer_path = Path(args.offer)
    contact_path = Path(args.contact)
    if not offer_path.exists():
        print(f"ERREUR: {offer_path} introuvable", file=sys.stderr)
        sys.exit(1)
    if not contact_path.exists():
        print(f"ERREUR: {contact_path} introuvable", file=sys.stderr)
        sys.exit(1)

    offer_text = offer_path.read_text(encoding="utf-8")
    brief = build_brief(offer_path, args.top)
    contact = load_contact(contact_path)
    lang = brief["language"]

    if args.out:
        out_path = Path(args.out)
    else:
        # Convention: {CV|ML|LM}_Danny_Waser_{titre}.pdf - ML (EN) / LM (FR)
        abbr = "ML" if lang == "en" else "LM"
        poste = contact.get("contact", {}).get("poste", "Letter")
        poste_safe = re.sub(r"[^a-zA-Z0-9]+", "_", poste).strip("_")[:40]
        out_path = offer_path.parent / f"{abbr}_Danny_Waser_{poste_safe}.pdf"

    result = render_letter(brief, contact, offer_text, out_path, lang)
    print(f"✅ Lettre générée: {result}")
    print(f"   Langue: {lang.upper()} | Structure: VOUS → MOI → NOUS | Preuves: {len(brief['evidence'])}")


if __name__ == "__main__":
    main()
