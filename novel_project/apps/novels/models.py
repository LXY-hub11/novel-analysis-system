"""
Novel models for the novel analysis system.
"""
from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    """小说分类模型"""
    name = models.CharField(max_length=50, unique=True, verbose_name='分类名称')
    description = models.TextField(blank=True, verbose_name='分类描述')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'categories'
        verbose_name = '小说分类'
        verbose_name_plural = '小说分类'
        ordering = ['name']

    def __str__(self):
        return self.name


class Novel(models.Model):
    """小说模型"""
    title = models.CharField(max_length=200, verbose_name='小说标题')
    author = models.CharField(max_length=100, verbose_name='作者')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='分类')
    description = models.TextField(verbose_name='简介')
    word_count = models.IntegerField(default=0, verbose_name='字数')
    update_status = models.CharField(max_length=20, blank=True, verbose_name='更新状态')
    source = models.CharField(max_length=100, verbose_name='来源')
    platform = models.CharField(max_length=50, verbose_name='平台')
    clicks = models.IntegerField(default=0, verbose_name='点击数')
    collects = models.IntegerField(default=0, verbose_name='收藏数')
    recommends = models.IntegerField(default=0, verbose_name='推荐数')
    last_chapter = models.CharField(max_length=200, blank=True, verbose_name='最新章节')
    crawl_time = models.DateTimeField(verbose_name='爬取时间')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'novels'
        verbose_name = '小说'
        verbose_name_plural = '小说'
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class UserCollection(models.Model):
    """用户收藏模型"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    novel = models.ForeignKey(Novel, on_delete=models.CASCADE, verbose_name='小说')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='收藏时间')

    class Meta:
        db_table = 'user_collections'
        verbose_name = '用户收藏'
        verbose_name_plural = '用户收藏'
        unique_together = ['user', 'novel']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.novel.title}"


class UserRating(models.Model):
    """用户评分模型"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    novel = models.ForeignKey(Novel, on_delete=models.CASCADE, verbose_name='小说')
    rating = models.IntegerField(default=0, verbose_name='评分')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='评分时间')

    class Meta:
        db_table = 'user_ratings'
        verbose_name = '用户评分'
        verbose_name_plural = '用户评分'
        unique_together = ['user', 'novel']

    def __str__(self):
        return f"{self.user.username} - {self.novel.title} - {self.rating}"


class NovelAnalysis(models.Model):
    """小说分析结果模型"""
    novel = models.OneToOneField(Novel, on_delete=models.CASCADE, verbose_name='小说')
    sentiment_score = models.FloatField(default=0.0, verbose_name='情感得分')
    hot_score = models.FloatField(default=0.0, verbose_name='热度评分')
    quality_score = models.FloatField(default=0.0, verbose_name='质量评分')
    category_popularity = models.IntegerField(default=0, verbose_name='分类热度排名')
    word_count_level = models.CharField(max_length=20, verbose_name='字数级别')
    analysis_time = models.DateTimeField(auto_now_add=True, verbose_name='分析时间')

    class Meta:
        db_table = 'novel_analysis'
        verbose_name = '小说分析'
        verbose_name_plural = '小说分析'

    def __str__(self):
        return f"{self.novel.title} - Analysis"


class RecommendationLog(models.Model):
    """推荐日志模型"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    novel = models.ForeignKey(Novel, on_delete=models.CASCADE, verbose_name='推荐小说')
    recommendation_type = models.CharField(max_length=50, verbose_name='推荐类型')
    score = models.FloatField(default=0.0, verbose_name='推荐得分')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='推荐时间')

    class Meta:
        db_table = 'recommendation_logs'
        verbose_name = '推荐日志'
        verbose_name_plural = '推荐日志'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.novel.title} - {self.recommendation_type}"
