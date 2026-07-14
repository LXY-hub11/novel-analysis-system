"""
Admin configuration for users app.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile, UserActivity


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name = 'User Profile'
    verbose_name_plural = 'User Profiles'


class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ['username', 'email', 'is_staff', 'is_active', 'date_joined']

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super().get_inline_instances(request, obj)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'phone', 'gender', 'birthday', 'created_at']
    list_filter = ['gender', 'created_at']
    search_fields = ['user__username', 'phone', 'bio']
    ordering = ['-created_at']


@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'activity_type', 'activity_description', 'ip_address', 'created_at']
    list_filter = ['activity_type', 'created_at']
    search_fields = ['user__username', 'activity_description', 'ip_address']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
