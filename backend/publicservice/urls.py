from django.urls import path
from .views import (
    PublicServiceListCreateView,
    PublicServiceDetailView,
    PublicServiceReportCreateView,
    MyPublicServiceReportsView,
    MyPublicServiceReportDetailView,
    CancelMyPublicServiceReportView,
    AdminPublicServiceReportsView,
    AdminUpdatePublicServiceReportStatusView,
)

urlpatterns = [
    path("", PublicServiceListCreateView.as_view()),
    path("<int:pk>/", PublicServiceDetailView.as_view()),

    # Service Reports (User)
    path("reports/create/", PublicServiceReportCreateView.as_view()),
    path("reports/my/", MyPublicServiceReportsView.as_view()),
    path("reports/my/<int:pk>/", MyPublicServiceReportDetailView.as_view()),
    path("reports/my/<int:pk>/cancel/", CancelMyPublicServiceReportView.as_view()),

    # Service Reports (Admin)
    path("reports/admin/", AdminPublicServiceReportsView.as_view()),
    path("reports/<int:pk>/status/", AdminUpdatePublicServiceReportStatusView.as_view()),
]
