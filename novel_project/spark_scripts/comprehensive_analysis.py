"""
Comprehensive Spark data analysis for multi-platform novel data.
Performs: platform comparison, category analysis, word count stats,
popularity trends, author analytics, and generates analysis reports.
"""
import os
import sys
import json
from collections import Counter, defaultdict

_SPARK_AVAILABLE = False
try:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from spark_config import create_spark_session, load_novel_data, preprocess_novel_data
    _SPARK_AVAILABLE = True
except (ImportError, ModuleNotFoundError):
    pass


def analyze_platforms(spark, df):
    """Comprehensive platform-level analysis"""
    print("\n" + "=" * 60)
    print("PLATFORM ANALYSIS")
    print("=" * 60)

    from pyspark.sql.functions import col, count, sum, avg, max, min, stddev, round as sround

    platform_stats = df.groupBy("platform").agg(
        count("*").alias("novel_count"),
        sum("clicks").alias("total_clicks"),
        sum("collects").alias("total_collects"),
        sum("recommends").alias("total_recommends"),
        sum("word_count").alias("total_words"),
        sround(avg("clicks"), 2).alias("avg_clicks"),
        sround(avg("collects"), 2).alias("avg_collects"),
        sround(avg("word_count"), 2).alias("avg_words"),
        max("clicks").alias("max_clicks"),
        max("collects").alias("max_collects"),
    ).orderBy(col("novel_count").desc())

    platform_stats.show(20, False)
    return platform_stats


def analyze_categories(spark, df):
    """Category distribution and popularity analysis"""
    print("\n" + "=" * 60)
    print("CATEGORY ANALYSIS")
    print("=" * 60)

    from pyspark.sql.functions import col, count, sum, avg, round as sround

    cat_stats = df.groupBy("category").agg(
        count("*").alias("novel_count"),
        sround(avg("clicks"), 2).alias("avg_clicks"),
        sround(avg("collects"), 2).alias("avg_collects"),
        round(avg("recommends"), 2).alias("avg_recommends"),
        sum("word_count").alias("total_words"),
    ).orderBy(col("novel_count").desc())

    cat_stats.show(50, False)
    return cat_stats


def analyze_word_counts(spark, df):
    """Word count distribution analysis"""
    print("\n" + "=" * 60)
    print("WORD COUNT DISTRIBUTION")
    print("=" * 60)

    from pyspark.sql.functions import col, count, when

    wc_dist = df.withColumn("wc_level",
        when(col("word_count") < 200000, "短篇(<20万)")
        .when(col("word_count") < 500000, "中篇(20-50万)")
        .when(col("word_count") < 1000000, "长篇(50-100万)")
        .when(col("word_count") < 2000000, "超长篇(100-200万)")
        .when(col("word_count") < 5000000, "巨作(200-500万)")
        .otherwise("史诗(>500万)")
    ).groupBy("wc_level").agg(
        count("*").alias("count")
    ).orderBy("wc_level")

    wc_dist.show(20, False)

    # Platform-level word count distribution
    wc_platform = df.withColumn("wc_level",
        when(col("word_count") < 200000, "短篇(<20万)")
        .when(col("word_count") < 500000, "中篇(20-50万)")
        .when(col("word_count") < 1000000, "长篇(50-100万)")
        .when(col("word_count") < 2000000, "超长篇(100-200万)")
        .when(col("word_count") < 5000000, "巨作(200-500万)")
        .otherwise("史诗(>500万)")
    ).groupBy("platform", "wc_level").agg(
        count("*").alias("count")
    ).orderBy("platform", "wc_level")

    wc_platform.show(50, False)
    return wc_dist


def analyze_authors(spark, df):
    """Author productivity and popularity"""
    print("\n" + "=" * 60)
    print("AUTHOR ANALYSIS (Top 30)")
    print("=" * 60)

    from pyspark.sql.functions import col, count, sum, avg, round as sround

    author_stats = df.groupBy("author").agg(
        count("*").alias("novel_count"),
        sum("clicks").alias("total_clicks"),
        sround(avg("clicks"), 2).alias("avg_clicks"),
        sum("collects").alias("total_collects"),
        sum("word_count").alias("total_words"),
    ).orderBy(col("total_clicks").desc()).limit(30)

    author_stats.show(30, False)
    return author_stats


def analyze_status(spark, df):
    """Update status analysis"""
    print("\n" + "=" * 60)
    print("UPDATE STATUS ANALYSIS")
    print("=" * 60)

    from pyspark.sql.functions import col, count, sum, avg

    status_stats = df.groupBy("platform", "update_status").agg(
        count("*").alias("count"),
        avg("clicks").alias("avg_clicks"),
    ).orderBy("platform", "update_status")

    status_stats.show(50, False)
    return status_stats


def analyze_popularity_correlation(spark, df):
    """Analyze correlation between word count and popularity"""
    print("\n" + "=" * 60)
    print("POPULARITY CORRELATION ANALYSIS")
    print("=" * 60)

    from pyspark.sql.functions import col, corr

    corr_clicks_words = df.stat.corr("clicks", "word_count")
    corr_clicks_collects = df.stat.corr("clicks", "collects")
    corr_collects_recommends = df.stat.corr("collects", "recommends")

    print(f"Correlation (clicks vs word_count): {corr_clicks_words:.4f}")
    print(f"Correlation (clicks vs collects): {corr_clicks_collects:.4f}")
    print(f"Correlation (collects vs recommends): {corr_collects_recommends:.4f}")

    # Top novel by click-through rate (collects/clicks)
    from pyspark.sql.functions import expr

    df_with_ctr = df.withColumn("ctr", col("collects") / col("clicks"))
    df_with_ctr.filter(col("clicks") > 1000).select(
        "title", "author", "platform", "clicks", "collects", "ctr"
    ).orderBy(col("ctr").desc()).show(15, False)


def generate_analysis_report(spark, df):
    """Generate comprehensive analysis report as JSON"""
    from pyspark.sql.functions import col, count, sum, avg, max

    report = {}

    # Platform summary
    platform_rows = df.groupBy("platform").agg(
        count("*").alias("count"),
        sum("clicks").alias("total_clicks"),
        avg("clicks").alias("avg_clicks"),
        avg("word_count").alias("avg_words"),
    ).collect()

    report['platforms'] = [{
        'name': r['platform'],
        'count': r['count'],
        'total_clicks': r['total_clicks'],
        'avg_clicks': round(r['avg_clicks'], 2) if r['avg_clicks'] else 0,
        'avg_words': round(r['avg_words'], 2) if r['avg_words'] else 0,
    } for r in platform_rows]

    # Category summary
    cat_rows = df.groupBy("category").agg(
        count("*").alias("count"),
        avg("clicks").alias("avg_clicks"),
    ).orderBy(col("count").desc()).collect()

    report['categories'] = [{
        'name': r['category'],
        'count': r['count'],
        'avg_clicks': round(r['avg_clicks'], 2) if r['avg_clicks'] else 0,
    } for r in cat_rows]

    # Totals
    totals = df.agg(
        count("*").alias("total_novels"),
        sum("clicks").alias("total_clicks"),
        sum("collects").alias("total_collects"),
        sum("word_count").alias("total_words"),
    ).collect()[0]

    report['summary'] = {
        'total_novels': totals['total_novels'],
        'total_clicks': totals['total_clicks'],
        'total_collects': totals['total_collects'],
        'total_words': totals['total_words'],
        'total_platforms': df.select("platform").distinct().count(),
        'total_categories': df.select("category").distinct().count(),
        'total_authors': df.select("author").distinct().count(),
    }

    output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
    os.makedirs(output_dir, exist_ok=True)

    report_path = os.path.join(output_dir, 'analysis_report.json')
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"\nAnalysis report saved to: {report_path}")
    return report


def main():
    """Main analysis function"""
    print("=" * 60)
    print("SPARK COMPREHENSIVE NOVEL DATA ANALYSIS")
    print("=" * 60)

    data_path = 'd:/NOVEL ANALYSIS/novels_data.json'

    if _SPARK_AVAILABLE:
        try:
            spark = create_spark_session("NovelAnalysis")
            df = load_novel_data(spark, data_path)
            df = preprocess_novel_data(df)
            print(f"\nTotal records: {df.count()}")

            analyze_platforms(spark, df)
            analyze_categories(spark, df)
            analyze_word_counts(spark, df)
            analyze_authors(spark, df)
            analyze_status(spark, df)
            analyze_popularity_correlation(spark, df)
            generate_analysis_report(spark, df)
            spark.stop()
            return
        except Exception as e:
            print(f"\nSpark error: {e}, using Python fallback...")

    run_python_fallback_analysis(data_path)


def run_python_fallback_analysis(data_path):
    """Fallback analysis using pure Python (when Spark is unavailable)"""
    print("\n" + "=" * 60)
    print("PYTHON FALLBACK ANALYSIS")
    print("=" * 60)

    with open(data_path, 'r', encoding='utf-8') as f:
        novels = json.load(f)

    print(f"Total novels: {len(novels)}")

    # Platform stats
    platforms = defaultdict(lambda: {'count': 0, 'clicks': 0, 'collects': 0, 'words': 0})
    for n in novels:
        p = n.get('platform', '')
        platforms[p]['count'] += 1
        platforms[p]['clicks'] += n.get('clicks', 0)
        platforms[p]['collects'] += n.get('collects', 0)
        platforms[p]['words'] += n.get('word_count', 0)

    print("\n--- Platform Summary ---")
    for name, stats in sorted(platforms.items(), key=lambda x: x[1]['count'], reverse=True):
        avg_c = stats['clicks'] / stats['count'] if stats['count'] else 0
        print(f"  {name:12s}: {stats['count']:4d} novels | avg_clicks={avg_c:,.0f} | total_words={stats['words']:,}")

    # Category stats
    categories = Counter(n.get('category', '') for n in novels)
    print("\n--- Category Distribution ---")
    for cat, cnt in categories.most_common(20):
        print(f"  {cat:8s}: {cnt:4d}")

    # Status stats
    statuses = Counter(n.get('update_status', '') for n in novels)
    print("\n--- Status Distribution ---")
    for s, cnt in statuses.most_common():
        print(f"  {s}: {cnt} ({cnt/len(novels)*100:.1f}%)")

    # Author stats
    authors = Counter(n.get('author', '') for n in novels)
    print("\n--- Top Authors ---")
    for author, cnt in authors.most_common(15):
        total_clicks = sum(n['clicks'] for n in novels if n.get('author') == author)
        print(f"  {author:12s}: {cnt:3d} novels | total_clicks={total_clicks:,}")

    # Save report
    report = {
        'summary': {
            'total_novels': len(novels),
            'total_platforms': len(platforms),
            'total_categories': len(categories),
            'total_authors': len(authors),
        },
        'platforms': {k: dict(v) for k, v in platforms.items()},
        'categories': dict(categories),
        'statuses': dict(statuses),
    }

    output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
    os.makedirs(output_dir, exist_ok=True)
    report_path = os.path.join(output_dir, 'analysis_report.json')
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"\nAnalysis report saved to: {report_path}")


if __name__ == '__main__':
    main()
