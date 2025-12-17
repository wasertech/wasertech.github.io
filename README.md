# My Curriculum Vitae

This repository contains the source for my personal curriculum vitae website and for generating my CV as a PDF.

## 🚀 How to Work on This Project

### Why a Local Server is Required

Modern web browsers have a security feature called CORS (Cross-Origin Resource Sharing) that prevents a web page from loading local files directly from your computer's file system (`file:///...`). Because this website dynamically loads its content from `cv_data.json` using the `fetch` API, you **must** use a local web server to view it in your browser. Opening the `index.html` file directly will not work.

### Quick Start

1.  **Install dependencies:** This only needs to be done once.
    ```bash
    make install
    ```

2.  **Build all assets:** Before you can view the site or the PDFs, you need to generate them from the data files.
    ```bash
    make all
    ```

3.  **View the website locally:** This is the most important step for local development.
    ```bash
    make serve
    ```
    Then open [http://localhost:8000](http://localhost:8000) in your browser.

## 📝 How to Update Your CV

This project is designed to be easy to maintain. All your CV data is stored in simple `.toml` files in the `data/` directory.

### To Add a New Experience

1.  Create a new `.toml` file in the `data/experiences/` directory. You can use an existing file as a template.
2.  After adding or editing any `.toml` files, regenerate all the assets by running:
    ```bash
    make all
    ```
3.  You can then view your changes by running `make serve` again.

### To Update Other Sections

*   **Profile:** Edit `data/profile/profile.toml`
*   **Contact Info:** Edit `data/contact/contact.toml`
*   **Skills:** Edit `data/skills/skills.toml`
*   **Languages:** Edit `data/languages/languages.toml`
*   **Interests:** Edit `data/interests/interests.toml`
*   **Certifications:** Add a new `.toml` file in `data/certifications/`

After any change, run `make all` to regenerate all assets.

## ⚙️ Makefile Targets

*   `make all`: (Default) Builds the JSON data, vCard, QR code, and generates the PDFs.
*   `make build`: Builds the `cv_data.json`, `waser.vcf`, and `qrc.png` from the TOML data.
*   `make pdf`: Generates the `CV_EN.pdf` and `CV_FR.pdf` files.
*   `make install`: Sets up the Python virtual environment and installs all required dependencies from `requirements.txt`.
*   `make serve`: Starts a local development server for viewing the website.
*   `make clean`: Removes all generated files.

## 🌐 Frontend

The website is a simple, static site that uses [Pico.css](https://picocss.com/) for styling. All the content is dynamically loaded from `static/cv_data.json` by `static/js/app.js`. It is designed to be hosted on GitHub Pages.
