from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, RegistrationRequest


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ("username", "full_name", "role", "verified", "is_active")
    list_filter = ("role", "verified", "is_active")

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Personal info", {"fields": ("full_name", "address", "phone", "citizen_id")}),
        ("Permissions", {"fields": ("role", "verified", "is_active", "is_staff", "is_superuser")}),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )


@admin.register(RegistrationRequest)
class RegistrationRequestAdmin(admin.ModelAdmin):
    list_display = ("full_name", "citizen_id", "phone", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("full_name", "citizen_id", "phone")
