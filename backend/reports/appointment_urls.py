from django.urls import path
from .views import appointment_views as av
from .views.appointment_views import (
    create_appointment,
    my_appointments,
    cancel_appointment,
    admin_appointments,
    approve_appointment,
    reject_appointment,
    add_appointment_note,
    appointment_detail,
    done_appointment,
)

urlpatterns = [
    # USER
    path("create/", create_appointment),
    path("my/", my_appointments),
    path("my/<int:pk>/cancel/", cancel_appointment),
    path("my/<int:pk>/", appointment_detail),

    # ADMIN
    path("all/", admin_appointments),

    path("<int:pk>/approve/", approve_appointment),
    path("<int:pk>/reject/", reject_appointment),
    path("<int:pk>/note/", add_appointment_note),
    path("<int:pk>/done/", done_appointment),
]