"""
Enriched novel data generator.
Generates realistic multi-platform novel data for analysis and visualization.
"""
import json
import random
import os
from datetime import datetime, timedelta


class NovelDataGenerator:
    """Generate realistic multi-platform novel data"""

    PLATFORMS = [
        {'name': '起点中文网', 'domain': 'qidian.com', 'type': 'male'},
        {'name': '番茄小说', 'domain': 'fanqienovel.com', 'type': 'mixed'},
        {'name': '晋江文学城', 'domain': 'jjwxc.net', 'type': 'female'},
        {'name': '纵横中文网', 'domain': 'zongheng.com', 'type': 'male'},
        {'name': '七猫小说', 'domain': 'qimao.com', 'type': 'mixed'},
        {'name': '飞卢小说', 'domain': 'faloo.com', 'type': 'male'},
        {'name': '17k小说网', 'domain': '17k.com', 'type': 'mixed'},
        {'name': '潇湘书院', 'domain': 'xxsy.net', 'type': 'female'},
    ]

    CATEGORIES = {
        '玄幻': ['东方玄幻', '异世大陆', '高武世界', '神话修真'],
        '仙侠': ['古典仙侠', '现代修真', '洪荒封神', '幻想修仙'],
        '都市': ['都市生活', '都市异能', '青春校园', '职场商战'],
        '科幻': ['星际文明', '未来世界', '时空穿梭', '末世危机'],
        '历史': ['架空历史', '秦汉三国', '两晋隋唐', '宋元明清'],
        '军事': ['战争幻想', '谍战特工', '抗战烽火', '军旅生涯'],
        '游戏': ['电子竞技', '虚拟网游', '游戏异界', '游戏系统'],
        '竞技': ['体育竞技', '篮球风云', '足球梦想', '格斗搏击'],
        '悬疑': ['悬疑侦探', '诡秘悬疑', '灵异恐怖', '心理罪案'],
        '言情': ['古代言情', '现代言情', '豪门总裁', '纯爱青春'],
        '轻小说': ['原生幻想', '青春日常', '搞笑吐槽', '同人衍生'],
        '奇幻': ['史诗奇幻', '剑与魔法', '黑暗幻想', '幽默奇幻'],
        '武侠': ['传统武侠', '新派武侠', '国术古武', '江湖恩怨'],
        '现实': ['社会悬疑', '时代变迁', '人间百态', '家庭伦理'],
        '短篇': ['微型小说', '短篇合集', '睡前故事', '散文随笔'],
    }

    AUTHORS_POOL = [
        '天下归元', '烽火戏诸侯', '猫腻', '辰东', '天蚕土豆', '唐家三少',
        '我吃西红柿', '萧鼎', '忘语', '耳根', '烟雨江南', '江南',
        '南派三叔', '刘慈欣', '马伯庸', '紫金陈', '九鹭非香', 'Priest',
        '墨香铜臭', '淮上', '巫哲', '木苏里', '漫漫何其多', '梦溪石',
        '会说话的肘子', '老鹰吃小鸡', '爱潜水的乌贼', '宅猪', '血染卫生棉',
        '横扫天涯', '净无痕', '风凌天下', '血红', '跃千愁', '愤怒的香蕉',
        '陈词懒调', '远瞳', '二目', '齐佩甲', '舍庄', '悠然',
        '柳下挥', '烽火', '骁骑校', '孑与2', '三戒大师', '贼道三痴',
        '月关', '天使奥斯卡', '更俗', '酒徒', '常书欣', '卓牧闲',
        '半醉游子', '十里剑神', '剑客浪心', '烟雨如江南', '叶落无心',
        '水千澈', '苏小暖', '吱吱', '冬天的柳叶', '云霓', '闲听落花',
        '意千重', '吱吱', '莞尔wr', '林家成', '希行', '祈祷君',
        '玄幻妖孽', '开局玄幻小猪', '玄幻梦想家', '长青画羡鱼', '红袖添香',
    ]

    NOUNS = ['剑', '刀', '天', '龙', '凤', '神', '魔', '仙', '帝', '皇',
             '星', '海', '云', '风', '雷', '火', '冰', '影', '灵', '魂',
             '道', '法', '术', '气', '元', '真', '玄', '极', '圣', '王']

    ADJECTIVES = ['绝世', '万古', '无上', '不朽', '逆天', '吞噬', '苍穹', '九霄',
                  '混沌', '鸿蒙', '永恒', '无双', '独尊', '凌天', '傲世', '霸天']

    STATUSES = ['连载中', '已完结', '连载中', '连载中', '连载中', '已完结', '连载中',
                '连载中', '连载中', '连载中', '已完结', '连载中', '连载中']

    def __init__(self, seed=42):
        random.seed(seed)

    def generate_title(self, category):
        """Generate a realistic novel title"""
        patterns = [
            lambda: f"{random.choice(self.ADJECTIVES)}{random.choice(self.NOUNS)}{random.choice(self.NOUNS)}",
            lambda: f"{random.choice(self.ADJECTIVES)}{random.choice(self.NOUNS)}",
            lambda: f"{random.choice(self.NOUNS)}{random.choice(self.ADJECTIVES)}",
            lambda: f"{random.choice(self.NOUNS)}{random.choice(self.NOUNS)}{random.choice(self.NOUNS)}",
            lambda: f"重生之{random.choice(self.ADJECTIVES)}{random.choice(self.NOUNS)}",
            lambda: f"穿越之{random.choice(self.ADJECTIVES)}{random.choice(self.NOUNS)}",
            lambda: f"我在{random.choice(self.NOUNS)}界{random.choice(['修仙', '成神', '称帝', '逆袭', '求生'])}",
            lambda: f"从{random.choice(self.NOUNS)}开始的{random.choice(self.NOUNS)}之路",
            lambda: f"{random.choice(self.NOUNS)}{random.choice(self.NOUNS)}：{random.choice(self.ADJECTIVES)}{random.choice(self.NOUNS)}",
            lambda: f"{random.choice(self.ADJECTIVES)}：我的{random.choice(self.NOUNS)}{random.choice(self.NOUNS)}",
            lambda: f"我的{random.choice(self.NOUNS)}能{random.choice(['修炼', '吞噬', '进化', '暴击', '复制'])}",
            lambda: f"开局{random.choice(['一把', '一个', '一只', '一本', '一套'])}{random.choice(self.NOUNS)}",
        ]
        return random.choice(patterns)()

    def generate_description(self, title, category, author):
        """Generate realistic novel description"""
        templates = [
            f"一个普通少年，意外获得了{random.choice(self.ADJECTIVES)}系统，从此踏上了一条不平凡的修炼之路。在这个{category}的世界里，他能否一步步成长为{random.choice(self.NOUNS)}强者？且看{title}为你揭晓。",
            f"当{random.choice(self.NOUNS)}降临，天地大变。少年{author}从微末中崛起，手握{random.choice(self.ADJECTIVES)}{random.choice(self.NOUNS)}，在这乱世中书写属于自己的传奇。",
            f"穿越到异世界，成为一个{random.choice(self.NOUNS)}宗门的杂役弟子，{author}凭借着前世的记忆和智慧，一步步在{category}的世界里搅动风云。",
            f"重活一世，{author}决心不再做那个默默无闻的小人物。带着前世的经验，他要在{category}的世界里，开创属于自己的{random.choice(self.NOUNS)}帝国。",
            f"这是一个{category}为尊的世界。{author}出生在一个偏远小城，却怀揣着成为{random.choice(self.NOUNS)}的梦想。机缘巧合下，他得到了一本{random.choice(self.ADJECTIVES)}秘籍……",
            f"{title}讲述了在{category}世界中，主角从一介凡人开始，经历无数艰难险阻，最终成就{random.choice(self.NOUNS)}霸业的故事。热血、感动、友情与爱情交织。",
            f"天地不仁，以万物为刍狗。在这{category}的时代，{author}不信命，不认命。他要靠自己的力量，打破命运的枷锁，书写一段{random.choice(self.ADJECTIVES)}传奇。",
            f"当{category}的世界与现实交织，一个普通青年{author}发现了隐藏在平凡生活中的惊天秘密。从此，他的生活发生了翻天覆地的变化。",
            f"史上最{random.choice(self.ADJECTIVES)}的{category}故事！主角{author}带着{random.choice(self.ADJECTIVES)}光环，一路碾压，爽感十足，不容错过！",
            f"在{category}的世界观下，{author}构建了一个宏大的宇宙体系。{title}不仅是一部小说，更是一幅波澜壮阔的史诗画卷。",
        ]
        desc = random.choice(templates)
        if random.random() > 0.6:
            desc += random.choice([
                " PS：本书节奏明快，爽点满满，欢迎收藏阅读！",
                " PS：已有百万字完本作品，品质保证。",
                " PS：新书求收藏、求推荐、求月票！",
                " PS：每日两更，风雨无阻，欢迎追读。",
            ])
        return desc

    def generate_novel(self, platform, category):
        """Generate a single complete novel entry"""
        title = self.generate_title(category)
        author = random.choice(self.AUTHORS_POOL)

        # Word count distribution
        word_count_dist = random.choices(
            [50_000, 150_000, 500_000, 1_200_000, 2_500_000, 4_000_000, 6_000_000],
            weights=[5, 15, 25, 25, 15, 10, 5]
        )[0]
        word_count = max(10000, int(random.gauss(word_count_dist, word_count_dist * 0.5)))

        # Popularity metrics by platform
        base_popularity = {
            '起点中文网': (500, 50000),
            '番茄小说': (800, 80000),
            '晋江文学城': (400, 40000),
            '纵横中文网': (300, 30000),
            '七猫小说': (600, 60000),
            '飞卢小说': (350, 35000),
            '17k小说网': (250, 25000),
            '潇湘书院': (300, 30000),
        }

        min_click, max_click = base_popularity.get(platform, (200, 20000))
        clicks = max(10, int(random.gauss((min_click + max_click) // 2, max_click // 3)))
        clicks = min(clicks, max_click * 3)

        collect_rate = random.uniform(0.02, 0.25)
        collects = int(clicks * collect_rate)

        recommend_rate = random.uniform(0.01, 0.15)
        recommends = int(clicks * recommend_rate)

        status = random.choice(self.STATUSES)
        last_chapter = f"第{random.randint(100, 3000)}章 {self.generate_title(category)}" if status == '连载中' else ''

        days_ago = random.randint(0, 90)
        crawl_time = (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d %H:%M:%S')

        return {
            'title': title,
            'author': author,
            'category': category,
            'description': self.generate_description(title, category, author),
            'word_count': word_count,
            'update_status': status,
            'source': platform,
            'platform': platform,
            'clicks': clicks,
            'collects': collects,
            'recommends': recommends,
            'last_chapter': last_chapter,
            'crawl_time': crawl_time,
        }

    def generate_dataset(self, novels_per_platform=80):
        """Generate full multi-platform dataset"""
        all_novels = []
        platform_categories = {}

        male_platforms = [p for p in self.PLATFORMS if p['type'] in ('male', 'mixed')]
        female_platforms = [p for p in self.PLATFORMS if p['type'] in ('female', 'mixed')]

        male_categories = ['玄幻', '仙侠', '都市', '科幻', '历史', '军事', '游戏', '竞技', '武侠', '奇幻']
        female_categories = ['言情', '轻小说', '现实', '短篇', '悬疑', '都市', '科幻', '历史', '奇幻']

        for platform_info in self.PLATFORMS:
            pname = platform_info['name']
            ptype = platform_info['type']
            categories = male_categories if ptype == 'male' else (female_categories if ptype == 'female' else male_categories + female_categories)

            weighted_categories = categories.copy()
            if ptype == 'male':
                weighted_categories += ['玄幻', '仙侠', '都市'] * 2
            elif ptype == 'female':
                weighted_categories += ['言情', '轻小说', '都市'] * 2

            platform_categories[pname] = categories

        for platform_info in self.PLATFORMS:
            pname = platform_info['name']
            ptype = platform_info['type']

            n_novels = novels_per_platform + random.randint(-15, 15)
            print(f"  Generating {n_novels} novels for {pname}...")

            categories = male_categories if ptype == 'male' else (female_categories if ptype == 'female' else male_categories + female_categories)

            if ptype == 'male':
                weighted = categories + ['玄幻', '仙侠', '都市'] * 3
            elif ptype == 'female':
                weighted = categories + ['言情', '轻小说', '都市'] * 3
            else:
                weighted = categories + ['玄幻', '都市', '言情'] * 2

            for _ in range(n_novels):
                cat = random.choice(weighted)
                novel = self.generate_novel(pname, cat)
                all_novels.append(novel)

        random.shuffle(all_novels)
        return all_novels

    def save_dataset(self, novels, filepath):
        """Save dataset to JSON file"""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(novels, f, ensure_ascii=False, indent=2)
        print(f"Saved {len(novels)} novels to {filepath}")


def generate_analytics_summary(novels):
    """Print analytics summary of generated data"""
    from collections import Counter

    platforms = Counter(n['platform'] for n in novels)
    categories = Counter(n['category'] for n in novels)
    statuses = Counter(n['update_status'] for n in novels)

    total_clicks = sum(n['clicks'] for n in novels)
    total_collects = sum(n['collects'] for n in novels)
    total_words = sum(n['word_count'] for n in novels)

    print("\n" + "=" * 60)
    print("DATA ANALYTICS SUMMARY")
    print("=" * 60)

    print(f"\nTotal novels: {len(novels)}")
    print(f"Total clicks: {total_clicks:,}")
    print(f"Total collects: {total_collects:,}")
    print(f"Total words: {total_words:,}")

    print(f"\n--- Platform Distribution ---")
    for platform, count in platforms.most_common():
        bar = '█' * (count // 5)
        print(f"  {platform:12s}: {count:4d} {bar}")

    print(f"\n--- Category Distribution ---")
    for cat, count in categories.most_common():
        bar = '█' * (count // 5)
        print(f"  {cat:8s}: {count:4d} {bar}")

    print(f"\n--- Status Distribution ---")
    for status, count in statuses.most_common():
        print(f"  {status}: {count} ({count/len(novels)*100:.1f}%)")

    print(f"\n--- Platform Averages ---")
    for platform in platforms:
        pnovels = [n for n in novels if n['platform'] == platform]
        if pnovels:
            avg_clicks = sum(n['clicks'] for n in pnovels) / len(pnovels)
            avg_collects = sum(n['collects'] for n in pnovels) / len(pnovels)
            avg_words = sum(n['word_count'] for n in pnovels) / len(pnovels)
            print(f"  {platform:12s}: avg_clicks={avg_clicks:,.0f}  avg_collects={avg_collects:,.0f}  avg_words={avg_words:,.0f}")


def main():
    print("=" * 60)
    print("ENRICHED NOVEL DATA GENERATOR")
    print("=" * 60)

    generator = NovelDataGenerator(seed=42)
    novels = generator.generate_dataset(novels_per_platform=80)

    output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
    output_file = os.path.join(output_dir, 'enriched_novels.json')

    # Also update the main novels_data.json
    main_output = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '..', 'novels_data.json')

    generator.save_dataset(novels, output_file)
    generator.save_dataset(novels, main_output)

    generate_analytics_summary(novels)

    print(f"\nData files generated:")
    print(f"  {output_file}")
    print(f"  {main_output}")


if __name__ == '__main__':
    main()
