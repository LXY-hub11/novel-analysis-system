"""
User models for the novel analysis system.
"""
from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    """用户扩展信息模型"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='用户')
    phone = models.CharField(max_length=20, blank=True, verbose_name='手机号')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name='头像')
    gender = models.CharField(max_length=10, choices=[
        ('male', '男'),
        ('female', '女'),
        ('unknown', '未知')
    ], default='unknown', verbose_name='性别')
    birthday = models.DateField(null=True, blank=True, verbose_name='生日')
    bio = models.TextField(blank=True, verbose_name='个人简介')
    favorite_categories = models.ManyToManyField('novels.Category', blank=True, verbose_name='喜欢的分类')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'user_profiles'
        verbose_name = '用户信息'
        verbose_name_plural = '用户信息'

    def __str__(self):
        return f"Profile of {self.user.username}"


class UserActivity(models.Model):
    """用户活动日志模型"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    activity_type = models.CharField(max_length=50, verbose_name='活动类型')
    activity_description = models.CharField(max_length=200, verbose_name='活动描述')
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name='IP地址')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='活动时间')

    class Meta:
        db_table = 'user_activities'
        verbose_name = '用户活动'
        verbose_name_plural = '用户活动'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.activity_type}"
