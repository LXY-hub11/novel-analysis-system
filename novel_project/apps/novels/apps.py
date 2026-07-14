"""
Novels app configuration.
"""
from django.apps import AppConfig


class NovelsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.novels'
    verbose_name = '小说管理'
