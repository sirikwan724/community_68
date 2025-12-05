from django.urls import path
from .views import admin_request_help, create_report, admin_list_reports, create_request_help, my_request_help, admin_request_help, update_my_request
from . import views

urlpatterns = [

    # -------------------------
    # Report (User)
    # -------------------------
    path("create/", views.create_report),
    path("my/", views.my_reports),
    path("<int:pk>/", views.report_detail),
    path("<int:pk>/cancel/", views.report_cancel),

    # -------------------------
    # Report (Admin)
    # -------------------------
    path("admin-all/", views.admin_list_reports),
    path("<int:pk>/accept/", views.report_accept),
    path("<int:pk>/add-note/", views.report_add_note),
    path("<int:pk>/done/", views.report_done),
    path("<int:pk>/rollback/", views.report_rollback),

    path("admin/pending/", views.admin_reports_pending),
    path("admin/processing/", views.admin_reports_processing),
    path("admin/resolved/", views.admin_reports_resolved),

    # -------------------------
    # Request Help (User)
    # -------------------------
    path("help/create/", views.create_request_help),
    path("help/my/", views.my_request_help),
    path("help/my/<int:pk>/", views.get_my_request_help),
    path("help/my/<int:pk>/update/", views.update_my_request),
    path("help/my/<int:pk>/cancel/", views.cancel_my_request),  

    # -------------------------
    # Request Help (Admin)
    # -------------------------
    path("help/admin/", views.admin_request_help),
    path("help/<int:pk>/approve/", views.request_help_approve),

    # -------------------------
    # Statistics
    # -------------------------
    path("admin/stats/", views.admin_stats),  
]