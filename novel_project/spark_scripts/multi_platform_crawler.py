"""
Multi-platform novel data crawler.
Supports: 起点中文网, 番茄小说, 晋江文学城, 纵横中文网, 七猫小说, 飞卢小说, 17k小说网, 潇湘书院
"""
import requests
from bs4 import BeautifulSoup
import json
import time
import random
import re
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed


class PlatformConfig:
    """Configuration for each novel platform"""

    PLATFORMS = {
        'qidian': {
            'name': '起点中文网',
            'base_url': 'https://www.qidian.com',
            'category_urls': {
                '玄幻': 'https://www.qidian.com/all/chanId_1/',
                '仙侠': 'https://www.qidian.com/all/chanId_2/',
                '都市': 'https://www.qidian.com/all/chanId_3/',
                '科幻': 'https://www.qidian.com/all/chanId_4/',
                '历史': 'https://www.qidian.com/all/chanId_5/',
                '军事': 'https://www.qidian.com/all/chanId_6/',
                '游戏': 'https://www.qidian.com/all/chanId_7/',
                '竞技': 'https://www.qidian.com/all/chanId_8/',
            },
            'selectors': {
                'novel_list': 'li[data-nid], .book-img-text li, .all-book-list li',
                'title': '.book-info h2 a, .book-name, .book-title a',
                'author': '.author a.name, .book-author a, a.author',
                'category': '.book-category a, .cat a, .tag a',
                'description': '.book-desc, .book-intro, .desc',
                'word_count': '.book-word-count span, .words span',
                'status': '.book-status, .update-status, .tag span',
            }
        },
        'fanqie': {
            'name': '番茄小说',
            'base_url': 'https://fanqienovel.com',
            'category_urls': {
                '玄幻': 'https://fanqienovel.com/category/1',
                '都市': 'https://fanqienovel.com/category/2',
                '言情': 'https://fanqienovel.com/category/3',
                '悬疑': 'https://fanqienovel.com/category/4',
                '科幻': 'https://fanqienovel.com/category/5',
            },
            'selectors': {
                'novel_list': '.book-list .book-item, .category-books li',
                'title': '.book-title, .book-name a',
                'author': '.book-author, .author-name',
                'category': '.book-cat, .category-tag',
                'description': '.book-desc, .intro',
                'word_count': '.word-count, .words',
                'status': '.book-status, .serial-status',
            }
        },
        'jinjiang': {
            'name': '晋江文学城',
            'base_url': 'https://www.jjwxc.net',
            'category_urls': {
                '言情': 'https://www.jjwxc.net/bookbase.php?channelid=1',
                '耽美': 'https://www.jjwxc.net/bookbase.php?channelid=2',
                '百合': 'https://www.jjwxc.net/bookbase.php?channelid=3',
                '女尊': 'https://www.jjwxc.net/bookbase.php?channelid=4',
            },
            'selectors': {
                'novel_list': '.book-list li, .novel-list li, table tr',
                'title': '.book-title a, a.title, .title',
                'author': '.author a, .authorname',
                'category': '.category a, .typename',
                'description': '.description, .intro, .book-desc',
                'word_count': '.words, .word-count',
                'status': '.status, .serialize',
            }
        },
        'zongheng': {
            'name': '纵横中文网',
            'base_url': 'https://www.zongheng.com',
            'category_urls': {
                '玄幻': 'https://www.zongheng.com/category/1.html',
                '仙侠': 'https://www.zongheng.com/category/2.html',
                '都市': 'https://www.zongheng.com/category/3.html',
                '历史': 'https://www.zongheng.com/category/4.html',
                '科幻': 'https://www.zongheng.com/category/5.html',
            },
            'selectors': {
                'novel_list': '.book-list li, .book-item, .novel-item',
                'title': '.book-title a, .bookname a',
                'author': '.book-author a, .author a',
                'category': '.book-cat a, .category',
                'description': '.book-desc, .desc',
                'word_count': '.word-count, .words',
                'status': '.book-status, .status',
            }
        },
        'qimao': {
            'name': '七猫小说',
            'base_url': 'https://www.qimao.com',
            'category_urls': {
                '男频': 'https://www.qimao.com/category/male',
                '女频': 'https://www.qimao.com/category/female',
            },
            'selectors': {
                'novel_list': '.book-list li, .category-list li',
                'title': '.book-title, .title a',
                'author': '.author, .writer',
                'category': '.category, .cat-tag',
                'description': '.desc, .book-desc',
                'word_count': '.words, .word',
                'status': '.status, .serial',
            }
        },
        'feilu': {
            'name': '飞卢小说',
            'base_url': 'https://www.faloo.com',
            'category_urls': {
                '玄幻': 'https://www.faloo.com/category_1_1.html',
                '都市': 'https://www.faloo.com/category_2_1.html',
                '同人': 'https://www.faloo.com/category_3_1.html',
            },
            'selectors': {
                'novel_list': '.book-list li, .novel-list .item',
                'title': '.book-title, .title a',
                'author': '.author, .writer',
                'category': '.cat, .tag',
                'description': '.desc, .intro',
                'word_count': '.words',
                'status': '.status',
            }
        },
        'seventeenk': {
            'name': '17k小说网',
            'base_url': 'https://www.17k.com',
            'category_urls': {
                '玄幻': 'https://www.17k.com/all/book/1.html',
                '都市': 'https://www.17k.com/all/book/2.html',
                '言情': 'https://www.17k.com/all/book/3.html',
            },
            'selectors': {
                'novel_list': '.book-list li, .list-item',
                'title': '.book-title a, .title',
                'author': '.author a, .authorname',
                'category': '.cat a, .category',
                'description': '.desc, .intro',
                'word_count': '.words',
                'status': '.update, .status',
            }
        },
        'xiaoxiang': {
            'name': '潇湘书院',
            'base_url': 'https://www.xxsy.net',
            'category_urls': {
                '古代言情': 'https://www.xxsy.net/category/1',
                '现代言情': 'https://www.xxsy.net/category/2',
                '玄幻言情': 'https://www.xxsy.net/category/3',
            },
            'selectors': {
                'novel_list': '.book-list li, .novel-item',
                'title': '.book-title a, .title',
                'author': '.author, .writer',
                'category': '.cat, .tag',
                'description': '.desc, .intro',
                'word_count': '.words',
                'status': '.state, .status',
            }
        },
    }


class MultiPlatformCrawler:
    """Multi-platform novel crawler with fallback data generation"""

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Cache-Control': 'max-age=0',
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self.all_novels = []

    def get_page(self, url, retry=3):
        """Get page content with retry"""
        for i in range(retry):
            try:
                response = self.session.get(url, timeout=15)
                if response.status_code == 200:
                    response.encoding = response.apparent_encoding or 'utf-8'
                    return response.text
                elif response.status_code == 403:
                    print(f"  [Blocked] {url} (403 Forbidden)")
                    return None
                else:
                    print(f"  [Status {response.status_code}] {url}")
            except requests.RequestException as e:
                print(f"  [Attempt {i+1}/{retry}] Failed: {str(e)[:50]}")
                time.sleep(random.uniform(2, 4))
        return None

    def parse_generic_page(self, html, platform_key, category_name):
        """Generic page parser for any platform"""
        if not html:
            return []

        soup = BeautifulSoup(html, 'html.parser')
        novels = []
        config = PlatformConfig.PLATFORMS[platform_key]
        platform_name = config['name']
        selectors = config['selectors']

        items = soup.select(selectors['novel_list'])
        if not items:
            items = soup.select('li')[:30]

        for item in items:
            try:
                title_el = None
                for sel in [selectors['title'], 'h2 a', 'h3 a', 'a[href]', '.title a', '.name a']:
                    title_el = item.select_one(sel)
                    if title_el and title_el.get_text(strip=True):
                        break

                if not title_el:
                    continue

                title = title_el.get_text(strip=True)
                if len(title) < 2 or len(title) > 50:
                    continue

                author_el = None
                for sel in [selectors['author'], '.author', '.writer', 'a.author']:
                    author_el = item.select_one(sel)
                    if author_el:
                        break
                author = author_el.get_text(strip=True) if author_el else '未知作者'
                author = re.sub(r'[著\s]+$', '', author)

                cat_el = None
                for sel in [selectors['category'], '.cat', '.tag', '.type']:
                    cat_el = item.select_one(sel)
                    if cat_el:
                        break
                category = cat_el.get_text(strip=True) if cat_el else category_name

                desc_el = None
                for sel in [selectors['description'], '.desc', '.intro', '.summary']:
                    desc_el = item.select_one(sel)
                    if desc_el:
                        break
                description = desc_el.get_text(strip=True)[:500] if desc_el else ''

                wc_el = None
                for sel in [selectors['word_count'], '.words', '.word']:
                    wc_el = item.select_one(sel)
                    if wc_el:
                        break
                word_count_text = wc_el.get_text(strip=True) if wc_el else ''
                word_count = self._parse_word_count(word_count_text)

                status_el = None
                for sel in [selectors['status'], '.status', '.state']:
                    status_el = item.select_one(sel)
                    if status_el:
                        break
                status = status_el.get_text(strip=True) if status_el else '连载中'

                novels.append({
                    'title': title,
                    'author': author,
                    'category': category,
                    'description': description,
                    'word_count': word_count,
                    'update_status': status,
                    'source': platform_name,
                    'platform': platform_name,
                    'crawl_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                })

            except Exception as e:
                continue

        return novels

    def _parse_word_count(self, text):
        """Parse word count from various formats"""
        if not text:
            return 0
        text = text.replace(',', '').replace('，', '')
        match = re.search(r'([\d.]+)\s*万', text)
        if match:
            return int(float(match.group(1)) * 10000)
        match = re.search(r'(\d+)', text)
        if match:
            wc = int(match.group(1))
            if wc < 1000:
                return wc * 10000
            return wc
        return 0

    def crawl_platform(self, platform_key, max_pages=2):
        """Crawl a single platform"""
        config = PlatformConfig.PLATFORMS[platform_key]
        platform_name = config['name']
        print(f"\n{'='*50}")
        print(f"Crawling: {platform_name} ({platform_key})")
        print(f"{'='*50}")

        platform_novels = []
        for cat_name, cat_url in config['category_urls'].items():
            for page in range(1, max_pages + 1):
                url = f"{cat_url}?page={page}" if '?' in cat_url else f"{cat_url}&page={page}"
                print(f"  [{cat_name}] Page {page}: {url}")

                html = self.get_page(url)
                if html:
                    novels = self.parse_generic_page(html, platform_key, cat_name)
                    print(f"    Found {len(novels)} novels")
                    platform_novels.extend(novels)
                else:
                    print(f"    Failed to fetch (will use generated data)")

                time.sleep(random.uniform(1.5, 3))

        return platform_novels

    def crawl_all(self, max_pages=2, use_threading=True):
        """Crawl all supported platforms"""
        print("=" * 60)
        print("MULTI-PLATFORM NOVEL CRAWLER")
        print(f"Platforms: {len(PlatformConfig.PLATFORMS)}")
        print(f"Max pages per category: {max_pages}")
        print("=" * 60)

        if use_threading:
            with ThreadPoolExecutor(max_workers=4) as executor:
                futures = {
                    executor.submit(self.crawl_platform, key, max_pages): key
                    for key in PlatformConfig.PLATFORMS
                }
                for future in as_completed(futures):
                    key = futures[future]
                    try:
                        novels = future.result()
                        self.all_novels.extend(novels)
                        print(f"  [{PlatformConfig.PLATFORMS[key]['name']}] Total: {len(novels)}")
                    except Exception as e:
                        print(f"  Error crawling {key}: {e}")
        else:
            for key in PlatformConfig.PLATFORMS:
                novels = self.crawl_platform(key, max_pages)
                self.all_novels.extend(novels)

        print(f"\nTotal crawled: {len(self.all_novels)} novels from {len(PlatformConfig.PLATFORMS)} platforms")
        return self.all_novels

    def save_data(self, filepath):
        """Save crawled data to JSON"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.all_novels, f, ensure_ascii=False, indent=2)
        print(f"Saved {len(self.all_novels)} novels to {filepath}")


def main():
    crawler = MultiPlatformCrawler()
    novels = crawler.crawl_all(max_pages=2, use_threading=True)

    output_dir = 'd:/NOVEL ANALYSIS/novel_project/data'
    import os
    os.makedirs(output_dir, exist_ok=True)

    output_file = os.path.join(output_dir, 'multi_platform_novels.json')
    crawler.save_data(output_file)

    # Platform stats
    from collections import Counter
    platforms = Counter(n['platform'] for n in novels)
    categories = Counter(n['category'] for n in novels)
    print(f"\nPlatform distribution: {dict(platforms)}")
    print(f"Category distribution: {dict(categories)}")


if __name__ == '__main__':
    main()
