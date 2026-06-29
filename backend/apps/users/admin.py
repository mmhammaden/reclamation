from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('matricule', 'email', 'role', 'first_name', 'last_name', 'is_active')
    list_filter = ('role', 'is_active')
    search_fields = ('matricule', 'email', 'first_name', 'last_name')
    ordering = ('matricule',)

    fieldsets = (
        (None, {'fields': ('matricule', 'password')}),
        ('Informations personnelles', {'fields': ('first_name', 'last_name', 'email', 'telephone')}),
        ('Rôle & Permissions', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('matricule', 'email', 'role', 'password1', 'password2'),
        }),
    )