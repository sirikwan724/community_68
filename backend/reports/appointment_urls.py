from django.urls import path
from . import appointment_views

urlpatterns = [

    # ============================
    # USER: นัดหมาย
    # ============================
    path("create/", appointment_views.create_appointment, name="create_appointment"),
    path("my/", appointment_views.my_appointments, name="my_appointments"),

    # ============================
    # ADMIN: นัดหมายทั้งหมด
    # ============================
    path("all/", appointment_views.admin_list_appointments, name="admin_list_appointments"),

    # ============================
    # ADMIN: การจัดการสถานะ
    # ============================
    path("<int:id>/accept/", appointment_views.accept_appointment, name="accept_appointment"),
    path("<int:id>/reject/", appointment_views.reject_appointment, name="reject_appointment"),
    path("<int:id>/done/", appointment_views.done_appointment, name="done_appointment"),
]
