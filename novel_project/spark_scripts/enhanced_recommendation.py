"""
Enhanced recommendation system with TF-IDF, cross-platform analysis, and multi-strategy fusion.
"""
import os
import json
import math
import re
from collections import Counter, defaultdict
from datetime import datetime

import numpy as np


class TFIDFVectorizer:
    """Simple TF-IDF vectorizer for Chinese text"""

    def __init__(self, max_features=500):
        self.max_features = max_features
        self.vocabulary = {}
        self.idf = {}

    def _tokenize(self, text):
        """Simple Chinese text tokenization using character bigrams"""
        if not text:
            return []
        text = re.sub(r'[^一-鿿]', ' ', text)
        chars = text.replace(' ', '')
        bigrams = [chars[i:i+2] for i in range(len(chars)-1)]
        unigrams = list(chars)
        return unigrams + bigrams

    def fit(self, documents):
        """Fit TF-IDF on document collection"""
        doc_count = len(documents)
        df = Counter()

        for doc in documents:
            tokens = set(self._tokenize(doc))
            df.update(tokens)

        top_tokens = [t for t, _ in df.most_common(self.max_features)]
        self.vocabulary = {t: i for i, t in enumerate(top_tokens)}

        for token, idx in self.vocabulary.items():
            self.idf[idx] = math.log((doc_count + 1) / (df.get(token, 1) + 1)) + 1

        return self

    def transform(self, documents):
        """Transform documents to TF-IDF vectors"""
        vectors = []
        for doc in documents:
            tokens = self._tokenize(doc)
            tf = Counter(tokens)
            vec = np.zeros(len(self.vocabulary))

            total = sum(tf.values()) or 1
            for token, count in tf.items():
                if token in self.vocabulary:
                    idx = self.vocabulary[token]
                    vec[idx] = (count / total) * self.idf.get(idx, 0)

            norm = np.linalg.norm(vec)
            if norm > 0:
                vec /= norm

            vectors.append(vec)

        return np.array(vectors)


class EnhancedRecommender:
    """Enhanced multi-strategy recommendation system"""

    def __init__(self, novels_data):
        self.novels = novels_data
        self.tfidf = None
        self.content_vectors = None
        self._build_index()

    def _build_index(self):
        """Build internal indices for fast lookup"""
        self.title_index = {}
        self.platform_index = defaultdict(list)
        self.category_index = defaultdict(list)
        self.author_index = defaultdict(list)

        for i, novel in enumerate(self.novels):
            title = novel.get('title', '')
            self.title_index[title] = i
            self.platform_index[novel.get('platform', '')].append(i)
            self.category_index[novel.get('category', '')].append(i)
            self.author_index[novel.get('author', '')].append(i)

    def fit_content_model(self):
        """Train TF-IDF model on novel descriptions"""
        descriptions = [n.get('description', '') for n in self.novels]
        self.tfidf = TFIDFVectorizer(max_features=500)
        self.tfidf.fit(descriptions)
        self.content_vectors = self.tfidf.transform(descriptions)
        print(f"Content model trained: {len(self.tfidf.vocabulary)} features for {len(self.novels)} novels")

    def content_similarity(self, novel_idx, candidate_indices):
        """Calculate content-based similarity using TF-IDF"""
        if self.content_vectors is None:
            self.fit_content_model()

        target_vec = self.content_vectors[novel_idx]
        similarities = []

        for idx in candidate_indices:
            if idx == novel_idx:
                continue
            sim = float(np.dot(target_vec, self.content_vectors[idx]))
            similarities.append((idx, sim))

        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities

    def attribute_similarity(self, novel1_idx, novel2_idx):
        """Calculate multi-attribute similarity between two novels"""
        n1 = self.novels[novel1_idx]
        n2 = self.novels[novel2_idx]
        score = 0.0

        if n1.get('category') == n2.get('category'):
            score += 3.0
        if n1.get('platform') == n2.get('platform'):
            score += 1.5
        if n1.get('author') == n2.get('author'):
            score += 2.5

        wc1 = n1.get('word_count', 0)
        wc2 = n2.get('word_count', 0)
        if wc1 > 0 and wc2 > 0:
            ratio = min(wc1, wc2) / max(wc1, wc2)
            score += ratio * 1.0

        return score

    def content_based_recommend(self, novel_title, top_n=10):
        """Content-based recommendation"""
        if novel_title not in self.title_index:
            print(f"Novel '{novel_title}' not found")
            return []

        idx = self.title_index[novel_title]
        novel = self.novels[idx]
        category = novel.get('category', '')

        candidates = list(self.category_index.get(category, []))
        if len(candidates) < top_n * 3:
            candidates = list(range(len(self.novels)))

        similarities = self.content_similarity(idx, candidates)
        return [(self.novels[i], sim) for i, sim in similarities[:top_n]]

    def collaborative_filter_recommend(self, user_favorite_titles, top_n=10):
        """Collaborative filtering based on user favorites"""
        favorite_indices = []
        for title in user_favorite_titles:
            if title in self.title_index:
                favorite_indices.append(self.title_index[title])

        if not favorite_indices:
            return []

        all_scores = defaultdict(float)
        weight_sum = 1.0 / len(favorite_indices) if favorite_indices else 1.0

        for fav_idx in favorite_indices:
            for i in range(len(self.novels)):
                if i in favorite_indices:
                    continue
                sim = self.attribute_similarity(fav_idx, i)
                all_scores[i] += sim * weight_sum

        ranked = sorted(all_scores.items(), key=lambda x: x[1], reverse=True)
        return [(self.novels[i], score) for i, score in ranked[:top_n]]

    def popularity_recommend(self, top_n=10, platform=None, category=None):
        """Popularity-based recommendation"""
        candidates = self.novels

        if platform:
            candidates = [self.novels[i] for i in self.platform_index.get(platform, [])]
        if category:
            candidates = [n for n in candidates if n.get('category') == category]

        scored = []
        for novel in candidates:
            score = 0.0
            score += math.log(novel.get('clicks', 0) + 1) * 3.0
            score += math.log(novel.get('collects', 0) + 1) * 2.0
            score += math.log(novel.get('recommends', 0) + 1) * 1.5
            ratio = novel.get('collects', 0) / max(novel.get('clicks', 1), 1)
            score += ratio * 5.0
            scored.append((novel, score))

        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_n]

    def cross_platform_recommend(self, novel_title, target_platform, top_n=10):
        """Cross-platform recommendation: find similar novels on a different platform"""
        if novel_title not in self.title_index:
            return []

        idx = self.title_index[novel_title]
        novel = self.novels[idx]
        source_platform = novel.get('platform', '')

        if source_platform == target_platform:
            return self.content_based_recommend(novel_title, top_n)

        target_indices = [i for i in self.platform_index.get(target_platform, [])
                          if i != idx]

        similarities = self.content_similarity(idx, target_indices)
        return [(self.novels[i], sim) for i, sim in similarities[:top_n]]

    def hybrid_recommend(self, user_profile, top_n=15):
        """Hybrid recommendation combining all strategies"""
        favorites = user_profile.get('favorites', [])
        preferred_cats = user_profile.get('preferred_categories', [])
        preferred_platforms = user_profile.get('preferred_platforms', [])
        history = set(user_profile.get('history', []))

        scores = defaultdict(float)

        # Strategy 1: Collaborative filtering from favorites (weight: 0.35)
        if favorites:
            cf_recs = self.collaborative_filter_recommend(favorites, top_n * 3)
            max_cf = max(s for _, s in cf_recs) if cf_recs else 1.0
            for novel, score in cf_recs:
                if novel['title'] not in history:
                    scores[novel['title']] += (score / max_cf) * 0.35

        # Strategy 2: Category preference (weight: 0.25)
        for cat in preferred_cats:
            cat_novels = [self.novels[i] for i in self.category_index.get(cat, [])]
            for novel in cat_novels[:30]:
                if novel['title'] not in history:
                    scores[novel['title']] += 0.25

        # Strategy 3: Platform preferences (weight: 0.20)
        for platform in preferred_platforms:
            plat_novels = [self.novels[i] for i in self.platform_index.get(platform, [])]
            max_clicks = max((n.get('clicks', 1) for n in plat_novels), default=1)
            for novel in plat_novels[:20]:
                if novel['title'] not in history:
                    pop_score = novel.get('clicks', 0) / max_clicks
                    scores[novel['title']] += pop_score * 0.20

        # Strategy 4: Global popularity (weight: 0.20)
        pop_recs = self.popularity_recommend(top_n * 2)
        max_pop = max(s for _, s in pop_recs) if pop_recs else 1.0
        for novel, score in pop_recs:
            if novel['title'] not in history:
                scores[novel['title']] += (score / max_pop) * 0.20

        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return [(self._get_novel_by_title(title), score) for title, score in ranked[:top_n]]

    def _get_novel_by_title(self, title):
        idx = self.title_index.get(title)
        return self.novels[idx] if idx is not None else None

    def diversity_boost(self, recommendations, diversity_factor=0.3):
        """Boost recommendation diversity by penalizing same-author/cluster items"""
        if len(recommendations) <= 3:
            return recommendations

        boosted = []
        seen_authors = set()
        seen_categories = Counter()

        for novel, score in recommendations:
            if novel is None:
                continue
            adjusted = score
            author = novel.get('author', '')
            cat = novel.get('category', '')

            if author in seen_authors:
                adjusted *= (1 - diversity_factor)
            cat_penalty = seen_categories.get(cat, 0) * diversity_factor * 0.5
            adjusted *= (1 - cat_penalty)

            seen_authors.add(author)
            seen_categories[cat] += 1
            boosted.append((novel, adjusted))

        boosted.sort(key=lambda x: x[1], reverse=True)
        return boosted

    def get_platform_insights(self):
        """Get cross-platform insights for analysis"""
        insights = {}
        platforms = set(n.get('platform', '') for n in self.novels)

        for platform in platforms:
            pnovels = [n for n in self.novels if n.get('platform') == platform]
            if not pnovels:
                continue

            insights[platform] = {
                'count': len(pnovels),
                'avg_clicks': sum(n.get('clicks', 0) for n in pnovels) / len(pnovels),
                'avg_collects': sum(n.get('collects', 0) for n in pnovels) / len(pnovels),
                'avg_words': sum(n.get('word_count', 0) for n in pnovels) / len(pnovels),
                'top_categories': Counter(
                    n.get('category', '') for n in pnovels
                ).most_common(5),
                'top_authors': Counter(
                    n.get('author', '') for n in pnovels
                ).most_common(5),
                'completion_rate': sum(
                    1 for n in pnovels if n.get('update_status') == '已完结'
                ) / len(pnovels),
            }

        return insights


def run_recommendation_demo():
    """Demonstration of the enhanced recommendation system"""
    print("=" * 60)
    print("ENHANCED RECOMMENDATION SYSTEM DEMO")
    print("=" * 60)

    # Load data
    data_path = 'd:/NOVEL ANALYSIS/novels_data.json'
    with open(data_path, 'r', encoding='utf-8') as f:
        novels = json.load(f)

    print(f"\nLoaded {len(novels)} novels")

    recommender = EnhancedRecommender(novels)
    recommender.fit_content_model()

    # Demo 1: Content-based recommendation
    sample = novels[0]
    print(f"\n{'─'*60}")
    print(f"1. Content-Based Recommendation for: {sample['title']}")
    print(f"   Author: {sample['author']} | Platform: {sample['platform']} | Category: {sample['category']}")
    print(f"{'─'*60}")
    recs = recommender.content_based_recommend(sample['title'], top_n=8)
    for i, (novel, score) in enumerate(recs, 1):
        print(f"  {i:2d}. {novel['title'][:20]:20s} | {novel['author'][:10]:10s} | {novel['platform']:8s} | Score: {score:.4f}")

    # Demo 2: Collaborative filtering
    print(f"\n{'─'*60}")
    print("2. Collaborative Filtering (based on 3 favorites)")
    print(f"{'─'*60}")
    favorites = [novels[0]['title'], novels[5]['title'], novels[10]['title']]
    recs = recommender.collaborative_filter_recommend(favorites, top_n=8)
    for i, (novel, score) in enumerate(recs, 1):
        print(f"  {i:2d}. {novel['title'][:20]:20s} | {novel['author'][:10]:10s} | {novel['platform']:8s} | Score: {score:.4f}")

    # Demo 3: Popularity by platform
    print(f"\n{'─'*60}")
    print("3. Top Popular Novels by Platform")
    print(f"{'─'*60}")
    platforms = set(n['platform'] for n in novels)
    for plat in sorted(platforms):
        recs = recommender.popularity_recommend(top_n=3, platform=plat)
        print(f"\n  [{plat}]")
        for i, (novel, score) in enumerate(recs, 1):
            print(f"    {i}. {novel['title'][:25]:25s} | Clicks: {novel['clicks']:,} | Score: {score:.2f}")

    # Demo 4: Diversity-boosted recommendations
    print(f"\n{'─'*60}")
    print("4. Diversity-Boosted Recommendations")
    print(f"{'─'*60}")
    raw_recs = recommender.popularity_recommend(top_n=15)
    diverse_recs = recommender.diversity_boost(raw_recs, diversity_factor=0.4)
    print(f"  Before diversity boost (top 8):")
    for i, (novel, score) in enumerate(raw_recs[:8], 1):
        print(f"    {i}. {novel['title'][:25]:25s} | {novel['author'][:10]:10s} | Category: {novel['category']} | Score: {score:.2f}")
    print(f"  After diversity boost (top 8):")
    for i, (novel, score) in enumerate(diverse_recs[:8], 1):
        print(f"    {i}. {novel['title'][:25]:25s} | {novel['author'][:10]:10s} | Category: {novel['category']} | Score: {score:.2f}")

    # Demo 5: Platform insights
    print(f"\n{'─'*60}")
    print("5. Cross-Platform Insights")
    print(f"{'─'*60}")
    insights = recommender.get_platform_insights()
    for plat, data in sorted(insights.items()):
        print(f"\n  [{plat}]")
        print(f"    Novels: {data['count']}")
        print(f"    Avg Clicks: {data['avg_clicks']:,.0f}")
        print(f"    Avg Collects: {data['avg_collects']:,.0f}")
        print(f"    Avg Words: {data['avg_words']:,.0f}")
        print(f"    Completion Rate: {data['completion_rate']:.1%}")
        print(f"    Top Categories: {', '.join(c for c,_ in data['top_categories'][:3])}")
        print(f"    Top Authors: {', '.join(a for a,_ in data['top_authors'][:3])}")

    print(f"\n{'='*60}")
    print("DEMO COMPLETE")
    print(f"{'='*60}")


if __name__ == '__main__':
    run_recommendation_demo()
