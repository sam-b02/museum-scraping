# Museum Scraping Project

## Overview
A complete end‑to‑end pipeline for extracting Google Maps reviews of Indian museums. The workflow starts from a PDF list of museums, generates Google Maps URLs, scrapes reviews, cleans the data, and outputs both JSON datasets and ready‑to‑use HTML reports.

## Repository Structure
```
📁 data/            # Source PDFs (e.g., museums.pdf)
📁 output/          # Raw and final JSON results, text extracts
📁 reviews/         # Sample processed review files
📁 scripts/         # Pipeline scripts
   ├─ url.py               # Build Google Maps URLs from PDF data
   ├─ scraper.py           # Scrape reviews (supports async mode)
   ├─ museum_clean.py      # Basic cleaning of raw HTML
   ├─ final_clean.py       # Final data tidy‑up
   └─ …
📁 templates/       # HTML templates for rendering results
📁 .env            # Store API keys (never commit)
📄 requirements.txt
📄 README.md
```

## Installation
1. **Prerequisites** – Python 3.10+ installed and added to `PATH`.
2. Clone the repository:
   ```bash
   git clone https://github.com/sam-b02/museum-scraping
   cd museum-scraping
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create a `.env` file with your Google Maps API key:
   ```text
   GOOGLE_MAPS_API_KEY=<your-key>
   ```

## Quick Start
Run the full pipeline with a series of commands (adjust paths as needed):
```bash
python scripts/url.py          # generate URLs from `data/museums.pdf`
python scripts/scraper.py       # scrape reviews for each URL (async enabled by default)
python scripts/museum_clean.py  # clean raw HTML output
python scripts/final_clean.py   # produce final JSON (`output/output_final.json`)
```
Open `templates/index.html` in a browser to view a simple HTML report.

## Usage Details
- **Generating URLs** – `url.py` reads `data/museums.pdf` and writes `urls.txt`.
- **Scraping** – `scraper.py` reads `urls.txt`. Use the `--async` flag for parallel requests (default enabled).
- **Cleaning** – `museum_clean.py` removes HTML tags and normalises whitespace.
- **Finalisation** – `final_clean.py` merges all cleaned files into `output_final.json` and validates the schema.

## Configuration
All configurable parameters live in `config.yaml` (generated on first run). Common settings:
- `max_requests_per_minute` – throttle rate for Google Maps.
- `output_dir` – directory for JSON and HTML results.

## Testing
```bash
pytest tests/          # run unit tests for URL generation and parsers
```

## License
This project is licensed under the MIT License.

---
*Built with Python, Requests, and BeautifulSoup.*