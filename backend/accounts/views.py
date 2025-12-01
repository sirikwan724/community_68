import re
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.response import Response
from rest_framework import status, viewsets, permissions, generics
from django.db import transaction  # เพิ่ม Transaction เพื่อความปลอดภัยข้อมูล

from django.contrib.auth import get_user_model
# นำเข้า Model และ Serializer ที่ต้องใช้
from .models import RegistrationRequest, News, HeadmanStatus
from .serializers import (
    RegistrationRequestSerializer, 
    UserUpdateSerializer, 
    NewsSerializer,
    MyTokenObtainPairSerializer
)
from rest_framework_simplejwt.views import TokenObtainPairView

User = get_user_model()

def generate_unique_username(base_name):
    """สร้าง username จากชื่อเต็ม โดยจัดการให้ไม่ซ้ำกัน"""
    #  ลบช่องว่างและเปลี่ยนเป็นตัวพิมพ์เล็ก
    base_username = re.sub(r'[^a-z0-9]', '', base_name.replace(' ', '').lower())
    
    #  ตรวจสอบว่า username นี้มีอยู่แล้วหรือไม่
    if not User.objects.filter(username=base_username).exists():
        return base_username
    
    #  ถ้ามีอยู่แล้ว ให้เพิ่มตัวเลขต่อท้าย
    i = 1
    while True:
        new_username = f"{base_username}{i}"
        if not User.objects.filter(username=new_username).exists():
            return new_username
        i += 1

# ส่วนจัดการข่าวสาร (News)
class NewsViewSet(viewsets.ModelViewSet):
    queryset = News.objects.all()
    serializer_class = NewsSerializer
    
    # กำหนดสิทธิ์: คนทั่วไปดูได้ (GET) แต่ถ้าจะแก้ไข/ลบ ต้องเป็น Admin
    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS: # GET, HEAD, OPTIONS
            return [permissions.AllowAny()] 
        return [permissions.IsAdminUser()] 

    # บันทึกอัตโนมัติว่าใครเป็นคนโพสต์
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


# ส่วนจัดการผู้ใช้งาน (User & Auth)

# Custom Token View เพื่อให้ส่ง role กลับไปด้วยตอน Login
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_users(request):
    if request.user.role != "admin":
        return Response({"detail": "คุณไม่มีสิทธิ์"}, status=403)

    users = User.objects.filter(role="user")
    data = [
        {
            "id": u.id,
            "full_name": u.full_name,
            "citizen_id": u.citizen_id,
            "address": u.address,
            "phone": u.phone,
        }
        for u in users
    ]
    return Response(data)

# ส่งคำขอสมัครสมาชิก
@api_view(['POST'])
def register_request(request):
    serializer = RegistrationRequestSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response(
            {"message": "ส่งคำขอสมัครสำเร็จ รอผู้ใหญ่บ้านอนุมัติ"},
            status=status.HTTP_201_CREATED
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ดูข้อมูลผู้ใช้ที่กำลัง Login อยู่
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me(request):
    user = request.user

    # แยกชื่อ-นามสกุล เพื่อให้ Frontend แสดงผลสวยๆ
    first = user.full_name.split(' ')[0] if user.full_name else user.username
    
    data = {
        "id": user.id,
        "username": user.username,
        "full_name": user.full_name,
        "first_name": first,
        "address": user.address,
        "phone": user.phone,
        "citizen_id": user.citizen_id,
        "house_owner_name": user.house_owner_name,
        "role": user.role,
        "verified": user.verified,
    }

    return Response(data)

# แก้ไขโปรไฟล์
@api_view(["PUT", "PATCH"])
@permission_classes([IsAuthenticated])
def update_profile(request):
    user = request.user
    data = request.data

    # อัปเดตตรงๆ เลย ไม่ต้อง pending
    user.full_name = data.get("full_name", user.full_name)
    user.phone = data.get("phone", user.phone)
    user.address = data.get("address", user.address)
    user.house_number = data.get("house_number", user.house_number)
    user.village = data.get("village", user.village)

    user.save()

    return Response({"detail": "Profile updated", "user": UserSerializer(user).data})



# ส่วนของผู้ใหญ่บ้าน (Admin Actions)

# ดูคำขอทั้งหมด
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def request_list(request):
    if request.user.role != "admin":
        return Response({"detail": "คุณไม่มีสิทธิ์เข้าถึงข้อมูลนี้"}, status=403)

    requests = RegistrationRequest.objects.filter(status="pending").order_by("-id")
    serializer = RegistrationRequestSerializer(requests, many=True)
    return Response(serializer.data)

# 📌 ดึงคำขอทั้งหมด (pending + approved + rejected)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def request_all(request):
    if request.user.role != "admin":
        return Response({"detail": "คุณไม่มีสิทธิ์เข้าถึงข้อมูลนี้"}, status=403)

    requests = RegistrationRequest.objects.all().order_by("-id")
    serializer = RegistrationRequestSerializer(requests, many=True)
    return Response(serializer.data)

# ดูคำขอรายบุคคล
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def request_detail(request, pk):
    if request.user.role != "admin":
        return Response({"detail": "คุณไม่มีสิทธิ์"}, status=403)

    try:
        req = RegistrationRequest.objects.get(pk=pk)
    except RegistrationRequest.DoesNotExist:
        return Response({"detail": "ไม่พบคำขอ"}, status=404)

    serializer = RegistrationRequestSerializer(req)
    return Response(serializer.data)


# อนุมัติ → สร้าง User จริง
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def request_approve(request, pk):
    # 1. ตรวจสอบสิทธิ์ Admin ทันที
    if request.user.role != "admin":
        return Response({"detail": "คุณไม่มีสิทธิ์"}, status=403)
    
    # 2. ดึงข้อมูลคำขอ (req) และจัดการ Exception
    try:
        req = RegistrationRequest.objects.get(pk=pk)
    except RegistrationRequest.DoesNotExist:
        return Response({"detail": "ไม่พบคำขอ"}, status=404)

    # 3. ตรวจสอบสถานะ (ควรอยู่หลังจากการดึง req)
    if req.status != "pending":
        return Response({"detail": "คำขอนี้ได้รับการพิจารณาแล้ว"}, status=400)

    # 4. กำหนด Username และจัดการ Transaction
    try:
        # กำหนด username: ใช้ full_name เป็นค่าเริ่มต้น, อนุญาตให้ Admin กำหนดเอง
        admin_defined_username = request.data.get('username')
        
        # ⭐ โค้ดนี้จะใช้ generate_unique_username ที่คุณต้องวางไว้ในไฟล์เดียวกัน
        if admin_defined_username:
            final_username = generate_unique_username(admin_defined_username)
        else:
            final_username = generate_unique_username(req.full_name)

        # การสำรองข้อมูล (Fallback): ถ้า username ที่สร้างขึ้นมาว่าง ให้ใช้ citizen_id แทน
        if not final_username:
            final_username = req.citizen_id

        with transaction.atomic():
            # 1. สร้าง User จริง (Password Hash มาแล้ว ห้าม Hash ซ้ำ)
            user = User(
                # ⭐ แก้ไขบรรทัดนี้: ใช้ final_username แทน req.citizen_id
                username=final_username, 
                full_name=req.full_name,
                address=req.address,
                phone=req.phone,
                citizen_id=req.citizen_id,
                house_owner_name=req.house_owner_name,
                role="user",
                verified=True,
                is_active=True
            )
            user.password = req.password  # Assign hashed password directly
            user.save()

            # 2. อัพเดทสถานะคำขอ
            req.status = "approved"
            req.save()

        return Response(
            {"message": f"อนุมัติสำเร็จ และสร้างบัญชีผู้ใช้แล้ว (Username: {final_username})", "user_id": user.id, "username": final_username},
            status=200
        )
        
    except Exception as e:
        return Response({"detail": f"เกิดข้อผิดพลาด: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# ปฏิเสธคำขอ
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def request_reject(request, pk):
    if request.user.role != "admin":
        return Response({"detail": "คุณไม่มีสิทธิ์"}, status=403)

    try:
        req = RegistrationRequest.objects.get(pk=pk)
    except RegistrationRequest.DoesNotExist:
        return Response({"detail": "ไม่พบคำขอ"}, status=404)

    if req.status != "pending":
        return Response({"detail": "คำขอนี้ได้รับการพิจารณาแล้ว"}, status=400)

    req.status = "rejected"
    req.save()

    return Response({"message": "ปฏิเสธสำเร็จ"}, status=200)

class NewsCreateAPIView(generics.CreateAPIView):
    queryset = News.objects.all()
    serializer_class = NewsSerializer
    # มีแค่ Admin เท่านั้นที่ควรสร้างข่าวสารได้
    permission_classes = [IsAdminUser] 

# 📌 ดึงสถานะล่าสุด
@api_view(["GET"])
def headman_status(request):
    status_obj, _ = HeadmanStatus.objects.get_or_create(id=1)
    return Response({"is_online": status_obj.is_online})


# 📌 เปลี่ยนสถานะ (เฉพาะ admin)
@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def update_headman_status(request):
    if request.user.role != "admin":
        return Response({"detail": "คุณไม่มีสิทธิ์"}, status=403)

    status_obj, _ = HeadmanStatus.objects.get_or_create(id=1)
    new_status = request.data.get("is_online", False)
    status_obj.is_online = bool(new_status)
    status_obj.save()

    return Response({"message": "อัปเดตสถานะสำเร็จ", "is_online": status_obj.is_online})