#!/bin/bash

# Configuration
PROJECT_ROOT="/home/waser/Projets/curriculum"
SEARCHES_DIR="$PROJECT_ROOT/searches"
CONTACTS_DIR="$PROJECT_ROOT/contacts"
VENV_PYTHON="$PROJECT_ROOT/.venv/bin/python"

echo "🚀 Starting recruitment response generation via Bash..."

# 1. Create the PDF generator script first (Static)
PDF_GENERATOR="/tmp/pdf_gen.py"
cat <<'INNEREOF' > "$PDF_GENERATOR"
import sys
from fpdf import FPDF

def generate(input_file, output_file):
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
        pdf = FPDF()
        pdf.add_page()
        pdf_font = "Arial"
        pdf.set_font(pdf_font, size=12)
        # Replace characters that cause latin-1 issues
        clean_text = content.encode('latin-1', 'replace').decode('latin-1')
        pdf.multi_cell(0, 8, txt=clean_text)
        pdf.output(output_file)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    generate(sys.argv[1], sys._arg_v[2]) # wait, typo in arg index! Fix it.
INNEREOF
