from django.urls import path
from .views import (
    # User / Guest
    CommunityProfileDetailAdminAPIView,
    VillageFullAPIView,
    CommunityProfileListAPIView,
    FundTypeListAPIView,
    FundRecordListAPIView,
    FundLoanListAPIView,

    # Admin
    VillageAdminAPIView,
    VillageHistoryAdminAPIView,
    VillagePlaceAdminAPIView,
    VillagePlaceDetailAdminAPIView,
    VillageExtraSectionAdminAPIView,
    VillageExtraSectionDetailAdminAPIView,
    CommunityProfileAdminAPIView,
    FundTypeAdminAPIView,
    FundTypeDetailAdminAPIView,
    FundRecordAdminAPIView,
    FundLoanExcelImportAPIView,
)

urlpatterns = [
    # User / Guest
    path("village/full/", VillageFullAPIView.as_view()),
    path("village/profiles/", CommunityProfileListAPIView.as_view()),
    path("village/funds/", FundTypeListAPIView.as_view()),
    path("village/funds/<int:fund_id>/years/", FundRecordListAPIView.as_view()),
    path(
        "village/funds/records/<int:record_id>/loans/",
        FundLoanListAPIView.as_view()
    ),

    # Admin 
    path("admin/village/overview/", VillageAdminAPIView.as_view()),
    path("admin/village/history/", VillageHistoryAdminAPIView.as_view()),

    path("admin/village/places/", VillagePlaceAdminAPIView.as_view()),
    path("admin/village/places/<int:pk>/", VillagePlaceDetailAdminAPIView.as_view()),

    path("admin/village/extra-sections/", VillageExtraSectionAdminAPIView.as_view()),
    path(
        "admin/village/extra-sections/<int:pk>/",
        VillageExtraSectionDetailAdminAPIView.as_view()
    ),

    path("admin/village/profiles/", CommunityProfileAdminAPIView.as_view()),
    path(
        "admin/village/profiles/<int:pk>/",
        CommunityProfileDetailAdminAPIView.as_view()
    ),

    path("admin/funds/", FundTypeAdminAPIView.as_view()),
    path("admin/funds/<int:pk>/", FundTypeDetailAdminAPIView.as_view()),

    path(
        "admin/funds/<int:fund_id>/records/",
        FundRecordAdminAPIView.as_view()
    ),

    path(
        "admin/funds/records/<int:record_id>/import-excel/",
        FundLoanExcelImportAPIView.as_view()
    ),

]
