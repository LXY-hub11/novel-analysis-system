"""
Novel data crawler for Qidian website.
"""
import requests
from bs4 import BeautifulSoup
import json
import time
import random
from datetime import datetime


class NovelCrawler:
    """Crawler for novel websites"""

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def get_page(self, url, retry=3):
        """Get page content with retry logic"""
        for i in range(retry):
            try:
                response = self.session.get(url, timeout=10)
                if response.status_code == 200:
                    return response.text
                else:
                    print(f"Status code {response.status_code} for {url}")
            except requests.RequestException as e:
                print(f"Request failed (attempt {i+1}/{retry}): {e}")
                time.sleep(random.uniform(1, 3))

        return None

    def parse_novel_list_page(self, html):
        """Parse novel list page"""
        if not html:
            return []

        soup = BeautifulSoup(html, 'html.parser')
        novels = []

        novel_items = soup.select('.novel-item') or soup.select('.book-item') or soup.select('li[data-nid]')

        for item in novel_items:
            try:
                title = item.select_one('.title a') or item.select_one('a.title')
                author = item.select_one('.author') or item.select_one('a.author')
                category = item.select_one('.category') or item.select_one('.tag')
                description = item.select_one('.desc') or item.select_one('.description')

                if title:
                    novel = {
                        'title': title.get_text(strip=True),
                        'author': author.get_text(strip=True) if author else '未知作者',
                        'category': category.get_text(strip=True) if category else '未分类',
                        'description': description.get_text(strip=True) if description else '',
                        'source': '起点中文网',
                        'platform': '起点中文网',
                        'crawl_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    }
                    novels.append(novel)

            except Exception as e:
                print(f"Error parsing novel item: {e}")
                continue

        return novels

    def crawl_category_page(self, category_url, pages=1):
        """Crawl novels from a category page"""
        all_novels = []

        for page in range(1, pages + 1):
            url = f"{category_url}?page={page}"
            print(f"Crawling page {page}: {url}")

            html = self.get_page(url)
            novels = self.parse_novel_list_page(html)
            all_novels.extend(novels)

            time.sleep(random.uniform(1, 2))

        return all_novels

    def crawl_novel_detail(self, novel_url):
        """Crawl detailed information of a single novel"""
        html = self.get_page(novel_url)
        if not html:
            return None

        soup = BeautifulSoup(html, 'html.parser')

        try:
            title = soup.select_one('h1.book-title') or soup.select_one('h1')
            author = soup.select_one('.author-name') or soup.select_one('.author a')
            category = soup.select_one('.category a') or soup.select_one('.book-category a')
            description = soup.select_one('.book-description') or soup.select_one('.desc')
            word_count = soup.select_one('.word-count') or soup.select_one('.words')
            status = soup.select_one('.status') or soup.select_one('.update-status')

            novel = {
                'title': title.get_text(strip=True) if title else '',
                'author': author.get_text(strip=True) if author else '',
                'category': category.get_text(strip=True) if category else '',
                'description': description.get_text(strip=True) if description else '',
                'word_count': word_count.get_text(strip=True) if word_count else '0',
                'update_status': status.get_text(strip=True) if status else '',
                'source': '起点中文网',
                'platform': '起点中文网',
                'crawl_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            }

            return novel

        except Exception as e:
            print(f"Error parsing novel detail: {e}")
            return None

    def save_to_json(self, novels, filepath):
        """Save novels data to JSON file"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(novels, f, ensure_ascii=False, indent=2)
        print(f"Saved {len(novels)} novels to {filepath}")

    def load_from_json(self, filepath):
        """Load novels data from JSON file"""
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)


def crawl_main():
    """Main crawling function"""
    crawler = NovelCrawler()

    output_file = 'd:/NOVEL ANALYSIS/novel_project/data/crawled_novels.json'

    existing_novels = []
    try:
        existing_novels = crawler.load_from_json(output_file)
        print(f"Loaded {len(existing_novels)} existing novels")
    except FileNotFoundError:
        print("No existing data found, starting fresh")

    sample_categories = [
        'https://www.qidian.com/all/chanId_1/',  # 玄幻
        'https://www.qidian.com/all/chanId_2/',  # 仙侠
        'https://www.qidian.com/all/chanId_3/',  # 都市
        'https://www.qidian.com/all/chanId_4/',  # 科幻
    ]

    for category_url in sample_categories:
        print(f"\nCrawling category: {category_url}")
        novels = crawler.crawl_category_page(category_url, pages=2)
        print(f"Found {len(novels)} novels in this category")
        existing_novels.extend(novels)

        time.sleep(random.uniform(2, 5))

    crawler.save_to_json(existing_novels, output_file)
    print(f"\nTotal novels collected: {len(existing_novels)}")


if __name__ == '__main__':
    crawl_main()
