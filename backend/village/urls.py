from django.urls import path
from .views import (
    # Public
    VillageFullAPIView,
    CommunityProfileListAPIView,
    FundTypeListAPIView,
    FundRecordListAPIView,
    FundLoanListAPIView,

    # Admin (overview)
    VillageAdminAPIView,

    # Admin (sections/places)
    VillageSectionAdminAPIView,
    VillageSectionDetailAdminAPIView,
    VillagePlaceAdminAPIView,
    VillagePlaceDetailAdminAPIView,

    # Admin (images)
    VillageSectionImageUploadAdminAPIView,
    VillageSectionImageDeleteAdminAPIView,
    VillagePlaceImageUploadAdminAPIView,
    VillagePlaceImageDeleteAdminAPIView,

    # Admin profiles
    CommunityProfileAdminAPIView,
    CommunityProfileDetailAdminAPIView,

    # Admin funds
    FundTypeAdminAPIView,
    FundTypeDetailAdminAPIView,
    FundRecordAdminAPIView,
    FundLoanExcelImportAPIView,
)

urlpatterns = [
    # Public
    path("village/full/", VillageFullAPIView.as_view()),
    path("village/profiles/", CommunityProfileListAPIView.as_view()),
    path("village/funds/", FundTypeListAPIView.as_view()),
    path("village/funds/<int:fund_id>/years/", FundRecordListAPIView.as_view()),
    path("village/funds/records/<int:record_id>/loans/", FundLoanListAPIView.as_view()),

    # Admin: overview
    path("admin/village/overview/", VillageAdminAPIView.as_view()),

    # Admin: sections CRUD
    path("admin/village/sections/", VillageSectionAdminAPIView.as_view()),
    path("admin/village/sections/<int:pk>/", VillageSectionDetailAdminAPIView.as_view()),

    # Admin: places CRUD (ผูกกับ section)
    path("admin/village/sections/<int:section_id>/places/", VillagePlaceAdminAPIView.as_view()),
    path("admin/village/places/<int:pk>/", VillagePlaceDetailAdminAPIView.as_view()),

    # Admin: upload/delete images (section)
    path("admin/village/sections/<int:section_id>/images/", VillageSectionImageUploadAdminAPIView.as_view()),
    path("admin/village/section-images/<int:pk>/", VillageSectionImageDeleteAdminAPIView.as_view()),

    # Admin: upload/delete images (place)
    path("admin/village/places/<int:place_id>/images/", VillagePlaceImageUploadAdminAPIView.as_view()),
    path("admin/village/place-images/<int:pk>/", VillagePlaceImageDeleteAdminAPIView.as_view()),

    # Admin: profiles
    path("admin/village/profiles/", CommunityProfileAdminAPIView.as_view()),
    path("admin/village/profiles/<int:pk>/", CommunityProfileDetailAdminAPIView.as_view()),

    # Admin: funds
    path("admin/funds/", FundTypeAdminAPIView.as_view()),
    path("admin/funds/<int:pk>/", FundTypeDetailAdminAPIView.as_view()),
    path("admin/funds/<int:fund_id>/records/", FundRecordAdminAPIView.as_view()),
    path("admin/funds/records/<int:record_id>/import-excel/", FundLoanExcelImportAPIView.as_view()),
]