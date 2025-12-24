from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, RegistrationRequest, Profile


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ("username", "role", "verified", "is_active")
    list_filter = ("role", "verified", "is_active")

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Permissions", {"fields": ("role", "verified", "is_active", "is_staff", "is_superuser")}),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "full_name", "phone_number")
    search_fields = ("user__username", "full_name")


@admin.register(RegistrationRequest)
class RegistrationRequestAdmin(admin.ModelAdmin):
    list_display = ("full_name", "citizen_id", "phone", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("full_name", "citizen_id", "phone")
