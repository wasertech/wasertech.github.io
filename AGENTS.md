# AGENTS.md

## Project Overview

Python-based Curriculum Vitae (CV) generator. CV content lives in `data/*.toml` files. Build scripts aggregate TOML into `static/cv_data.json`, then generate a static website, bilingual PDFs, a vCard, and a QR code.

**Two-generation system:**
1. **Portfolio (vitrine)** — `build.py` → `generate_pdf.py` produces the generic `CV_EN.pdf`/`CV_FR.pdf` from `static/cv_data.json`.
2. **Sur mesure (par postulation)** — `match_skills.py` → `generate_cv.py` + `gen_letters.py` produces a targeted CV + cover letter per job offer from the evidence reservoir (`data/evidence/evidence.toml`).

## Architecture

- **Data Layer (`data/`)**: All CV content stored as `.toml` files — the single source of truth.
  - `data/evidence/evidence.toml` — **evidence reservoir**: proof entries (bilingual, quantified, tagged) that feed BOTH the targeted CV and the cover letter. Each entry: `skill`, `domain`, `tags`, `metrics` (numbers), `fr`/`en` descriptions, `source`.
- **Applications Tracking (`contacts/`)**: Subdirectory per job application. Each has a `contact.toml` (metadata) + `offre.md` (job posting text). Generated outputs follow the naming convention below.
- **`build.py`**: Aggregates TOML into `static/cv_data.json`, fetches GitHub contributions via `gh` CLI, generates vCard and QR code.
- **`generate_pdf.py`**: Portfolio CV — reads `cv_data.json` and uses `fpdf2` to render `CV_EN.pdf` and `CV_FR.pdf`.
- **`match_skills.py`**: Matches a job offer (`offre.md`) against the evidence reservoir. Scores each proof by keyword overlap + synonym map, produces a `brief` (top evidence, language detection FR/EN). Used by both `generate_cv.py` and `gen_letters.py`.
- **`generate_cv.py`**: Targeted CV from an offer. `--generic` mode produces the portfolio CV from the strongest evidence.
- **`gen_letters.py`**: Targeted cover letter from an offer, Lab4Tech VOUS→MOI→NOUS structure.
- **Frontend (`static/`)**: Static website using vanilla JS, Pico.css. `js/app.js` fetches `cv_data.json` and renders the UI.

## Output Naming Convention

Generated application files must follow `{TYPE}_Danny_Waser_{titre}.pdf`:

| Document | Type | Exemple |
| :--- | :--- | :--- |
| CV (identique FR/EN) | `CV` | `CV_Danny_Waser_ML_Platform_Engineer.pdf` |
| Lettre de motivation EN | `ML` | `ML_Danny_Waser_ML_Platform_Engineer.pdf` |
| Lettre de motivation FR | `LM` | `LM_Danny_Waser_Data_Engineer_100.pdf` |
| CV portfolio (générique) | `CV` | `CV_Danny_Waser_Portfolio.pdf` |

- `titre` = poste du `contact.toml`, espaces → underscores, tronqué à 40 chars.
- `ML` (Motivation Letter) pour offre EN, `LM` (Lettre de Motivation) pour offre FR.
- Les scripts calculent automatiquement ce nom ; `--out` reste disponible pour forcer un chemin.

## Commands

| Command | Description |
| :--- | :--- |
| `make install` | Create `.venv` and install dependencies from `requirements.txt` |
| `make all` | Full build: JSON data, vCard, QR code, and PDFs |
| `make build` | Run `build.py` only (JSON, vCard, QR code) |
| `make pdf` | Run `generate_pdf.py` only (portfolio PDF generation) |
| `.venv/bin/python3 generate_cv.py contacts/<company>/offre.md --contact contacts/<company>/contact.toml` | Targeted CV → `CV_Danny_Waser_<titre>.pdf` |
| `.venv/bin/python3 generate_cv.py --generic` | Portfolio CV from strongest evidence → `CV_Danny_Waser_Portfolio.pdf` |
| `.venv/bin/python3 gen_letters.py contacts/<company>/offre.md --contact contacts/<company>/contact.toml` | Targeted cover letter → `ML_Danny_Waser_<titre>.pdf` (EN) / `LM_Danny_Waser_<titre>.pdf` (FR) |
| `make serve` | Start local HTTP server at `http://localhost:8000` |
| `make clean` | Remove generated artifacts |

There are no unit tests in this project. To verify changes, run `make all` then `make serve` and inspect the output in a browser.

## Lab4Tech Methodology (2026 Workshop)

This project integrates the Lab4Tech 7-step career marketing methodology:

### 1. Cover Letter Structure: VOUS - MOI - NOUS
| Section | Content | Purpose |
|---------|---------|---------|
| **VOUS** (You) | Reference specific company needs from the job posting | Show research & understanding |
| **MOI** (Me) | 3 key qualifications matching requirements | Demonstrate fit |
| **NOUS** (Us) | Future together, enthusiasm, next steps | Project forward |

### 2. Self-Marketing Steps (for CV positioning)
1. **Se connaître** — SWOT, personal values, differentiators
2. **Se positionner** — Define your professional space
3. **Se rendre visible** — LinkedIn, blog, events
4. **Cibler** — Target companies by sector/tech/values
5. **Se rassurer** — Build confidence before interviews
6. **Se présenter** — Elevator pitch, dossier, storytelling
7. **Créer le lien de confiance** — Transparency & trust

### 3. Swiss-Specific Resources
- **Job boards**: ictcareer.ch, ai-jobs-switzerland.ch, swissdevjobs.ch, jobs.ch, jobup.ch
- **Salary calculators**: Salarium OFS, Robert Half Guide, Michael Page
- **Company research**: swissfirms.ch, kompass.ch, sociorama.ch, Zefix
- **Associations**: SwissICT, CH Open, PMI, ISACA, Clusis, Digitalswitzerland, AGRP, CRR
- **Networking**: 50%+ of TIC jobs in CH come from network — cooptation, référencement, events

### 4. Interview Preparation
- Research company (products, clients, competition, reputation)
- Research position (requirements, challenges, new or replacement)
- Prepare pitch (30s/60s/90s versions)
- Types: directive, semi-directive, non-directive, high-pressure, friendly
- Body language, phone readiness, thank-you email within 24h
- Salary negotiation: know benchmarks before discussing

### 5. LinkedIn Optimization
- Professional photo (AI-analyzed), custom banner, keyword-rich headline
- "About" with value proposition, achievement-based experience descriptions
- Endorsements, recommendations, regular posting
- Tools: Jobscan, Fyte4u pitch app, LinkedIn Photo Analyzer, Boolean search

## Development Workflow

1. Edit `.toml` files in `data/` to modify CV content.
2. Run `make all` to regenerate all assets.
3. Run `make serve` to preview the website locally (required due to CORS — opening `index.html` directly will not work).
4. For job applications, manage files inside `contacts/<company>/contact.toml` + `offre.md`. To generate the corresponding targeted CV and cover letter, run:
   ```bash
   .venv/bin/python3 generate_cv.py contacts/<company>/offre.md --contact contacts/<company>/contact.toml
   .venv/bin/python3 gen_letters.py contacts/<company>/offre.md --contact contacts/<company>/contact.toml
   ```

## Contact Log / Application Tracking (`contact.toml` format)

Each application in `contacts/<company_directory>/contact.toml` must follow this schema:

```toml
[contact]
date_postulation = "YYYY-MM-DD"                     # (mandatory)
methode_postulation = "voie electronique"           # (mandatory: 'voie electronique', 'lettre', 'contact personnel', 'téléphone')
entreprise = "Company Name"                         # (mandatory)
rue = "Street Name"                                 # (mandatory)
numero = "Number"                                   # (mandatory)
case_postale = ""                                   # (optional)
pays = "Country"                                    # (mandatory)
npa = "Zip/NPA"                                     # (mandatory)
lieu = "City/Lieu"                                  # (mandatory)
personne_contactee = "Contact Person/Department"    # (mandatory)
courriel = "contact@email.com"                      # (mandatory)
telephone = ""                                      # (optional)
poste = "Job Title"                                 # (mandatory)
lien_offre = "https://..."                           # (mandatory: MUST be a direct link to the offer; 404/broken/generic links are invalid!)
taux_occupation = "100%"                            # (mandatory)
statut = "en suspens"                               # (mandatory: 'en suspens', 'engagement', 'réponse négative')

[cover_letter]
langue = "fr"                                       # (mandatory: 'fr' or 'en')
body = [                                            # (mandatory: array of paragraphs)
    "Paragraph 1...",
    "Paragraph 2..."
]
```

> [!IMPORTANT]
> The link to the offer (`lien_offre`) must always be a direct link to the job announcement. If it returns a 404, is broken, or is a generic careers landing page, it is **invalid**!


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
