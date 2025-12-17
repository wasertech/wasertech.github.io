# Project Overview

This is a **Python-based Curriculum Vitae (CV) generator**. It manages personal professional data in structured **TOML files** and uses them to generate:
1.  A **static website** (HTML/JS/CSS) that dynamically loads content.
2.  **PDF versions** of the CV in multiple languages (English and French).
3.  **vCard** and **QR Code** for contact sharing.

The project separates content (data) from presentation (templates/scripts), making it easy to update the CV without touching the code.

## 🏗 Architecture

*   **Data Layer (`data/`)**: All CV content is stored here in `.toml` files (e.g., `profile.toml`, `experiences/*.toml`). This acts as the single source of truth.
*   **Build Scripts**:
    *   `build.py`: Aggregates all `.toml` files into a single `static/cv_data.json` file for the frontend. It also fetches GitHub contributions using the `gh` CLI and generates the vCard/QR code.
    *   `generate_pdf.py`: Reads `static/cv_data.json` and uses `fpdf2` to render pixel-perfect PDF resumes (`CV_EN.pdf`, `CV_FR.pdf`).
*   **Frontend (`static/`)**: A static web application.
    *   `index.html`: The main entry point.
    *   `js/app.js`: Fetches `cv_data.json` and renders the UI.
    *   **Pico.css**: Used for clean, minimalist styling.

## 🚀 Key Commands

The project uses a `Makefile` to automate common tasks.

| Command | Description |
| :--- | :--- |
| `make install` | Sets up the Python virtual environment (`.venv`) and installs dependencies. |
| `make all` | Runs the full build process: generates JSON data, vCard, QR code, and PDFs. |
| `make build` | Runs only `build.py` (JSON, vCard, QR code). |
| `make pdf` | Runs only `generate_pdf.py` (PDF generation). |
| `make serve` | Starts a local HTTP server at `http://localhost:8000` to view the site (bypassing CORS issues). |
| `make clean` | Removes all generated artifacts (`cv_data.json`, PDFs, etc.). |

## 💻 Development Conventions

*   **Adding Content:**
    *   **New Experiences/Certifications:** Create a new `.toml` file in `data/experiences/` or `data/certifications/`. Use existing files as templates.
    *   **Updating Static Info:** Edit the single `.toml` files (e.g., `profile.toml`, `skills.toml`).
    *   **Rebuild:** Always run `make all` (or at least `make build`) after modifying data files to see changes.
*   **Code Style:**
    *   Python scripts generally follow PEP 8.
    *   The frontend uses standard HTML5/CSS3 and vanilla JavaScript (ES6+).
*   **Localization:** The project is bilingual (EN/FR). Ensure all data files contain keys for both `[en]` and `[fr]` sections where applicable.

## 📂 Directory Structure

*   `data/`: **Edit your CV content here.**
    *   `profile/`, `contact/`, `skills/`, `languages/`, `interests/`: Single `.toml` files.
    *   `experiences/`, `certifications/`: Multiple `.toml` files (one per item).
    *   `contributions/`: Configuration for fetching GitHub stats.
*   `static/`: The web root. Contains CSS, fonts, images, and the generated assets.
    *   `cv_data.json`: The generated data file consumed by the frontend.
*   `build.py`: Main data processing script.
*   `generate_pdf.py`: PDF rendering script.

## ⚠️ Requirements & Dependencies

*   **Python 3.10+**
*   **GitHub CLI (`gh`)**: *Optional but recommended.* Used by `build.py` to fetch open-source contribution statistics. If missing or not authenticated, the build will warn but proceed without GitHub data.
*   **Python Libraries**: Defined in `requirements.txt`.
    *   **Note:** The dependency list is extensive and includes heavy ML libraries (`torch`, `transformers`, `nvidia-*`). These appear to be part of a larger shared environment or intended for future AI features, as the core build scripts mainly rely on `toml`, `fpdf2`, `Pillow`, and standard libraries.