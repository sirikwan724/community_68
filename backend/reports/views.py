from django.db.models import Count
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import Report, ReportNote, RequestHelp
from .serializers import ReportSerializer, ReportNoteSerializer, RequestHelpSerializer


# =====================================================
# 1) USER ส่งรายงาน (CREATE)
# =====================================================
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_report(request):

    data = request.data.copy()

    # เติมข้อมูลผู้ใช้ให้อัตโนมัติ
    data["user"] = request.user.id
    data["fullname"] = request.user.full_name
    data["phone"] = request.user.phone

    serializer = ReportSerializer(data=data)

    if serializer.is_valid():
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    print("CREATE REPORT ERROR:", serializer.errors)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# =====================================================
# 2) USER: ดู / แก้ไข รายงาน
# =====================================================
@api_view(["GET", "PUT"])
@permission_classes([IsAuthenticated])
def report_detail(request, pk):
    try:
        report = Report.objects.get(pk=pk)
    except Report.DoesNotExist:
        return Response({"detail": "ไม่พบรายงานนี้"}, status=404)

    if report.user != request.user:
        return Response({"detail": "คุณไม่มีสิทธิ์เข้าถึงรายงานนี้"}, status=403)

    # GET
    if request.method == "GET":
        return Response(ReportSerializer(report).data)

    # PUT
    if report.status != "pending":
        return Response({"detail": "รายงานนี้ถูกรับเรื่องแล้ว แก้ไขไม่ได้"}, status=400)

    data = request.data.copy()
    data["user"] = request.user.id

    serializer = ReportSerializer(report, data=data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)

    return Response(serializer.errors, status=400)


# =====================================================
# 3) ADMIN: ดูรายงานทั้งหมด
# =====================================================
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def admin_list_reports(request):
    if request.user.role != "admin":
        return Response({"detail": "คุณไม่มีสิทธิ์"}, status=403)

    reports = Report.objects.all().order_by("-created_at")
    return Response(ReportSerializer(reports, many=True).data)


# =====================================================
# 4) USER ดูรายงานตัวเอง
# =====================================================
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def my_reports(request):
    reports = Report.objects.filter(user=request.user).order_by("-created_at")
    return Response(ReportSerializer(reports, many=True).data)


# =====================================================
# 5) USER ยกเลิกรายงาน
# =====================================================
@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def report_cancel(request, pk):
    try:
        report = Report.objects.get(pk=pk, user=request.user)
    except Report.DoesNotExist:
        return Response({"detail": "ไม่พบรายงานนี้"}, status=404)

    if report.status != "pending":
        return Response({"detail": "ไม่สามารถยกเลิกได้"}, status=400)

    report.delete()
    return Response({"message": "ยกเลิกคำร้องสำเร็จ"}, status=200)


# =====================================================
# 6) ADMIN รับเรื่อง → processing
# =====================================================
@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def report_accept(request, pk):

    if request.user.role != "admin":
        return Response({"detail": "คุณไม่มีสิทธิ์"}, status=403)

    try:
        report = Report.objects.get(pk=pk)
    except Report.DoesNotExist:
        return Response({"detail": "ไม่พบรายงานนี้"}, status=404)

    report.status = "processing"
    report.save()

    return Response({"message": "รับเรื่องแล้ว"}, status=200)


# =====================================================
# 7) ADMIN เพิ่มโน้ตในรายงาน
# =====================================================
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def report_add_note(request, pk):

    if request.user.role != "admin":
        return Response({"detail": "คุณไม่มีสิทธิ์"}, status=403)

    try:
        report = Report.objects.get(pk=pk)
    except Report.DoesNotExist:
        return Response({"detail": "ไม่พบรายงานนี้"}, status=404)

    message = request.data.get("message", "").strip()
    if not message:
        return Response({"detail": "โน้ตต้องไม่ว่าง"}, status=400)

    note = ReportNote.objects.create(
        report=report,
        text=message
    )

    return Response({
        "message": "เพิ่มโน้ตแล้ว",
        "note": ReportNoteSerializer(note).data
    }, status=201)


# =====================================================
# 8) ADMIN แก้ไขเสร็จแล้ว → resolved
# =====================================================
@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def report_done(request, pk):

    if request.user.role != "admin":
        return Response({"detail": "คุณไม่มีสิทธิ์"}, status=403)

    try:
        report = Report.objects.get(pk=pk)
    except Report.DoesNotExist:
        return Response({"detail": "ไม่พบรายงานนี้"}, status=404)

    report.status = "resolved"
    report.save()

    return Response({"message": "อัปเดตสถานะแล้วเสร็จ"}, status=200)


# =====================================================
# 9) ADMIN Rollback → processing
# =====================================================
@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def report_rollback(request, pk):

    if request.user.role != "admin":
        return Response({"detail": "คุณไม่มีสิทธิ์"}, status=403)

    try:
        report = Report.objects.get(pk=pk)
    except Report.DoesNotExist:
        return Response({"detail": "ไม่พบรายงานนี้"}, status=404)

    report.status = "processing"
    report.save()

    return Response({"message": "ย้อนกลับสถานะเป็นกำลังดำเนินการ"}, status=200)


# =====================================================
# ADMIN: แสดงรายงานตามสถานะ
# =====================================================
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def admin_reports_pending(request):
    if request.user.role != "admin":
        return Response({"detail": "คุณไม่มีสิทธิ์"}, status=403)

    reports = Report.objects.filter(status="pending").order_by("-created_at")
    return Response(ReportSerializer(reports, many=True).data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def admin_reports_processing(request):
    if request.user.role != "admin":
        return Response({"detail": "คุณไม่มีสิทธิ์"}, status=403)

    reports = Report.objects.filter(status="processing").order_by("-created_at")
    return Response(ReportSerializer(reports, many=True).data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def admin_reports_resolved(request):
    if request.user.role != "admin":
        return Response({"detail": "คุณไม่มีสิทธิ์"}, status=403)

    reports = Report.objects.filter(status="resolved").order_by("-created_at")
    return Response(ReportSerializer(reports, many=True).data)


# =====================================================
# 10) USER ส่งคำขอความอนุเคราะห์
# =====================================================
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_request_help(request):
    print("DEBUG DATA:", request.data)

    data = request.data.copy()
    data["user"] = request.user.id

    serializer = RequestHelpSerializer(data=data)
    if serializer.is_valid():
        serializer.save(user=request.user)
        return Response(serializer.data, status=201)

    print("DEBUG ERROR:", serializer.errors)
    return Response(serializer.errors, status=400)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_my_request_help(request, pk):
    try:
        req = RequestHelp.objects.get(pk=pk, user=request.user)
    except RequestHelp.DoesNotExist:
        return Response({"detail": "ไม่พบคำขอนี้"}, status=404)

    return Response(RequestHelpSerializer(req).data)

# =====================================================
# 11) USER ดูคำขอของตัวเอง
# =====================================================
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def my_request_help(request):
    help_list = RequestHelp.objects.filter(user=request.user).order_by("-created_at")
    return Response(RequestHelpSerializer(help_list, many=True).data)


# =====================================================
# 12) ADMIN ดูคำขอทั้งหมด
# =====================================================
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def admin_request_help(request):
    if request.user.role != "admin":
        return Response({"detail": "ไม่มีสิทธิ์"}, status=403)

    helps = RequestHelp.objects.all().order_by("-created_at")
    return Response(RequestHelpSerializer(helps, many=True).data)


# =====================================================
# 13) ADMIN อนุมัติคำขอ
# =====================================================
@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def request_help_approve(request, pk):

    if request.user.role != "admin":
        return Response({"detail": "ไม่มีสิทธิ์"}, status=403)

    help_obj = RequestHelp.objects.get(pk=pk)
    help_obj.status = "approved"
    help_obj.save()

    return Response({"message": "อนุมัติแล้ว"})


# =====================================================
# 14) USER แก้ไขคำขอของตัวเอง
# =====================================================
@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def update_my_request(request, pk):

    try:
        req = RequestHelp.objects.get(pk=pk, user=request.user)
    except RequestHelp.DoesNotExist:
        return Response({"detail": "ไม่พบคำขอนี้"}, status=404)

    if req.status in ["approved", "rejected", "done"]:
        return Response({"detail": "ไม่สามารถแก้ไขคำขอนี้ได้"}, status=400)

    serializer = RequestHelpSerializer(req, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()
        return Response({"message": "แก้ไขคำขอสำเร็จ", "data": serializer.data}, status=200)

    return Response(serializer.errors, status=400)


# =====================================================
# 15) USER ยกเลิกคำขอของตัวเอง  ← (เพิ่มใหม่!!)
# =====================================================
@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def cancel_my_request(request, pk):

    try:
        req = RequestHelp.objects.get(pk=pk, user=request.user)
    except RequestHelp.DoesNotExist:
        return Response({"detail": "ไม่พบคำขอนี้"}, status=404)

    if req.status != "pending":
        return Response({"detail": "คำขอนี้ไม่สามารถยกเลิกได้"}, status=400)

    req.status = "rejected"
    req.save()

    return Response({"message": "ยกเลิกคำขอแล้ว"}, status=200)


# =====================================================
# 16) ADMIN สถิติระบบ
# =====================================================
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def admin_statistics(request):

    if request.user.role != "admin":
        return Response({"detail": "ไม่มีสิทธิ์"}, status=403)

    # รายงานร้องเรียน
    report_qs = (
        Report.objects.values("category")
        .annotate(total=Count("id"))
        .order_by("category")
    )

    reports_by_category = {
        item["category"]: item["total"] for item in report_qs
    }

    # คำขอความอนุเคราะห์
    request_qs = (
        RequestHelp.objects.values("request_type")
        .annotate(total=Count("id"))
        .order_by("request_type")
    )

    requests_by_type = {
        (item["request_type"] or "ไม่ระบุ"): item["total"]
        for item in request_qs
    }

    return Response({
        "reports_by_category": reports_by_category,
        "requests_by_type": requests_by_type
    })


# =====================================================
# 17) ADMIN สถิติ (แบบ fix category)
# =====================================================
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def admin_stats(request):

    if request.user.role != "admin":
        return Response({"detail": "ไม่มีสิทธิ์"}, status=403)

    categories = ["ไฟฟ้า", "น้ำ", "ถนน", "บุคคล", "เสียง", "กลิ่น"]
    reports_by_category = {
        c: Report.objects.filter(category=c).count()
        for c in categories
    }

    types = ["เสียง", "ปิดทาง", "ทั้งสองอย่าง", "อื่นๆ"]
    requests_by_type = {
        t: RequestHelp.objects.filter(request_type=t).count()
        for t in types
    }

    return Response({
        "reports_by_category": reports_by_category,
        "requests_by_type": requests_by_type
    })
