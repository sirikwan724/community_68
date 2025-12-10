from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import Appointment
from .serializers import AppointmentSerializer


# ============================================
# 1) USER: สร้างนัดหมาย
# ============================================
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_appointment(request):
    data = request.data.copy()
    data["user"] = request.user.id

    serializer = AppointmentSerializer(data=data)
    if serializer.is_valid():
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ============================================
# 2) USER: ดูนัดหมายของตัวเอง
# ============================================
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def my_appointments(request):
    appointments = Appointment.objects.filter(user=request.user).order_by("-date")
    serializer = AppointmentSerializer(appointments, many=True)
    return Response(serializer.data)


# ============================================
# 3) ADMIN: ดูนัดหมายทั้งหมด
# ============================================
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def admin_list_appointments(request):

    if request.user.role != "admin":
        return Response({"detail": "คุณไม่มีสิทธิ์เข้าถึง"}, status=403)

    appointments = Appointment.objects.all().order_by("-date")
    serializer = AppointmentSerializer(appointments, many=True)
    return Response(serializer.data)


# ============================================
# 4) ADMIN: อนุมัตินัดหมาย
# ============================================
@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def accept_appointment(request, id):

    if request.user.role != "admin":
        return Response({"detail": "คุณไม่มีสิทธิ์"}, status=403)

    try:
        appointment = Appointment.objects.get(id=id)
    except Appointment.DoesNotExist:
        return Response({"error": "ไม่พบนัดหมาย"}, status=404)

    appointment.status = "approved"
    appointment.save()

    return Response({"message": "อนุมัติสำเร็จ", "status": "approved"}, status=200)


# ============================================
# 5) ADMIN: ปฏิเสธนัดหมาย
# ============================================
@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def reject_appointment(request, id):

    if request.user.role != "admin":
        return Response({"detail": "คุณไม่มีสิทธิ์"}, status=403)

    try:
        appointment = Appointment.objects.get(id=id)
    except Appointment.DoesNotExist:
        return Response({"error": "ไม่พบนัดหมาย"}, status=404)

    appointment.status = "rejected"
    appointment.save()

    return Response({"message": "ปฏิเสธสำเร็จ", "status": "rejected"}, status=200)


# ============================================
# 6) (Optional) ADMIN: ดำเนินการเสร็จสิ้น
# ============================================
@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def done_appointment(request, id):

    if request.user.role != "admin":
        return Response({"detail": "คุณไม่มีสิทธิ์"}, status=403)

    try:
        appointment = Appointment.objects.get(id=id)
    except Appointment.DoesNotExist:
        return Response({"error": "ไม่พบนัดหมาย"}, status=404)

    appointment.status = "done"
    appointment.save()

    return Response({"message": "ดำเนินการเสร็จสิ้น", "status": "done"}, status=200)
