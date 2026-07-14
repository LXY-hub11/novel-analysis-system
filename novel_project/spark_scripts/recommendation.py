"""
Item-based Collaborative Filtering Recommendation System.
"""
from spark_config import create_spark_session
from pyspark.sql import SparkSession
from pyspark.ml.feature import IDF, Tokenizer, HashingTF
from pyspark.ml.linalg import Vectors
from pyspark.sql.functions import col, udf, collect_list, concat_ws, lower, trim, broadcast
from pyspark.sql.types import ArrayType, FloatType, DoubleType, IntegerType
import math
import os


def calculate_cosine_similarity(vec1, vec2):
    """Calculate cosine similarity between two vectors"""
    if vec1 is None or vec2 is None:
        return 0.0

    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    norm1 = math.sqrt(sum(a * a for a in vec1))
    norm2 = math.sqrt(sum(b * b for b in vec2))

    if norm1 == 0 or norm2 == 0:
        return 0.0

    return dot_product / (norm1 * norm2)


def content_based_recommendation(spark, novel_df, target_title, top_n=10):
    """Content-based recommendation using description similarity"""
    print(f"\n=== Content-Based Recommendation for: {target_title} ===")

    target_novel = novel_df.filter(col("title") == target_title).first()
    if not target_novel:
        print(f"Novel '{target_title}' not found!")
        return None

    target_category = target_novel["category"]
    target_author = target_novel["author"]

    similar_novels = novel_df.filter(
        (col("title") != target_title) &
        ((col("category") == target_category) | (col("author") == target_author))
    )

    def calculate_similarity_score(novel):
        score = 0.0
        if novel["category"] == target_category:
            score += 3.0
        if novel["author"] == target_author:
            score += 2.0
        desc1 = target_novel["description"][:100] if target_novel["description"] else ""
        desc2 = novel["description"][:100] if novel["description"] else ""
        common_words = set(desc1) & set(desc2)
        score += len(common_words) * 0.1
        return score

    similar_novels_list = similar_novels.take(top_n * 2)
    scored_novels = [(novel, calculate_similarity_score(novel)) for novel in similar_novels_list]
    scored_novels.sort(key=lambda x: x[1], reverse=True)

    print(f"\nTop {top_n} similar novels:")
    for i, (novel, score) in enumerate(scored_novels[:top_n], 1):
        print(f"{i}. {novel['title']} (Score: {score:.2f}) | Author: {novel['author']} | Category: {novel['category']}")

    return scored_novels[:top_n]


def category_popularity_recommendation(spark, novel_df, target_category, top_n=10):
    """Recommendation based on category popularity"""
    print(f"\n=== Category Popularity Recommendation: {target_category} ===")

    category_novels = novel_df.filter(col("category") == target_category)

    popular_novels = category_novels.orderBy(
        col("clicks").desc(nullsLast=True),
        col("recommends").desc(nullsLast=True)
    ).take(top_n)

    print(f"\nTop {top_n} popular novels in '{target_category}':")
    for i, novel in enumerate(popular_novels, 1):
        print(f"{i}. {novel['title']} | Author: {novel['author']} | Clicks: {novel['clicks']}")

    return popular_novels


def item_similarity_recommendation(spark, novel_df, user_favorites, top_n=10):
    """Item-based collaborative filtering recommendation"""
    print(f"\n=== Item-based Collaborative Filtering Recommendation ===")
    print(f"User favorites: {user_favorites}")

    favorite_novels = novel_df.filter(col("title").isin(user_favorites)).collect()

    if not favorite_novels:
        print("No matching favorites found!")
        return None

    all_novels = novel_df.collect()

    similarities = []
    for fav_novel in favorite_novels:
        for novel in all_novels:
            if novel["title"] != fav_novel["title"]:
                similarity = calculate_item_similarity(fav_novel, novel)
                similarities.append((novel, similarity))

    similarities.sort(key=lambda x: x[1], reverse=True)

    print(f"\nTop {top_n} recommended novels based on your favorites:")
    for i, (novel, sim) in enumerate(similarities[:top_n], 1):
        print(f"{i}. {novel['title']} (Similarity: {sim:.4f}) | {novel['author']} | {novel['category']}")

    return similarities[:top_n]


def calculate_item_similarity(novel1, novel2):
    """Calculate similarity between two novels based on attributes"""
    similarity = 0.0

    if novel1["category"] == novel2["category"]:
        similarity += 3.0

    if novel1["author"] == novel2["author"]:
        similarity += 2.0

    desc1_words = set(novel1["description"].split()) if novel1["description"] else set()
    desc2_words = set(novel2["description"].split()) if novel2["description"] else set()

    if desc1_words and desc2_words:
        jaccard = len(desc1_words & desc2_words) / len(desc1_words | desc2_words)
        similarity += jaccard * 2.0

    return similarity


def hybrid_recommendation(spark, novel_df, user_id, user_favorites, target_category, top_n=10):
    """Hybrid recommendation combining multiple strategies"""
    print(f"\n{'='*60}")
    print(f"HYBRID RECOMMENDATION FOR USER: {user_id}")
    print(f"{'='*60}")

    content_recs = []
    if user_favorites:
        content_recs = item_similarity_recommendation(
            spark, novel_df, user_favorites, top_n * 2
        )

    category_recs = category_popularity_recommendation(
        spark, novel_df, target_category, top_n * 2
    )

    if not content_recs and not category_recs:
        print("\nNo recommendations available!")
        return []

    combined_scores = {}

    if content_recs:
        max_sim = max(sim for _, sim in content_recs) if content_recs else 1.0
        for novel, sim in content_recs:
            title = novel["title"]
            normalized_score = (sim / max_sim) * 0.6
            combined_scores[title] = combined_scores.get(title, 0) + normalized_score

    if category_recs:
        for i, novel in enumerate(category_recs):
            title = novel["title"]
            popularity_score = 1.0 - (i / len(category_recs)) if category_recs else 0
            combined_scores[title] = combined_scores.get(title, 0) + (popularity_score * 0.4)

    ranked_recommendations = sorted(
        combined_scores.items(),
        key=lambda x: x[1],
        reverse=True
    )[:top_n]

    print(f"\n{'='*60}")
    print(f"FINAL HYBRID RECOMMENDATIONS (Top {top_n})")
    print(f"{'='*60}")

    result = []
    for i, (title, score) in enumerate(ranked_recommendations, 1):
        novel = novel_df.filter(col("title") == title).first()
        if novel:
            print(f"{i}. {novel['title']} | {novel['author']} | {novel['category']} | Score: {score:.4f}")
            result.append((novel, score))

    return result


def train_recommendation_model(spark, novel_df):
    """Train and return a recommendation model"""
    print("\n=== Training Recommendation Model ===")

    novels_list = novel_df.collect()

    similarity_matrix = []
    for i, novel1 in enumerate(novels_list):
        row = []
        for j, novel2 in enumerate(novels_list):
            if i == j:
                row.append(1.0)
            else:
                sim = calculate_item_similarity(novel1, novel2)
                row.append(sim)
        similarity_matrix.append(row)

    print(f"Similarity matrix computed for {len(novels_list)} novels")

    return similarity_matrix, novels_list


def get_personalized_recommendations(spark, novel_df, user_history, user_profile, top_n=10):
    """Get personalized recommendations based on user profile and history"""
    print(f"\n=== Personalized Recommendations for User ===")

    favorite_categories = user_profile.get("favorite_categories", [])
    favorite_authors = user_profile.get("favorite_authors", [])

    recommendations = []

    for novel in novel_df.collect():
        score = 0.0

        if novel["category"] in favorite_categories:
            score += 5.0

        if novel["author"] in favorite_authors:
            score += 3.0

        if novel["title"] not in user_history:
            score += 1.0

        recommendations.append((novel, score))

    recommendations.sort(key=lambda x: x[1], reverse=True)

    print(f"\nTop {top_n} personalized recommendations:")
    for i, (novel, score) in enumerate(recommendations[:top_n], 1):
        print(f"{i}. {novel['title']} | {novel['author']} | {novel['category']} | Score: {score:.1f}")

    return recommendations[:top_n]


if __name__ == "__main__":
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    json_path = os.path.join(project_root, "..", "novels_data.json")

    print(f"Loading data from: {json_path}")

    try:
        spark = create_spark_session("NovelRecommendation")

        novel_df = spark.read.json(json_path)
        novel_df.createOrReplaceTempView("novels")

        print(f"\nTotal novels loaded: {novel_df.count()}")

        sample_title = novel_df.select("title").first()["title"]
        content_based_recommendation(spark, novel_df, sample_title, 5)

        sample_category = novel_df.select("category").filter(
            col("category").isNotNull()
        ).first()["category"]
        if sample_category:
            category_popularity_recommendation(spark, novel_df, sample_category, 5)

        print("\nRecommendation system initialized successfully!")

    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()

    finally:
        if 'spark' in locals():
            spark.stop()
