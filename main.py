import argparse
import os
import re
import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

class TemplateDownloader:
    def __init__(self, base_url, output_folder):
        self.base_url = base_url.rstrip('/')
        self.output_folder = os.path.join('templates', output_folder)  # Modified path
        self.visited_urls = set()
        self.assets = set()
        self.queue = []

        parsed_base = urlparse(self.base_url)
        self.domain = parsed_base.netloc
        self.base_path = self._get_base_path(parsed_base.path)

        os.makedirs(self.output_folder, exist_ok=True)

    def _get_base_path(self, original_path):
        """Determine template base path"""
        if '.' in os.path.basename(original_path):
            return os.path.dirname(original_path) + '/'
        return original_path.rstrip('/') + '/'

    def sanitize_url(self, url):
        return urljoin(self.base_url, url).split('#')[0].split('?')[0]

    def is_valid_url(self, url):
        parsed = urlparse(url)
        path = parsed.path
        return (
            parsed.netloc == self.domain and
            path.startswith(self.base_path) and
            not path.endswith(('.php', '.asp', '.aspx'))
        )

    def get_relative_path(self, url):
        parsed = urlparse(url)
        full_path = parsed.path
        relative_path = full_path[len(self.base_path):] if full_path.startswith(self.base_path) else ''
        return os.path.join(self.output_folder, relative_path)

    def save_content(self, url, content, is_html=False):
        path = self.get_relative_path(url)

        if is_html:
            if not url.endswith('.html'):
                if not os.path.splitext(path)[1]:
                    path = os.path.join(path, 'index.html') if url.endswith('/') else path + '.html'

        os.makedirs(os.path.dirname(path), exist_ok=True)

        with open(path, 'wb') as f:
            f.write(content)
        return path

    def extract_css_assets(self, css_content, css_url):
        """Extract assets from CSS files"""
        assets = []
        pattern = re.compile(r"url\(['\"]?(.*?)['\"]?\)", re.IGNORECASE)
        for match in pattern.findall(css_content):
            asset_url = self.sanitize_url(match)
            if self.is_valid_url(asset_url) and asset_url not in self.assets:
                assets.append(asset_url)
                self.assets.add(asset_url)
        return assets

    def extract_assets(self, soup):
        assets = []
        tags = {
            'link': 'href',
            'script': 'src',
            'img': 'src',
            'source': 'src',
            'audio': 'src',
            'video': 'src',
            'embed': 'src',
            'meta': 'content'
        }

        for tag, attr in tags.items():
            for element in soup.find_all(tag, **{attr: True}):
                url = self.sanitize_url(element[attr])
                if self.is_valid_url(url) and url not in self.assets:
                    assets.append(url)
                    self.assets.add(url)
        return assets

    def process_html(self, url, content):
        soup = BeautifulSoup(content, 'html.parser')

        # Find links to other HTML pages
        for link in soup.find_all('a', href=True):
            new_url = self.sanitize_url(link['href'])
            if self.is_valid_url(new_url) and new_url not in self.visited_urls:
                self.queue.append(new_url)

        return self.extract_assets(soup)

    def download_asset(self, url):
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                path = self.save_content(url, response.content)
                print(f"  → Asset downloaded: {path}")

                # Check for CSS files to extract nested assets
                if 'text/css' in response.headers.get('Content-Type', ''):
                    css_assets = self.extract_css_assets(response.text, url)
                    for asset in css_assets:
                        self.download_asset(asset)

        except Exception as e:
            print(f"Error downloading asset {url}: {e}")

    def run(self):
        self.queue.append(self.base_url)

        while self.queue:
            current_url = self.queue.pop(0)

            if current_url in self.visited_urls:
                continue

            self.visited_urls.add(current_url)

            try:
                print(f"Downloading: {current_url}")
                response = requests.get(current_url, timeout=10)

                if response.status_code == 200:
                    is_html = 'text/html' in response.headers.get('Content-Type', '')
                    saved_path = self.save_content(current_url, response.content, is_html)

                    if is_html:
                        print(f"  → HTML saved at: {saved_path}")
                        assets = self.process_html(current_url, response.content)
                        for asset in assets:
                            self.download_asset(asset)
                    else:
                        print(f"  → File saved: {saved_path}")

            except Exception as e:
                print(f"Error processing {current_url}: {e}")

def main():
    parser = argparse.ArgumentParser(description='Web Template Downloader')
    parser.add_argument('folder', help='Output directory name')
    parser.add_argument('url', help='Template URL')
    args = parser.parse_args()

    # Create base templates directory if not exists
    os.makedirs('templates', exist_ok=True)

    downloader = TemplateDownloader(args.url, args.folder)
    downloader.run()
    print("\nDownload completed! Output directory:", os.path.abspath(downloader.output_folder))

if __name__ == '__main__':
    main()