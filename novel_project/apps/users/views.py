"""
Views for users app.
"""
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.models import User
from .models import UserProfile, UserActivity
import json


def user_login(request):
    """User login view"""
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')

        if not username or not password:
            return render(request, 'users/login.html', {
                'error': '用户名和密码不能为空'
            })

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            UserActivity.objects.create(
                user=user,
                activity_type='login',
                activity_description='用户登录',
                ip_address=get_client_ip(request)
            )
            next_url = request.GET.get('next', 'index')
            return redirect(next_url)
        else:
            return render(request, 'users/login.html', {
                'error': '用户名或密码错误'
            })

    return render(request, 'users/login.html')


def user_register(request):
    """User registration view"""
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        username = request.POST.get('username', '')
        email = request.POST.get('email', '')
        password = request.POST.get('password', '')
        password2 = request.POST.get('password2', '')

        if not username or not email or not password:
            return render(request, 'users/register.html', {
                'error': '所有字段都不能为空'
            })

        if password != password2:
            return render(request, 'users/register.html', {
                'error': '两次密码输入不一致'
            })

        if User.objects.filter(username=username).exists():
            return render(request, 'users/register.html', {
                'error': '用户名已存在'
            })

        if User.objects.filter(email=email).exists():
            return render(request, 'users/register.html', {
                'error': '邮箱已被使用'
            })

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        UserProfile.objects.create(user=user)

        UserActivity.objects.create(
            user=user,
            activity_type='register',
            activity_description='用户注册',
            ip_address=get_client_ip(request)
        )

        return redirect('login')

    return render(request, 'users/register.html')


@login_required
def user_logout(request):
    """User logout view"""
    UserActivity.objects.create(
        user=request.user,
        activity_type='logout',
        activity_description='用户登出',
        ip_address=get_client_ip(request)
    )
    logout(request)
    return redirect('login')


@login_required
def user_profile(request):
    """User profile view"""
    try:
        profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user)

    return render(request, 'users/profile.html', {
        'profile': profile
    })


@login_required
@require_http_methods(["POST"])
def update_profile(request):
    """Update user profile"""
    try:
        data = json.loads(request.body)

        user = request.user
        user.email = data.get('email', user.email)
        user.save()

        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.phone = data.get('phone', profile.phone)
        profile.gender = data.get('gender', profile.gender)
        profile.bio = data.get('bio', profile.bio)

        if 'birthday' in data and data['birthday']:
            profile.birthday = data['birthday']

        profile.save()

        UserActivity.objects.create(
            user=user,
            activity_type='update_profile',
            activity_description='更新个人资料',
            ip_address=get_client_ip(request)
        )

        return JsonResponse({'status': 'success', 'message': '资料更新成功'})

    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': '无效的JSON数据'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})


@login_required
def user_activity_history(request):
    """User activity history view"""
    activities = UserActivity.objects.filter(
        user=request.user
    ).order_by('-created_at')[:50]

    return render(request, 'users/activity_history.html', {
        'activities': activities
    })


def get_client_ip(request):
    """Get client IP address"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR', None)
    return ip
