from django.contrib import admin
from .models import Item, Location, BorrowRequest, BorrowItem


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ("name", "unit", "stock", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name",)


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name",)


class BorrowItemInline(admin.TabularInline):
    model = BorrowItem
    extra = 0


@admin.register(BorrowRequest)
class BorrowRequestAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "borrow_type",
        "borrower_name",
        "status",
        "created_at",
    )
    list_filter = ("borrow_type", "status")
    search_fields = ("borrower_name", "borrower_phone")
    inlines = [BorrowItemInline]
