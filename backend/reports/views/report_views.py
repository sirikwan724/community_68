from django.db.models import Count
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from ..models import Report, ReportNote
from ..serializers import ReportSerializer, ReportNoteSerializer


# =====================================================
# 1) USER ส่งรายงาน (CREATE)
# =====================================================
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_report(request):

    data = request.data.copy()
    data["user"] = request.user.id
    data["fullname"] = request.user.full_name
    data["phone"] = request.user.phone

    serializer = ReportSerializer(data=data)

    if serializer.is_valid():
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

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

    if request.user.role != "admin" and report.user != request.user:
        return Response({"detail": "คุณไม่มีสิทธิ์เข้าถึงรายงานนี้"}, status=403)

    if request.method == "GET":
        return Response(ReportSerializer(report).data)

    if report.status != "pending":
        return Response({"detail": "รายงานนี้ถูกรับเรื่องแล้ว แก้ไขไม่ได้"}, status=400)

    serializer = ReportSerializer(report, data=request.data, partial=True)
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
@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def report_cancel(request, pk):

    try:
        report = Report.objects.get(pk=pk, user=request.user)
    except Report.DoesNotExist:
        return Response({"detail": "ไม่พบรายงานนี้"}, status=404)

    if report.status != "pending":
        return Response({"detail": "ไม่สามารถยกเลิกได้"}, status=400)

    report.status = "canceled"
    report.save()
    
    return Response({"message": "ยกเลิกคำร้องสำเร็จ"})


# =====================================================
# 6) ADMIN รับเรื่อง → processing
# =====================================================
@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def report_accept(request, pk):

    if request.user.role != "admin":
        return Response({"detail": "คุณไม่มีสิทธิ์"}, status=403)

    report = Report.objects.get(pk=pk)
    report.status = "processing"
    report.save()

    return Response({"message": "รับเรื่องแล้ว"})


# =====================================================
# 7) ADMIN เพิ่มโน้ตในรายงาน
# =====================================================
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def report_add_note(request, pk):

    if request.user.role != "admin":
        return Response({"detail": "คุณไม่มีสิทธิ์"}, status=403)

    report = Report.objects.get(pk=pk)

    message = request.data.get("message", "").strip()
    if not message:
        return Response({"detail": "โน้ตต้องไม่ว่าง"}, status=400)

    note = ReportNote.objects.create(report=report, text=message)

    return Response({
        "message": "เพิ่มโน้ตแล้ว",
        "note": ReportNoteSerializer(note).data
    })


# =====================================================
# 8) ADMIN แก้ไขเสร็จแล้ว → resolved
# =====================================================
@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def report_done(request, pk):

    if request.user.role != "admin":
        return Response({"detail": "คุณไม่มีสิทธิ์"}, status=403)

    report = Report.objects.get(pk=pk)
    report.status = "resolved"
    report.save()

    message = request.data.get("message", "").strip()
    if message:
        ReportNote.objects.create(report=report, text=message)

    return Response({"message": "อัปเดตสถานะแล้วเสร็จ"})


# =====================================================
# 9) ADMIN Rollback → processing
# =====================================================
@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def report_rollback(request, pk):

    if request.user.role != "admin":
        return Response({"detail": "คุณไม่มีสิทธิ์"}, status=403)

    report = Report.objects.get(pk=pk)
    report.status = "processing"
    report.save()

    return Response({"message": "ย้อนกลับสถานะเป็นกำลังดำเนินการ"})


# =====================================================
# ADMIN: แสดงรายงานตามสถานะ
# =====================================================
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def admin_reports_pending(request):

    if request.user.role != "admin":
        return Response({"detail": "คุณไม่มีสิทธิ์"}, status=403)

    reports = Report.objects.filter(status="pending")
    return Response(ReportSerializer(reports, many=True).data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def admin_reports_processing(request):

    if request.user.role != "admin":
        return Response({"detail": "คุณไม่มีสิทธิ์"}, status=403)

    reports = Report.objects.filter(status="processing")
    return Response(ReportSerializer(reports, many=True).data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def admin_reports_resolved(request):

    if request.user.role != "admin":
        return Response({"detail": "คุณไม่มีสิทธิ์"}, status=403)

    reports = Report.objects.filter(status="resolved")
    return Response(ReportSerializer(reports, many=True).data)
