# Company Review Scraper 🔍

Automated scraper for collecting and analyzing company reviews from multiple sources.

## Features ✨

- Collects reviews from Google Maps
- Detects employment-related reviews
- Automated daily runs via GitHub Actions
- CSV output for easy analysis
- Duplicate detection
- Employment relevance scoring

## Setup 🛠️

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Add your Google Maps API key to GitHub Secrets as `GOOGLE_MAPS_API_KEY`

## Usage 🚀

The scraper runs automatically every day at midnight UTC via GitHub Actions.
You can also trigger it manually from the Actions tab.

### Manual Run
```bash
python test_scraper.py
```

## Output 📊

Reviews are saved to `company_reviews_new.csv` with the following information:
- Company name
- Industry
- Rating
- Pros/Cons
- Position
- Timestamp

## Contributing 🤝

Feel free to open issues or submit pull requests! 