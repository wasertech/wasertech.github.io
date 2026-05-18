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

- The `gh` CLI is optional. If missing or unauthenticated, `build.py` warns and proceeds without GitHub contribution data.
- Generated files (`cv_data.json`, PDFs, vCard, QR code) are in `static/` and should not be manually edited.
- Python 3.10+ is required.

## Behavioral Guidelines

Derived from Andrej Karpathy's observations on LLM coding pitfalls. These guidelines bias toward caution over speed — for trivial tasks, use judgment.

### Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

- State assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them — don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

### Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

### Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it — don't delete it.

When your changes create orphans:
- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: Every changed line should trace directly to the user's request.

### Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:
- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:
```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.

---

**These guidelines are working if:** fewer unnecessary changes in diffs, fewer rewrites due to overcomplication, and clarifying questions come before implementation rather than after mistakes.
