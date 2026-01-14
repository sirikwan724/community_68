from django.urls import path
from .views import *

urlpatterns = [
    # master data
    path("items/", ItemListView.as_view()),
    path("locations/", LocationListView.as_view()),

    # user
    path('requests/', CreateBorrowRequestView.as_view()),
    path('my/', MyBorrowRequestListView.as_view()),
    path('<int:pk>/request-return/', RequestReturnView.as_view()),

    # admin
    path('admin/requests/', AdminBorrowRequestListView.as_view()),
    path('admin/<int:pk>/approve/', AdminApproveBorrowView.as_view()),
    path('admin/<int:pk>/reject/', AdminRejectBorrowView.as_view()),
    path('admin/<int:pk>/confirm-return/', AdminConfirmReturnView.as_view()),
    path("admin/stats/borrow-items/", AdminBorrowItemStatsView.as_view()),
    path("admin/stats/borrow-locations/", AdminBorrowLocationStatsView.as_view()),
    path("admin/stats/summary/", AdminBorrowSummaryStatsView.as_view()),
]
