# AGENTS.md

## Project Overview

Python-based Curriculum Vitae (CV) generator. CV content lives in `data/*.toml` files. Build scripts aggregate TOML into `static/cv_data.json`, then generate a static website, bilingual PDFs, a vCard, and a QR code.

## Architecture

- **Data Layer (`data/`)**: All CV content stored as `.toml` files — the single source of truth.
- **`build.py`**: Aggregates TOML into `static/cv_data.json`, fetches GitHub contributions via `gh` CLI, generates vCard and QR code.
- **`generate_pdf.py`**: Reads `cv_data.json` and uses `fpdf2` to render `CV_EN.pdf` and `CV_FR.pdf`.
- **Frontend (`static/`)**: Static website using vanilla JS, Pico.css. `js/app.js` fetches `cv_data.json` and renders the UI.

## Commands

| Command | Description |
| :--- | :--- |
| `make install` | Create `.venv` and install dependencies from `requirements.txt` |
| `make all` | Full build: JSON data, vCard, QR code, and PDFs |
| `make build` | Run `build.py` only (JSON, vCard, QR code) |
| `make pdf` | Run `generate_pdf.py` only (PDF generation) |
| `make serve` | Start local HTTP server at `http://localhost:8000` |
| `make clean` | Remove generated artifacts |

There are no unit tests in this project. To verify changes, run `make all` then `make serve` and inspect the output in a browser.

## Development Workflow

1. Edit `.toml` files in `data/` to modify CV content.
2. Run `make all` to regenerate all assets.
3. Run `make serve` to preview the website locally (required due to CORS — opening `index.html` directly will not work).

## Code Style

### Python
- Follow **PEP 8** conventions.
- Use snake_case for functions and variables.
- Use meaningful docstrings for public functions (see `fetch_github_contributions` in `build.py`).
- Graceful error handling: wrap external calls (subprocess, file I/O) in try/except, print warnings, return safe defaults.
- Use f-strings for string interpolation.
- Import order: standard library first, then third-party, then local.

### JavaScript
- Vanilla ES6+ (no frameworks). Use `const`/`let`, arrow functions, template literals.
- Event listeners attached in `DOMContentLoaded` handler.
- Helper functions are defined as `const` with descriptive names.

### TOML Data Files
- All localized content uses `[en]` and `[fr]` sections. Both languages must be provided.
- Experiences and certifications are one `.toml` file per entry in their respective directories.
- Use multi-line strings (`"""`) for longer text content.

### Frontend (HTML/CSS)
- Uses Pico.css for base styling with custom SCSS in `static/scss/`.
- Font Awesome icons for UI elements.

## Important Notes

- **No `.cursorrules`, `.cursor/`, or `.github/copilot-instructions.md`** files exist in this repo.
- The `gh` CLI is optional. If missing or unauthenticated, `build.py` warns and proceeds without GitHub contribution data.
- Generated files (`cv_data.json`, PDFs, vCard, QR code) are in `static/` and should not be manually edited.
- Python 3.10+ is required.
