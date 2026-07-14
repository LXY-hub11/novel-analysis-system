"""
ASGI config for novel_analysis project.
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'novel_analysis.settings')

application = get_asgi_application()
