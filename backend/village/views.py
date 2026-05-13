import re
from decimal import Decimal

import pandas as pd
from django.db.models import Case, When, IntegerField
from django.shortcuts import get_object_or_404

from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser

from .models import (
    Village,
    VillageSection,
    VillageSectionImage,
    VillagePlace,
    VillagePlaceImage,
    CommunityProfile,
    FundType,
    FundRecord,
    FundLoan,
)

from .serializers import (
    VillageSerializer,
    VillageSectionSerializer,
    VillageSectionImageSerializer,
    VillagePlaceSerializer,
    VillagePlaceImageSerializer,
    CommunityProfileSerializer,
    FundTypeSerializer,
    FundRecordSerializer,
    FundLoanSerializer,
)

class IsAdminRole(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role in ["admin", "superadmin"]
        )
    
# -----------------------------
# Helpers for Excel import
# -----------------------------
def normalize(text):
    return re.sub(r"[ \-–_()/]", "", str(text)).lower().strip()

def find_header_row(df):
    required_keywords = ["ชื่อ", "บัญชี", "เงิน"]
    for i in range(len(df)):
        row = df.iloc[i]
        non_empty_cells = [str(cell) for cell in row if pd.notna(cell)]
        if len(non_empty_cells) < 3:
            continue

        match_count = 0
        for cell in non_empty_cells:
            cell_clean = normalize(cell)
            for keyword in required_keywords:
                if cell_clean == normalize(keyword) or normalize(keyword) in cell_clean:
                    match_count += 1

        if match_count >= 2:
            return i
    return None

def find_column(df, keywords):
    for col in df.columns:
        col_clean = normalize(col)
        for key in keywords:
            if normalize(key) in col_clean:
                return col
    return None

# -----------------------------
# Fund: Import Excel
# -----------------------------
class FundLoanExcelImportAPIView(APIView):
    permission_classes = [IsAdminRole]
    parser_classes = [MultiPartParser]

    def post(self, request, record_id):
        file = request.FILES.get("file")
        if not file:
            return Response({"detail": "ไม่พบไฟล์"}, status=400)

        fund_record = get_object_or_404(FundRecord, id=record_id)

        df_raw = pd.read_excel(file, header=None)
        header_row = find_header_row(df_raw)
        if header_row is None:
            return Response({"detail": "ไม่พบหัวตาราง"}, status=400)
        
        file.seek(0)
        df = pd.read_excel(file, header=header_row)
        df.columns = df.columns.str.strip()

        COLUMN_MAP = {
            "full_name": ["ชื่อ"],
            "bank_account": ["บัญชี", "เลขที่บัญชี"],
            "loan_amount": ["เงิน", "อนุมัติ", "จำนวนเงิน"],
            "purpose": ["วัตถุประสงค์", "อาชีพ"],
        }

        col_fullname = find_column(df, COLUMN_MAP["full_name"])
        col_account = find_column(df, COLUMN_MAP["bank_account"])
        col_amount = find_column(df, COLUMN_MAP["loan_amount"])
        col_purpose = find_column(df, COLUMN_MAP["purpose"])

        if not all([col_fullname, col_account, col_amount]):
            return Response({"detail": "รูปแบบไฟล์ไม่ถูกต้อง"}, status=400)

        FundLoan.objects.filter(fund_record=fund_record).delete()

        created = 0
        skipped = 0

        for _, row in df.iterrows():
            try:
                raw_amount = str(row[col_amount]).replace(",", "").strip()
                if not raw_amount or not raw_amount.replace(".", "").isdigit():
                    skipped += 1
                    continue

                loan_amount = Decimal(raw_amount)
                interest = loan_amount * fund_record.interest_rate / Decimal(100)

                FundLoan.objects.create(
                    fund_record=fund_record,
                    full_name=row[col_fullname] if col_fullname else "",
                    bank_account=str(row[col_account]) if col_account else "",
                    loan_amount=loan_amount,
                    interest_amount=interest,
                    purpose=row[col_purpose] if col_purpose else "",
                )
                created += 1
            except Exception:
                skipped += 1
                continue

        fund_record.last_uploaded_file = file.name
        fund_record.save()

        return Response({"message": f"นำเข้าข้อมูลสำเร็จ {created} รายการ", "skipped": skipped})

# -----------------------------
# Public: Village Full (ใหม่)
# -----------------------------
class VillageFullAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        village = Village.objects.first()
        if not village:
            return Response({"detail": "ไม่พบข้อมูลหมู่บ้าน"}, status=404)

        sections = VillageSection.objects.all().order_by("order", "id")
        data = {
            "overview": VillageSerializer(village, context={"request": request}).data,
            "sections": VillageSectionSerializer(sections, many=True, context={"request": request}).data,
        }
        return Response(data)


# -----------------------------
# Public: Profiles
# -----------------------------
class CommunityProfileListAPIView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = CommunityProfileSerializer

    def get_queryset(self):
        village = Village.objects.first()
        return CommunityProfile.objects.filter(village=village).annotate(
            group_order=Case(
                When(group="leader", then=1),
                When(group="committee", then=2),
                When(group="volunteer", then=3),
                output_field=IntegerField()
            )
        ).order_by("group_order", "level")

# -----------------------------
# Public: Funds
# -----------------------------
class FundTypeListAPIView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = FundTypeSerializer

    def get_queryset(self):
        village = Village.objects.first()
        return FundType.objects.filter(village=village, is_active=True)

class FundRecordListAPIView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = FundRecordSerializer

    def get_queryset(self):
        fund_id = self.kwargs["fund_id"]
        return FundRecord.objects.filter(fund_type_id=fund_id).order_by("-year")

class FundLoanListAPIView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = FundLoanSerializer

    def get_queryset(self):
        record_id = self.kwargs["record_id"]
        return FundLoan.objects.filter(fund_record_id=record_id)


# -----------------------------
# Admin: Village Overview
# -----------------------------
class VillageAdminAPIView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = VillageSerializer

    def get_object(self):
        return Village.objects.first()


# -----------------------------
# Admin: Sections CRUD
# -----------------------------
class VillageSectionAdminAPIView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = VillageSectionSerializer
    queryset = VillageSection.objects.all().order_by("order", "id")

class VillageSectionDetailAdminAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = VillageSectionSerializer
    queryset = VillageSection.objects.all()


# -----------------------------
# Admin: Places CRUD (ผูกกับ section)
# -----------------------------
class VillagePlaceAdminAPIView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = VillagePlaceSerializer

    def get_queryset(self):
        section_id = self.kwargs.get("section_id")
        return VillagePlace.objects.filter(section_id=section_id).order_by("order", "id")

    def perform_create(self, serializer):
        section_id = self.kwargs.get("section_id")
        section = get_object_or_404(VillageSection, id=section_id)
        serializer.save(section=section)

class VillagePlaceDetailAdminAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = VillagePlaceSerializer
    queryset = VillagePlace.objects.all()


# -----------------------------
# Admin: Upload/Delete Images (B)
# -----------------------------
class VillageSectionImageDeleteAdminAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, pk):
        img = get_object_or_404(VillageSectionImage, pk=pk)
        img.caption = request.data.get("caption", img.caption)
        img.save(update_fields=["caption"])
        return Response({"id": img.id, "caption": img.caption})

    def delete(self, request, pk):
        img = get_object_or_404(VillageSectionImage, pk=pk)
        if img.image:
            img.image.delete(save=False)
        img.delete()
        return Response(status=204)

class VillageSectionImageUploadAdminAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser]

    def post(self, request, section_id):
        section = get_object_or_404(VillageSection, id=section_id)
        image = request.FILES.get("image")      # ← เปลี่ยนจาก getlist("images")
        if not image:
            return Response({"detail": "ไม่พบไฟล์"}, status=400)
        caption = request.data.get("caption", "")
        img = VillageSectionImage.objects.create(section=section, image=image, caption=caption)
        ser = VillageSectionImageSerializer(img, context={"request": request})
        return Response(ser.data, status=201)

class VillagePlaceImageUploadAdminAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser]

    def post(self, request, place_id):
        place = get_object_or_404(VillagePlace, id=place_id)
        files = request.FILES.getlist("images")
        if not files:
            return Response({"detail": "ไม่พบไฟล์"}, status=400)

        created = [VillagePlaceImage.objects.create(place=place, image=f) for f in files]
        ser = VillagePlaceImageSerializer(created, many=True, context={"request": request})
        return Response(ser.data, status=201)

class VillagePlaceImageDeleteAdminAPIView(generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = VillagePlaceImage.objects.all()

    def perform_destroy(self, instance):
        if instance.image:
            instance.image.delete(save=False)
        instance.delete()


# -----------------------------
# Admin: Profiles
# -----------------------------
class CommunityProfileAdminAPIView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CommunityProfileSerializer

    def get_queryset(self):
        village = Village.objects.first()
        return CommunityProfile.objects.filter(village=village).annotate(
            group_order=Case(
                When(group="leader", then=1),
                When(group="committee", then=2),
                When(group="volunteer", then=3),
                output_field=IntegerField()
            )
        ).order_by("group_order", "level")

    def perform_create(self, serializer):
        village = Village.objects.first()
        serializer.save(village=village)

class CommunityProfileDetailAdminAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CommunityProfileSerializer
    queryset = CommunityProfile.objects.all()


# -----------------------------
# Admin: Funds
# -----------------------------
class FundTypeAdminAPIView(generics.ListCreateAPIView):
    permission_classes = [IsAdminRole]
    serializer_class = FundTypeSerializer

    def get_queryset(self):
        village = Village.objects.first()
        return FundType.objects.filter(village=village)

    def perform_create(self, serializer):
        village = Village.objects.first()
        serializer.save(village=village)

class FundTypeDetailAdminAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminRole]
    serializer_class = FundTypeSerializer
    queryset = FundType.objects.all()

class FundRecordAdminAPIView(generics.ListCreateAPIView):
    permission_classes = [IsAdminRole]
    serializer_class = FundRecordSerializer

    def get_queryset(self):
        fund_id = self.kwargs["fund_id"]
        return FundRecord.objects.filter(fund_type_id=fund_id)

    def perform_create(self, serializer):
        fund_type = get_object_or_404(FundType, id=self.kwargs["fund_id"])
        serializer.save(fund_type=fund_type)


# -----------------------------
# Admin: Update Village Location (lat/lng)
# -----------------------------
class VillageLocationUpdateAPIView(APIView):
    permission_classes = [IsAdminRole]

    def patch(self, request):
        village = Village.objects.first()
        if not village:
            return Response({"detail": "ไม่พบข้อมูลหมู่บ้าน"}, status=404)

        lat = request.data.get("latitude")
        lng = request.data.get("longitude")

        if lat is None or lng is None:
            return Response({"detail": "กรุณาระบุ latitude และ longitude"}, status=400)

        try:
            village.latitude = float(lat)
            village.longitude = float(lng)
            village.save(update_fields=["latitude", "longitude", "updated_at"])
        except (ValueError, TypeError):
            return Response({"detail": "ค่าพิกัดไม่ถูกต้อง"}, status=400)

        return Response({"latitude": str(village.latitude), "longitude": str(village.longitude)})