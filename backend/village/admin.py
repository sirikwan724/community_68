from django.contrib import admin
from .models import (
    Village,
    VillageHistory,
    VillagePlace,
    VillageExtraSection,
    CommunityProfile,
    FundType,
    FundRecord,
    FundLoan,
)

admin.site.register(Village)
admin.site.register(VillageHistory)
admin.site.register(VillagePlace)
admin.site.register(VillageExtraSection)
admin.site.register(FundType)
admin.site.register(FundRecord)
admin.site.register(FundLoan)

@admin.register(CommunityProfile)
class CommunityProfileAdmin(admin.ModelAdmin):
    list_display = (
        "full_name",
        "village",
        "group",
        "position",
        "level",
        "is_active",
    )

    list_filter = ("village", "group", "level", "is_active")

    search_fields = ("full_name", "position")

    ordering = ("village", "group", "level")
