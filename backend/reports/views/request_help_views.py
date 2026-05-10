from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from ..models import RequestHelp
from ..serializers import RequestHelpSerializer


# =====================================================
# 10) USER ส่งคำขอความอนุเคราะห์
# =====================================================
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_request_help(request):
    data = request.data.copy()
    data["user"] = request.user.id

    serializer = RequestHelpSerializer(data=data)
    if serializer.is_valid():
        serializer.save(user=request.user)
        return Response(serializer.data, status=201)

    return Response(serializer.errors, status=400)


# =====================================================
# USER: ดูคำขอของตัวเองทั้งหมด
# =====================================================
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def my_request_help(request):
    help_list = RequestHelp.objects.filter(user=request.user).order_by("-created_at")
    return Response(RequestHelpSerializer(help_list, many=True).data)


# =====================================================
# USER: ดูคำขอของตัวเอง (รายตัว)
# =====================================================
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_my_request_help(request, pk):
    try:
        req = RequestHelp.objects.get(pk=pk, user=request.user)
    except RequestHelp.DoesNotExist:
        return Response({"detail": "ไม่พบคำขอนี้"}, status=404)

    return Response(RequestHelpSerializer(req).data)


# =====================================================
# USER: แก้ไขคำขอของตัวเอง
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
        return Response(serializer.data)

    return Response(serializer.errors, status=400)


# =====================================================
# USER: ยกเลิกคำขอของตัวเอง
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

    req.status = "canceled"
    req.save()

    return Response({"message": "ยกเลิกคำขอแล้ว"})


# =====================================================
# ADMIN: ดูคำขอทั้งหมด
# =====================================================
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def admin_request_help(request):
    if request.user.role != "admin":
        return Response({"detail": "ไม่มีสิทธิ์"}, status=403)

    helps = RequestHelp.objects.all().order_by("-created_at")
    return Response(RequestHelpSerializer(helps, many=True).data)


# =====================================================
# ADMIN: อนุมัติคำขอ
# =====================================================
@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def request_help_approve(request, pk):
    if request.user.role != "admin":
        return Response({"detail": "ไม่มีสิทธิ์"}, status=403)

    try:
        help_obj = RequestHelp.objects.get(pk=pk)
    except RequestHelp.DoesNotExist:
        return Response({"detail": "ไม่พบคำขอนี้"}, status=404)

    help_obj.status = "approved"
    help_obj.save()

    return Response({"message": "อนุมัติแล้ว"})

# =====================================================
# ADMIN: ปฏิเสธคำขอ
# =====================================================
@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def request_help_reject(request, pk):
    if request.user.role != "admin":
        return Response({"detail": "ไม่มีสิทธิ์"}, status=403)

    try:
        help_obj = RequestHelp.objects.get(pk=pk)
    except RequestHelp.DoesNotExist:
        return Response({"detail": "ไม่พบคำขอนี้"}, status=404)

    if help_obj.status in ["rejected", "done", "canceled"]:
        return Response({"detail": "ไม่สามารถเปลี่ยนสถานะได้"}, status=400)

    help_obj.status = "rejected"
    help_obj.reject_reason = request.data.get("reason", "")
    help_obj.save()

    return Response({"message": "ปฏิเสธคำขอแล้ว"})


# =====================================================
# ADMIN: ปิดงาน (done)
# =====================================================
@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def request_help_done(request, pk):
    if request.user.role != "admin":
        return Response({"detail": "ไม่มีสิทธิ์"}, status=403)

    try:
        help_obj = RequestHelp.objects.get(pk=pk)
    except RequestHelp.DoesNotExist:
        return Response({"detail": "ไม่พบคำขอนี้"}, status=404)

    if help_obj.status != "approved":
        return Response({"detail": "ต้องอนุมัติก่อนถึงจะปิดงานได้"}, status=400)

    help_obj.status = "done"
    help_obj.save()

    return Response({"message": "ปิดงานเสร็จสิ้น"})