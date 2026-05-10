from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from ..models import Appointment
from ..serializers import AppointmentSerializer

from datetime import date, datetime, time as time_type

# ===============================
# APPOINTMENT (USER)
# ===============================

# 1) USER: สร้างนัดหมาย
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_appointment(request):
    data = request.data.copy()
    data["user"] = request.user.id
    # ตรวจสอบวันที่
    appointment_date = request.data.get("date")
    appointment_start = request.data.get("start_time")
    appointment_end = request.data.get("end_time")

    try:
        appt_date = date.fromisoformat(appointment_date)
        appt_start = time_type.fromisoformat(appointment_start)
        appt_end = time_type.fromisoformat(appointment_end)
    except (ValueError, TypeError):
        return Response({"detail": "รูปแบบวันที่หรือเวลาไม่ถูกต้อง"}, status=400)

    today = date.today()
    now = datetime.now().time()

    if appt_date < today:
        return Response({"detail": "ไม่สามารถนัดหมายวันที่ผ่านมาแล้วได้"}, status=400)

    if appt_date == today and appt_start < now:
        return Response({"detail": "ไม่สามารถนัดหมายเวลาที่ผ่านมาแล้วได้"}, status=400)

    if appt_end <= appt_start:
        return Response({"detail": "เวลาสิ้นสุดต้องมากกว่าเวลาเริ่มต้น"}, status=400)

    serializer = AppointmentSerializer(data=data)
    if serializer.is_valid():
        serializer.save(user=request.user)
        return Response(serializer.data, status=201)

    return Response(serializer.errors, status=400)


# 2) USER: ดูนัดหมายของตัวเอง
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def my_appointments(request):
    appointments = Appointment.objects.filter(
        user=request.user
    ).order_by("-created_at")

    serializer = AppointmentSerializer(appointments, many=True)
    return Response(serializer.data, status=200)


# 3) USER: ยกเลิกนัดหมายของตัวเอง
@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def cancel_appointment(request, pk):
    try:
        appointment = Appointment.objects.get(pk=pk, user=request.user)
    except Appointment.DoesNotExist:
        return Response({"detail": "ไม่พบนัดหมายนี้"}, status=404)

    if appointment.status != "pending":
        return Response(
            {"detail": "ไม่สามารถยกเลิกนัดหมายนี้ได้"},
            status=400
        )

    appointment.status = "canceled"
    appointment.save()

    return Response({"message": "ยกเลิกนัดหมายสำเร็จ"}, status=200)


# ===============================
# APPOINTMENT (ADMIN)
# ===============================

# 4) ADMIN: ดูนัดหมายทั้งหมด
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def admin_appointments(request):
    if request.user.role != "admin":
        return Response({"detail": "คุณไม่มีสิทธิ์"}, status=403)

    appointments = Appointment.objects.all().order_by("-created_at")
    serializer = AppointmentSerializer(appointments, many=True)
    return Response(serializer.data, status=200)


# 5) ADMIN: อนุมัตินัดหมาย
@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def approve_appointment(request, pk):
    if request.user.role != "admin":
        return Response({"detail": "คุณไม่มีสิทธิ์"}, status=403)

    try:
        appointment = Appointment.objects.get(pk=pk)
    except Appointment.DoesNotExist:
        return Response({"detail": "ไม่พบนัดหมายนี้"}, status=404)

    appointment.status = "approved"
    appointment.save()

    return Response({"message": "อนุมัตินัดหมายแล้ว"}, status=200)


# 6) ADMIN: ปฏิเสธนัดหมาย
@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def reject_appointment(request, pk):
    if request.user.role != "admin":
        return Response({"detail": "คุณไม่มีสิทธิ์"}, status=403)

    try:
        appointment = Appointment.objects.get(pk=pk)
    except Appointment.DoesNotExist:
        return Response({"detail": "ไม่พบนัดหมายนี้"}, status=404)
    
    note = request.data.get("note", "").strip()
    if not note:
        return Response({"detail": "กรุณาระบุเหตุผลการปฏิเสธ"}, status=400)

    appointment.status = "rejected"
    appointment.admin_note = note
    appointment.save()

    return Response({"message": "ปฏิเสธนัดหมายแล้ว"}, status=200)


# 7) ADMIN: เพิ่มหมายเหตุ
@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def add_appointment_note(request, pk):
    if request.user.role != "admin":
        return Response({"detail": "คุณไม่มีสิทธิ์"}, status=403)

    try:
        appointment = Appointment.objects.get(pk=pk)
    except Appointment.DoesNotExist:
        return Response({"detail": "ไม่พบนัดหมายนี้"}, status=404)

    note = request.data.get("note", "").strip()
    if not note:
        return Response({"detail": "กรุณากรอกหมายเหตุ"}, status=400)

    appointment.admin_note = note
    appointment.save()

    return Response({"message": "เพิ่มหมายเหตุสำเร็จ"}, status=200)

#  ADMIN: ทำเครื่องหมายว่าเสร็จสิ้น
@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def done_appointment(request, pk):
    if request.user.role != "admin":
        return Response({"detail": "คุณไม่มีสิทธิ์"}, status=403)

    try:
        appointment = Appointment.objects.get(pk=pk)
    except Appointment.DoesNotExist:
        return Response({"detail": "ไม่พบนัดหมายนี้"}, status=404)

    if appointment.status != "approved":
        return Response(
            {"detail": "สามารถทำเครื่องหมายเสร็จสิ้นได้เฉพาะนัดหมายที่อนุมัติแล้วเท่านั้น"},
            status=400
        )

    appointment.status = "done"
    appointment.save()

    return Response({"message": "อัปเดตเป็นเสร็จสิ้นแล้ว"}, status=200)

#  USER: ดู / แก้ไขนัดหมายของตัวเอง
@api_view(["GET", "PATCH"])
@permission_classes([IsAuthenticated])
def appointment_detail(request, pk):
    try:
        appointment = Appointment.objects.get(pk=pk, user=request.user)
    except Appointment.DoesNotExist:
        return Response(
            {"detail": "ไม่พบนัดหมายนี้"},
            status=404
        )

    # GET: โหลดข้อมูลเดิม
    if request.method == "GET":
        serializer = AppointmentSerializer(appointment)
        return Response(serializer.data, status=200)

    # PATCH: แก้ไขข้อมูล
    if request.method == "PATCH":

        # ป้องกันแก้ไข ถ้าไม่ใช่ pending
        if appointment.status != "pending":
            return Response(
                {"detail": "ไม่สามารถแก้ไขนัดหมายนี้ได้"},
                status=400
            )
        
        new_date = request.data.get("date", str(appointment.date))
        new_start = request.data.get("start_time", str(appointment.start_time))
        new_end = request.data.get("end_time", str(appointment.end_time))

        try:
            appt_date = date.fromisoformat(new_date)
            appt_start = time_type.fromisoformat(new_start)
            appt_end = time_type.fromisoformat(new_end)
        except (ValueError, TypeError):
            return Response({"detail": "รูปแบบวันที่หรือเวลาไม่ถูกต้อง"}, status=400)

        today = date.today()
        now = datetime.now().time()

        if appt_date < today:
            return Response({"detail": "ไม่สามารถนัดหมายวันที่ผ่านมาแล้วได้"}, status=400)

        if appt_date == today and appt_start < now:
            return Response({"detail": "ไม่สามารถนัดหมายเวลาที่ผ่านมาแล้วได้"}, status=400)

        if appt_end <= appt_start:
            return Response({"detail": "เวลาสิ้นสุดต้องมากกว่าเวลาเริ่มต้น"}, status=400)

        serializer = AppointmentSerializer(
            appointment,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)

        return Response(serializer.errors, status=400)
