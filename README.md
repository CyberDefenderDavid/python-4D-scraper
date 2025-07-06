# Singapore 4D Results Scraper

Automatically scrapes daily 4D results from Singapore Pools at 6:30pm SGT and updates a JSON file. Static frontend is hosted via GitHub Pages.

## Features

- Scrapes draw date, number, 1st/2nd/3rd prizes, starter & consolation
- Saves into `data/result.json`
- Retry logic if results are not yet updated
- Auto-deployed viewer (dropdown + table)

## Repo Layout

```
.github/workflows/scrape.yml    → GitHub Actions
scripts/main.sh                 → Bash scraper (curl + pup + jq)
data/result.json                → JSON results
data/raw_result.html            → Debug copy of scraped HTML
public/index.html               → GitHub Pages frontend
```
