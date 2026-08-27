# Makefile for CV project

# Variables
VENV = .venv
PYTHON = $(VENV)/bin/python3
PIP = $(VENV)/bin/pip

# Targets

all: build pdf

install: $(VENV)/bin/activate

$(VENV)/bin/activate: requirements.txt
	python3 -m venv $(VENV)
	$(PIP) install -r requirements.txt
	@echo "Virtual environment created and dependencies installed."

build:
	@echo "Building cv_data.json, vCard, and QR code..."
	$(PYTHON) build.py

pdf:
	@echo "Generating PDFs..."
	$(PYTHON) generate_pdf.py

serve:
	@echo "Starting development server at http://localhost:8000"
	@python3 -m http.server 8000

clean:
	@echo "Cleaning up generated files..."
	rm -f static/cv_data.json static/CV_Danny_Waser_AI_ML_Engineer.pdf static/CV_Danny_Waser_Ingenieur_AI_ML.pdf static/waser.vcf static/images/qrc.png

.PHONY: all install build pdf clean serve
