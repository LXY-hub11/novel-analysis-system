"""
Data import script: Import novels from JSON to Django database.
"""
import os
import sys
import django
import json
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'novel_analysis.settings')
django.setup()

from apps.novels.models import Novel, Category
from django.contrib.auth.models import User


def load_json_data(json_path):
    """Load novel data from JSON file"""
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def import_categories(novels_data):
    """Import categories from novels data"""
    categories = set()
    for novel in novels_data:
        if novel.get('category'):
            categories.add(novel['category'])

    for cat_name in categories:
        Category.objects.get_or_create(name=cat_name)
        print(f"Category: {cat_name}")

    print(f"Imported {len(categories)} categories")
    return categories


def import_novels(novels_data):
    """Import novels from JSON data to database"""
    novels_created = 0
    novels_updated = 0

    for novel_data in novels_data:
        try:
            title = novel_data.get('title', '').strip()
            if not title:
                continue

            category_name = novel_data.get('category', '未分类')
            category, _ = Category.objects.get_or_create(name=category_name)

            crawl_time_str = novel_data.get('crawl_time', '')
            try:
                crawl_time = datetime.strptime(crawl_time_str, '%Y-%m-%d %H:%M:%S')
            except:
                crawl_time = datetime.now()

            word_count_str = novel_data.get('word_count', '0')
            try:
                word_count = int(word_count_str) if word_count_str else 0
            except:
                word_count = 0

            clicks_str = novel_data.get('clicks', '0')
            try:
                clicks = int(clicks_str) if clicks_str else 0
            except:
                clicks = 0

            collects_str = novel_data.get('collects', '0')
            try:
                collects = int(collects_str) if collects_str else 0
            except:
                collects = 0

            recommends_str = novel_data.get('recommends', '0')
            try:
                recommends = int(recommends_str) if recommends_str else 0
            except:
                recommends = 0

            novel, created = Novel.objects.update_or_create(
                title=title,
                defaults={
                    'author': novel_data.get('author', '未知作者'),
                    'category': category,
                    'description': novel_data.get('description', ''),
                    'word_count': word_count,
                    'update_status': novel_data.get('update_status', ''),
                    'source': novel_data.get('source', '起点中文网'),
                    'platform': novel_data.get('platform', '起点中文网'),
                    'clicks': clicks,
                    'collects': collects,
                    'recommends': recommends,
                    'last_chapter': novel_data.get('last_chapter', ''),
                    'crawl_time': crawl_time,
                }
            )

            if created:
                novels_created += 1
            else:
                novels_updated += 1

        except Exception as e:
            print(f"Error importing novel '{title}': {e}")
            continue

    return novels_created, novels_updated


def create_test_user():
    """Create a test user for testing"""
    username = 'testuser'
    email = 'test@example.com'
    password = 'test123456'

    if not User.objects.filter(username=username).exists():
        user = User.objects.create_user(username, email, password)
        print(f"Test user created: {username}")
        return user
    else:
        print(f"Test user already exists: {username}")
        return User.objects.get(username=username)


def main():
    """Main import function"""
    print("="*60)
    print("NOVEL DATA IMPORT SCRIPT")
    print("="*60)

    json_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        '..',
        'novels_data.json'
    )

    print(f"\nLoading data from: {json_path}")

    if not os.path.exists(json_path):
        print(f"Error: JSON file not found at {json_path}")
        return

    novels_data = load_json_data(json_path)
    print(f"Loaded {len(novels_data)} novels from JSON")

    print("\n" + "-"*60)
    print("Step 1: Import Categories")
    print("-"*60)
    import_categories(novels_data)

    print("\n" + "-"*60)
    print("Step 2: Import Novels")
    print("-"*60)
    created, updated = import_novels(novels_data)
    print(f"\nNovels created: {created}")
    print(f"Novels updated: {updated}")

    print("\n" + "-"*60)
    print("Step 3: Create Test User")
    print("-"*60)
    create_test_user()

    print("\n" + "="*60)
    print("IMPORT COMPLETED!")
    print("="*60)

    total_novels = Novel.objects.count()
    total_categories = Category.objects.count()
    print(f"\nTotal novels in database: {total_novels}")
    print(f"Total categories in database: {total_categories}")


if __name__ == '__main__':
    main()
