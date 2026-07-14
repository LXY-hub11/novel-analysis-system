"""
URL configuration for novels app.
"""
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('novels/', views.novel_list, name='novel_list'),
    path('novel/<int:novel_id>/', views.novel_detail, name='novel_detail'),
    path('novel/<int:novel_id>/collect/', views.toggle_collection, name='toggle_collection'),
    path('novel/<int:novel_id>/rate/', views.rate_novel, name='rate_novel'),
    path('category-analysis/', views.category_analysis, name='category_analysis'),
    path('novel-analysis/', views.novel_analysis_view, name='novel_analysis'),
    path('recommendations/', views.recommendation_view, name='recommendations'),
    path('visualization/', views.data_visualization, name='data_visualization'),
    path('collections/', views.user_collections, name='user_collections'),
    # Enhanced analysis APIs
    path('api/platform-comparison/', views.api_platform_comparison, name='api_platform_comparison'),
    path('api/category-platform/', views.api_category_platform_analysis, name='api_category_platform'),
    path('api/word-count-dist/', views.api_word_count_distribution, name='api_word_count_dist'),
    path('api/popularity/', views.api_popularity_analysis, name='api_popularity'),
    path('api/author-analysis/', views.api_author_analysis, name='api_author_analysis'),
    path('api/status-analysis/', views.api_status_analysis, name='api_status_analysis'),
    path('api/category-stats/', views.api_category_stats, name='api_category_stats'),
    path('api/overview/', views.api_overview_stats, name='api_overview'),
    path('api/search/', views.api_novel_search, name='api_novel_search'),
    path('api/platforms-list/', views.api_platform_list, name='api_platforms_list'),
    path('api/scatter/', views.api_scatter_data, name='api_scatter'),
    path('api/rating-analysis/', views.api_rating_analysis, name='api_rating_analysis'),
    path('enhanced-analysis/', views.enhanced_analysis, name='enhanced_analysis'),
]
