# reports/views/stats_views.py
from django.db.models import Count
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..models import Report, RequestHelp, Appointment
from django.db.models.functions import ExtractYear


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def admin_stats(request):
    if request.user.role != "admin":
        return Response({"detail": "ไม่มีสิทธิ์"}, status=403)

    year = request.GET.get("year")
    print("YEAR RECEIVED:", year)

    # -------------------------
    # REPORTS
    # -------------------------
    reports = Report.objects.all()
    if year:
        reports = reports.filter(created_at__year=year)

    report_qs = (
        reports.values("category")
        .annotate(total=Count("id"))
        .order_by("category")
    )

    reports_by_category = {
        (r["category"] or "ไม่ระบุ"): r["total"]
        for r in report_qs
    }

    # -------------------------
    # REQUEST HELP
    # -------------------------
    requests = RequestHelp.objects.all()
    if year:
        requests = requests.filter(created_at__year=year)

    request_qs = (
        requests.values("request_type")
        .annotate(total=Count("id"))
        .order_by("request_type")
    )

    requests_by_type = {
        (r["request_type"] or "ไม่ระบุ"): r["total"]
        for r in request_qs
    }

    # -------------------------
    # APPOINTMENTS
    # -------------------------
    appointments = Appointment.objects.filter(status="approved")
    if year:
        appointments = appointments.filter(created_at__year=year)

    appointment_qs = (
        appointments.values("meet_with")
        .annotate(total=Count("id"))
        .order_by("meet_with")
    )

    appointments_by_meet_with = {
        (str(a["meet_with"]) if a["meet_with"] else "ไม่ระบุ"): a["total"]
        for a in appointment_qs
    }

    return Response({
        "reports_by_category": reports_by_category,
        "requests_by_type": requests_by_type,
        "appointments_by_meet_with": appointments_by_meet_with,
    })

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def available_years(request):
    if request.user.role != "admin":
        return Response({"detail": "ไม่มีสิทธิ์"}, status=403)

    years = (
        Report.objects
        .annotate(year=ExtractYear("created_at"))
        .values_list("year", flat=True)
        .distinct()
    )

    return Response(sorted(years, reverse=True))