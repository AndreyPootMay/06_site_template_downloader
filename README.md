Here's a professional `README.md` for your project:

```markdown
# Web Template Downloader

A Python CLI tool to download complete website templates (HTML, CSS, JS, images, fonts) while maintaining the original directory structure.

## Features

- Downloads all HTML pages linked from the starting URL
- Recursively downloads all static assets (CSS, JavaScript, images, fonts)
- Extracts assets referenced in CSS files (background images, fonts, etc.)
- Preserves original directory structure
- Saves templates in organized `templates/` directory
- English-language console output
- Skip already downloaded files

## Requirements

- Python 3.6+
- Required packages:
  - requests
  - beautifulsoup4

## Installation

1. Clone the repository or download the script:
```bash
git clone https://github.com/AndreyPootMay/web-template-downloader.git
cd web-template-downloader
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate.bat  # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

```bash
python downloader.py [OUTPUT_FOLDER_NAME] [TEMPLATE_URL]
```

Example:
```bash
python downloader.py folder_name website.com/index.html
```

This will create:
```
templates/
└── traveltrek/
    ├── index.html
    ├── assets/
    │   ├── css/
    │   ├── js/
    │   └── images/
    └── about.html
```

## How It Works

1. Starts with the provided URL (typically index.html)
2. Analyzes HTML to find:
   - Links to other HTML pages
   - References to static assets (CSS, JS, images)
3. Downloads each asset while preserving paths
4. Extracts additional assets from CSS files
5. Organizes everything in the `templates/` directory

## Limitations

- Only downloads resources from the same domain
- Doesn't handle dynamic content (PHP, ASP, etc.)
- May not capture assets loaded via JavaScript

## License

MIT License - Free for personal and commercial use

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss proposed changes.