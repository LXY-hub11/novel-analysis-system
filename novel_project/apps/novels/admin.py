"""
Admin configuration for novels app.
"""
from django.contrib import admin
from .models import Novel, Category, UserCollection, UserRating, NovelAnalysis, RecommendationLog


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'description', 'created_at']
    search_fields = ['name']
    ordering = ['name']


@admin.register(Novel)
class NovelAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'author', 'category', 'platform', 'clicks', 'created_at']
    list_filter = ['category', 'platform', 'source']
    search_fields = ['title', 'author', 'description']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    fieldsets = (
        (None, {
            'fields': ('title', 'author', 'category', 'description', 'word_count', 'update_status')
        }),
        ('来源信息', {
            'fields': ('source', 'platform', 'last_chapter', 'crawl_time')
        }),
        ('数据统计', {
            'fields': ('clicks', 'collects', 'recommends'),
        }),
    )


@admin.register(UserCollection)
class UserCollectionAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'novel', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'novel__title']
    ordering = ['-created_at']


@admin.register(UserRating)
class UserRatingAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'novel', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['user__username', 'novel__title']
    ordering = ['-created_at']


@admin.register(NovelAnalysis)
class NovelAnalysisAdmin(admin.ModelAdmin):
    list_display = ['id', 'novel', 'sentiment_score', 'hot_score', 'quality_score', 'analysis_time']
    list_filter = ['analysis_time']
    search_fields = ['novel__title']
    ordering = ['-analysis_time']


@admin.register(RecommendationLog)
class RecommendationLogAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'novel', 'recommendation_type', 'score', 'created_at']
    list_filter = ['recommendation_type', 'created_at']
    search_fields = ['user__username', 'novel__title']
    ordering = ['-created_at']
