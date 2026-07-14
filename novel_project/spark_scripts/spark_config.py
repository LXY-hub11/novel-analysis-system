"""
Spark configuration and connection module.
"""
import os
import sys

os.environ['JAVA_HOME'] = r'C:\Program Files\Eclipse Adoptium\jdk-11.0.24+8'
os.environ['HADOOP_HOME'] = r'D:\hadoop'
os.environ['SPARK_HOME'] = r'D:\spark'
os.environ['PYSPARK_PYTHON'] = sys.executable
os.environ['PYSPARK_DRIVER_PYTHON'] = sys.executable

from pyspark.sql import SparkSession
from pyspark import SparkConf, SparkContext


def create_spark_session(app_name="NovelAnalysis"):
    """Create and return a Spark session"""
    spark_builder = SparkSession.builder.appName(app_name)

    spark_builder = spark_builder.config("spark.driver.memory", "4g") \
        .config("spark.sql.shuffle.partitions", "200") \
        .config("spark.driver.maxResultSize", "2g") \
        .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer") \
        .config("spark.sql.crossJoin.enabled", "true")

    try:
        spark_builder = spark_builder.config("spark.hadoop.home", os.environ['HADOOP_HOME'])
    except:
        pass

    spark = spark_builder.getOrCreate()
    spark.sparkContext.setLogLevel("WARN")

    return spark


def load_novel_data(spark, json_path):
    """Load novel data from JSON file using Spark"""
    df = spark.read.json(json_path)
    return df


def preprocess_novel_data(df):
    """Preprocess novel data: cleaning and transformation"""
    from pyspark.sql.functions import col, when, trim, lower, length

    df_cleaned = df.filter(length(col("title")) > 0)

    df_cleaned = df_cleaned.withColumn("title", trim(col("title")))
    df_cleaned = df_cleaned.withColumn("author", trim(col("author")))
    df_cleaned = df_cleaned.withColumn("category",
                                       when(col("category").isNull(), "未分类")
                                       .otherwise(trim(col("category"))))

    df_cleaned = df_cleaned.withColumn("description",
                                       when(col("description").isNull(), "")
                                       .otherwise(col("description")))

    df_cleaned = df_cleaned.withColumn("source",
                                       when(col("source").isNull(), "未知")
                                       .otherwise(col("source")))

    return df_cleaned
