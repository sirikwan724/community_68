from django.urls import path
from .views import report_views as rv
from .views import request_help_views as hv
from .views import stats_views as sv
from . import views
from .views.report_views import report_cancel

urlpatterns = [

    # -------------------------
    # Report (User)
    # -------------------------
    path("create/", views.create_report),
    path("my/", views.my_reports),
    path("<int:pk>/", views.report_detail),
    path("<int:pk>/cancel/", report_cancel),

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
    path("help/<int:pk>/reject/", views.request_help_reject),
    path("help/<int:pk>/done/", views.request_help_done),

    # -------------------------
    # Statistics
    # -------------------------
    path("admin/stats/", views.admin_stats),
    path("admin/available-years/", sv.available_years),


    # -------------------------
    # Appointments (User)
    # -------------------------
    path("appointments/create/", views.create_appointment),
    path("appointments/my/", views.my_appointments),
    path("appointments/my/<int:pk>/cancel/", views.cancel_appointment),

    # -------------------------
    # Appointments (Admin)
    # -------------------------
    path("appointments/admin/", views.admin_appointments),
    path("appointments/<int:pk>/approve/", views.approve_appointment),
    path("appointments/<int:pk>/reject/", views.reject_appointment),
    path("appointments/<int:pk>/note/", views.add_appointment_note),
]
