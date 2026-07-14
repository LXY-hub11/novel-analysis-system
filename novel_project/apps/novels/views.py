"""
Views for novels app.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
from django.db.models import Q, Count, Avg, Sum, Min, Max, StdDev
from django.db.models.functions import TruncMonth
from django.views.decorators.http import require_http_methods
from .models import Novel, Category, UserCollection, UserRating, NovelAnalysis
import json
import os


def index(request):
    """Homepage view"""
    categories = Category.objects.all()
    recent_novels = Novel.objects.all()[:12]
    hot_novels = Novel.objects.filter(clicks__gt=0).order_by('-clicks')[:10]

    context = {
        'categories': categories,
        'recent_novels': recent_novels,
        'hot_novels': hot_novels,
    }
    return render(request, 'novels/index.html', context)


def novel_list(request):
    """Novel list view with filtering and pagination"""
    category_id = request.GET.get('category')
    platform = request.GET.get('platform', '')
    search_query = request.GET.get('search', '')
    page = request.GET.get('page', 1)

    novels = Novel.objects.all()

    if search_query:
        novels = novels.filter(
            Q(title__icontains=search_query) |
            Q(author__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    if category_id:
        novels = novels.filter(category_id=category_id)

    if platform:
        novels = novels.filter(platform=platform)

    novels = novels.order_by('-created_at')

    paginator = Paginator(novels, 12)
    novels_page = paginator.get_page(page)

    categories = Category.objects.all()
    platforms = Novel.objects.values_list('platform', flat=True).distinct().order_by('platform')

    context = {
        'novels': novels_page,
        'categories': categories,
        'platforms': platforms,
        'search_query': search_query,
        'current_category': int(category_id) if category_id else None,
        'current_platform': platform,
    }
    return render(request, 'novels/novel_list.html', context)


def novel_detail(request, novel_id):
    """Novel detail view"""
    novel = get_object_or_404(Novel, id=novel_id)
    novel.clicks += 1
    novel.save(update_fields=['clicks'])

    is_collected = False
    user_rating = None

    if request.user.is_authenticated:
        is_collected = UserCollection.objects.filter(
            user=request.user, novel=novel
        ).exists()
        rating_obj = UserRating.objects.filter(
            user=request.user, novel=novel
        ).first()
        user_rating = rating_obj.rating if rating_obj else 0

    similar_novels = Novel.objects.filter(
        category=novel.category
    ).exclude(id=novel.id)[:6]

    context = {
        'novel': novel,
        'is_collected': is_collected,
        'user_rating': user_rating,
        'similar_novels': similar_novels,
    }
    return render(request, 'novels/novel_detail.html', context)


@login_required
@require_http_methods(["POST"])
def toggle_collection(request, novel_id):
    """Toggle novel collection"""
    novel = get_object_or_404(Novel, id=novel_id)

    collection, created = UserCollection.objects.get_or_create(
        user=request.user,
        novel=novel
    )

    if not created:
        collection.delete()
        return JsonResponse({'status': 'removed', 'message': '取消收藏成功'})

    return JsonResponse({'status': 'added', 'message': '收藏成功'})


@login_required
@require_http_methods(["POST"])
def rate_novel(request, novel_id):
    """Rate a novel"""
    novel = get_object_or_404(Novel, id=novel_id)

    try:
        data = json.loads(request.body)
        rating = int(data.get('rating', 0))

        if rating < 1 or rating > 5:
            return JsonResponse({'status': 'error', 'message': '评分必须在1-5之间'})

        rating_obj, created = UserRating.objects.update_or_create(
            user=request.user,
            novel=novel,
            defaults={'rating': rating}
        )

        return JsonResponse({'status': 'success', 'message': '评分成功'})

    except (json.JSONDecodeError, ValueError) as e:
        return JsonResponse({'status': 'error', 'message': '无效的请求数据'})


def category_analysis(request):
    """Category analysis view"""
    categories = Category.objects.annotate(
        novel_count=Count('novel')
    ).order_by('-novel_count')

    category_data = []
    for cat in categories:
        avg_clicks = Novel.objects.filter(category=cat).aggregate(
            avg=Count('clicks')
        )['avg'] or 0
        category_data.append({
            'name': cat.name,
            'count': cat.novel_count,
            'avg_clicks': int(avg_clicks)
        })

    context = {
        'categories': categories,
        'category_data': category_data,
    }
    return render(request, 'novels/category_analysis.html', context)


def novel_analysis_view(request):
    """Novel data analysis view"""
    total_novels = Novel.objects.count()
    total_categories = Category.objects.count()

    novels_with_analysis = NovelAnalysis.objects.select_related('novel').all()[:20]

    category_stats = Category.objects.annotate(
        novel_count=Count('novel')
    ).values('name', 'novel_count').order_by('-novel_count')[:10]

    context = {
        'total_novels': total_novels,
        'total_categories': total_categories,
        'novels_with_analysis': novels_with_analysis,
        'category_stats': list(category_stats),
    }
    return render(request, 'novels/novel_analysis.html', context)


def recommendation_view(request):
    """Recommendation view"""
    if not request.user.is_authenticated:
        return redirect('login')

    user_collections = UserCollection.objects.filter(
        user=request.user
    ).select_related('novel')[:5]

    favorite_titles = [uc.novel.title for uc in user_collections]

    recommended_novels = []
    if favorite_titles:
        favorite_category = user_collections[0].novel.category if user_collections else None
        if favorite_category:
            recommended_novels = Novel.objects.filter(
                category=favorite_category
            ).exclude(
                id__in=[uc.novel.id for uc in user_collections]
            )[:10]

    context = {
        'user_collections': user_collections,
        'recommended_novels': recommended_novels,
    }
    return render(request, 'novels/recommendation.html', context)


def data_visualization(request):
    """Data visualization view"""
    categories = Category.objects.annotate(
        novel_count=Count('novel')
    ).values('name', 'novel_count').order_by('-novel_count')[:15]

    platforms = Novel.objects.values('platform').annotate(
        count=Count('id')
    ).order_by('-count')

    sources = Novel.objects.values('source').annotate(
        count=Count('id')
    ).order_by('-count')[:10]

    context = {
        'categories': list(categories),
        'platforms': list(platforms),
        'sources': list(sources),
    }
    return render(request, 'novels/data_visualization.html', context)


def user_collections(request):
    """User's collection view"""
    if not request.user.is_authenticated:
        return redirect('login')

    collections = UserCollection.objects.filter(
        user=request.user
    ).select_related('novel', 'novel__category').order_by('-created_at')

    context = {
        'collections': collections,
    }
    return render(request, 'novels/user_collections.html', context)


# ─── Enhanced Data Analysis APIs ────────────────────────────────────────────

def api_platform_comparison(request):
    """API: Cross-platform comparison data"""
    platforms = Novel.objects.values('platform').annotate(
        novel_count=Count('id'),
        total_clicks=Sum('clicks'),
        total_collects=Sum('collects'),
        total_recommends=Sum('recommends'),
        total_words=Sum('word_count'),
        avg_clicks=Avg('clicks'),
        avg_collects=Avg('collects'),
        avg_words=Avg('word_count'),
        max_clicks=Max('clicks'),
        max_words=Max('word_count'),
    ).order_by('-novel_count')

    return JsonResponse(list(platforms), safe=False)


def api_category_platform_analysis(request):
    """API: Category x Platform cross analysis"""
    data = Novel.objects.values('platform', 'category').annotate(
        count=Count('id'),
        total_clicks=Sum('clicks'),
        avg_clicks=Avg('clicks'),
    ).order_by('platform', '-count')

    return JsonResponse(list(data), safe=False)


def api_word_count_distribution(request):
    """API: Word count distribution analysis"""
    novels = Novel.objects.values('platform', 'word_count')
    platforms = {}

    for novel in novels:
        wc = novel['word_count']
        if wc < 200_000:
            level = '短篇(<20万)'
        elif wc < 500_000:
            level = '中篇(20-50万)'
        elif wc < 1_000_000:
            level = '长篇(50-100万)'
        elif wc < 2_000_000:
            level = '超长篇(100-200万)'
        elif wc < 5_000_000:
            level = '巨作(200-500万)'
        else:
            level = '史诗(>500万)'

        p = novel['platform']
        if p not in platforms:
            platforms[p] = {}
        platforms[p][level] = platforms[p].get(level, 0) + 1

    result = [{'platform': p, 'distribution': dist} for p, dist in platforms.items()]
    return JsonResponse(result, safe=False)


def api_popularity_analysis(request):
    """API: Popularity metrics analysis"""
    limit = int(request.GET.get('limit', 20))
    sort_by = request.GET.get('sort', '-clicks')

    novels = Novel.objects.values(
        'id', 'title', 'author', 'platform', 'category',
        'clicks', 'collects', 'recommends', 'word_count', 'update_status'
    ).order_by(sort_by)[:limit]

    return JsonResponse(list(novels), safe=False)


def api_author_analysis(request):
    """API: Author productivity and popularity analysis"""
    authors = Novel.objects.values('author', 'platform').annotate(
        novel_count=Count('id'),
        total_clicks=Sum('clicks'),
        total_collects=Sum('collects'),
        total_words=Sum('word_count'),
        avg_clicks=Avg('clicks'),
    ).order_by('-novel_count')[:30]

    return JsonResponse(list(authors), safe=False)


def api_status_analysis(request):
    """API: Update status across platforms"""
    data = Novel.objects.values('platform', 'update_status').annotate(
        count=Count('id'),
        avg_clicks=Avg('clicks'),
        avg_collects=Avg('collects'),
    ).order_by('platform', '-count')

    return JsonResponse(list(data), safe=False)


def api_category_stats(request):
    """API: Category statistics with platform breakdown"""
    cats = Novel.objects.values('category').annotate(
        novel_count=Count('id'),
        total_clicks=Sum('clicks'),
        total_collects=Sum('collects'),
        total_recommends=Sum('recommends'),
        total_words=Sum('word_count'),
        avg_clicks=Avg('clicks'),
        platform_count=Count('platform', distinct=True),
    ).order_by('-novel_count')

    return JsonResponse(list(cats), safe=False)


def api_overview_stats(request):
    """API: System overview statistics"""
    total_novels = Novel.objects.count()
    total_authors = Novel.objects.values('author').distinct().count()
    total_categories = Category.objects.count()
    total_words = Novel.objects.aggregate(s=Sum('word_count'))['s'] or 0
    total_clicks = Novel.objects.aggregate(s=Sum('clicks'))['s'] or 0
    total_collects = Novel.objects.aggregate(s=Sum('collects'))['s'] or 0
    platform_count = Novel.objects.values('platform').distinct().count()

    platform_breakdown = Novel.objects.values('platform').annotate(
        count=Count('id'),
        clicks=Sum('clicks'),
    ).order_by('-count')

    top_categories = Novel.objects.values('category').annotate(
        count=Count('id')
    ).order_by('-count')[:10]

    top_authors = Novel.objects.values('author').annotate(
        count=Count('id'),
        total_clicks=Sum('clicks'),
    ).order_by('-total_clicks')[:10]

    status_breakdown = Novel.objects.values('update_status').annotate(
        count=Count('id')
    )

    return JsonResponse({
        'totals': {
            'novels': total_novels,
            'authors': total_authors,
            'categories': total_categories,
            'words': total_words,
            'clicks': total_clicks,
            'collects': total_collects,
            'platforms': platform_count,
        },
        'platform_breakdown': list(platform_breakdown),
        'top_categories': list(top_categories),
        'top_authors': list(top_authors),
        'status_breakdown': list(status_breakdown),
    })


def api_novel_search(request):
    """API: Advanced novel search"""
    query = request.GET.get('q', '')
    platform = request.GET.get('platform', '')
    category = request.GET.get('category', '')
    status = request.GET.get('status', '')
    min_words = request.GET.get('min_words', '')
    max_words = request.GET.get('max_words', '')
    sort = request.GET.get('sort', '-clicks')
    limit = int(request.GET.get('limit', 50))

    novels = Novel.objects.all()

    if query:
        novels = novels.filter(
            Q(title__icontains=query) |
            Q(author__icontains=query) |
            Q(description__icontains=query)
        )
    if platform:
        novels = novels.filter(platform=platform)
    if category:
        novels = novels.filter(category=category)
    if status:
        novels = novels.filter(update_status=status)
    if min_words:
        novels = novels.filter(word_count__gte=int(min_words))
    if max_words:
        novels = novels.filter(word_count__lte=int(max_words))

    novels = novels.order_by(sort)[:limit]

    result = list(novels.values(
        'id', 'title', 'author', 'platform', 'category',
        'word_count', 'update_status', 'clicks', 'collects', 'recommends'
    ))
    return JsonResponse(result, safe=False)


def api_platform_list(request):
    """API: Get distinct platform and category lists for filtering"""
    platforms = list(Novel.objects.values('platform').distinct().order_by('platform'))
    categories = list(Novel.objects.values('category').distinct().order_by('category'))
    statuses = list(Novel.objects.values('update_status').exclude(
        update_status=''
    ).distinct().order_by('update_status'))
    return JsonResponse({
        'platforms': [p['platform'] for p in platforms],
        'categories': [c['category'] for c in categories],
        'statuses': [s['update_status'] for s in statuses],
    })


def api_scatter_data(request):
    """API: Data for scatter plot (word_count vs clicks, colored by platform)"""
    novels = Novel.objects.values(
        'title', 'platform', 'category',
        'word_count', 'clicks', 'collects', 'recommends'
    ).exclude(clicks=0).order_by('-clicks')[:200]

    return JsonResponse(list(novels), safe=False)


def api_rating_analysis(request):
    """API: User rating analysis"""
    ratings = UserRating.objects.values('novel__platform').annotate(
        avg_rating=Avg('rating'),
        rating_count=Count('id'),
    ).order_by('-avg_rating')

    rating_dist = UserRating.objects.values('rating').annotate(
        count=Count('id')
    ).order_by('rating')

    return JsonResponse({
        'platform_ratings': list(ratings),
        'rating_distribution': list(rating_dist),
    })


def enhanced_analysis(request):
    """Enhanced analysis dashboard page"""
    platforms = list(Novel.objects.values_list('platform', flat=True).distinct())
    categories = list(Novel.objects.values_list('category', flat=True).distinct())

    context = {
        'platforms': platforms,
        'categories': categories,
    }
    return render(request, 'novels/enhanced_analysis.html', context)
