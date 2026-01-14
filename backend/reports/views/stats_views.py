# reports/views/stats_views.py
from django.db.models import Count
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..models import Report, RequestHelp, Appointment


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def admin_stats(request):
    if request.user.role != "admin":
        return Response({"detail": "ไม่มีสิทธิ์"}, status=403)

    report_qs = (
        Report.objects.values("category")
        .annotate(total=Count("id"))
        .order_by("category")
    )
    reports_by_category = {
        (r["category"] or "ไม่ระบุ"): r["total"]
        for r in report_qs
    }

    request_qs = (
        RequestHelp.objects.values("request_type")
        .annotate(total=Count("id"))
        .order_by("request_type")
    )
    requests_by_type = {
        (r["request_type"] or "ไม่ระบุ"): r["total"]
        for r in request_qs
    }

    appointment_qs = (
        Appointment.objects.filter(status="approved")
        .values("meet_with")
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

        # (optional) เผื่ออนาคตอยากใช้แบบ list
        "raw": {
            "reports": list(report_qs),
            "requests": list(request_qs),
            "appointments": list(appointment_qs),
        }
    })
