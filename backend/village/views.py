import re
# from django.forms import IntegerField
from django.db.models import Case, When, IntegerField
from django.shortcuts import render
import pandas as pd
# Create your views here.
from decimal import Decimal
from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser

from .models import (
    Village,
    VillageHistory,
    VillagePlace,
    VillageExtraSection,
    CommunityProfile,
    FundType,
    FundRecord,
    FundLoan,
)

from .serializers import (
    VillageSerializer,
    VillageHistorySerializer,
    VillagePlaceSerializer,
    VillageExtraSectionSerializer,
    CommunityProfileSerializer,
    FundTypeSerializer,
    FundRecordSerializer,
    FundLoanSerializer,
)

def normalize(text):
    return re.sub(r"[ \-–_()/]", "", str(text)).lower().strip()

def find_header_row(df):
    required_keywords = ["ชื่อ", "บัญชี", "เงิน"]

    for i in range(len(df)):
        row = df.iloc[i]

        # เอาเฉพาะ cell ที่ไม่ใช่ NaN
        non_empty_cells = [str(cell) for cell in row if pd.notna(cell)]

        # ถ้ามี cell น้อยเกินไป แสดงว่าไม่น่าใช่ header
        if len(non_empty_cells) < 3:
            continue

        match_count = 0
        for cell in non_empty_cells:
            cell_clean = normalize(cell)

            for keyword in required_keywords:
                if cell_clean == normalize(keyword) or normalize(keyword) in cell_clean:
                    match_count += 1

        # ต้อง match อย่างน้อย 2 keyword
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

class FundLoanExcelImportAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser]

    def post(self, request, record_id):
        file = request.FILES.get("file")
        if not file:
            return Response({"detail": "ไม่พบไฟล์"}, status=400)

        fund_record = FundRecord.objects.get(id=record_id)

        df_raw = pd.read_excel(file, header=None)

        # หา header จริง
        header_row = find_header_row(df_raw)
        if header_row is None:
            return Response({"detail": "ไม่พบหัวตาราง"}, status=400)

        df = pd.read_excel(file, header=header_row) 
        df.columns = df.columns.str.strip()

        print(df.head(10))

        # print("Header Row Found:", header_row)
        print("Columns After Re-read:", df.columns)
        print("Detected Columns:", df.columns)

        COLUMN_MAP = {
            "full_name": ["ชื่อ"],
            "bank_account": ["บัญชี","เลขที่บัญชี"],
            "loan_amount": ["เงิน", "อนุมัติ","จำนวนเงิน"],
            "purpose": ["วัตถุประสงค์", "อาชีพ"],
        }

        col_fullname = find_column(df, COLUMN_MAP["full_name"])
        col_account = find_column(df, COLUMN_MAP["bank_account"])
        col_amount = find_column(df, COLUMN_MAP["loan_amount"])
        col_purpose = find_column(df, COLUMN_MAP["purpose"])

        if not all([col_fullname, col_account, col_amount]):
            return Response({"detail": "รูปแบบไฟล์ไม่ถูกต้อง"}, status=400)
        
        FundLoan.objects.filter(fund_record=fund_record).delete() #ลบข้อมูลเก่าออกก่อนนำเข้าใหม่

        created = 0
        skipped = 0

        for _, row in df.iterrows():
            try:
                raw_amount = str(row[col_amount]).replace(",", "").strip()

                if not raw_amount or not raw_amount.replace(".", "").isdigit():
                    skipped += 1
                    continue

                loan_amount = Decimal(raw_amount)
                interest = (
                    loan_amount * fund_record.interest_rate / Decimal(100)
                )

                FundLoan.objects.create(
                    fund_record=fund_record,
                    full_name=row[col_fullname] if col_fullname else "",
                    bank_account=str(row[col_account]) if col_account else "",
                    loan_amount=loan_amount,
                    interest_amount=interest,
                    purpose=row[col_purpose] if col_purpose else "",
                )

                created += 1

            except Exception as e:
                print("ข้ามแถว:", e)
                skipped += 1
                continue

        fund_record.last_uploaded_file = file.name
        fund_record.save()

        return Response({
            "message": f"นำเข้าข้อมูลสำเร็จ {created} รายการ",
            "skipped": skipped
        })

#รวม: ข้อมูลหมู่บ้านทั้งหมด
class VillageFullAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        village = Village.objects.first()
        if not village:
            return Response({"detail": "ไม่พบข้อมูลหมู่บ้าน"}, status=404)

        data = {
            "overview": VillageSerializer(village).data,
            "history": (
                VillageHistorySerializer(village.history).data
                if hasattr(village, "history")
                else None
            ),
            "places": VillagePlaceSerializer(
                village.places.order_by("order"),
                many=True
            ).data,
            "extra_sections": VillageExtraSectionSerializer(
                village.extra_sections.filter(is_active=True).order_by("order"),
                many=True
            ).data,
        }

        return Response(data)

#API โปรไฟล์ผู้นำ / กรรมการ / อสม.
class CommunityProfileListAPIView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = CommunityProfileSerializer

    def get_queryset(self):
        village = Village.objects.first()
        return CommunityProfile.objects.filter(
            village=village
        ).annotate(
            group_order=Case(
                When(group="leader", then=1),
                When(group="committee", then=2),
                When(group="volunteer", then=3),
                output_field=IntegerField()
            )
        ).order_by("group_order", "level")

#API รายการกองทุนที่มีให้เลือก
class FundTypeListAPIView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = FundTypeSerializer

    def get_queryset(self):
        village = Village.objects.first()
        return FundType.objects.filter(
            village=village,
            is_active=True
        )

#API กองทุนรายปี
class FundRecordListAPIView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = FundRecordSerializer

    def get_queryset(self):
        fund_id = self.kwargs["fund_id"]
        return FundRecord.objects.filter(
            fund_type_id=fund_id
        ).order_by("-year")

#รายชื่อผู้กู้ (ที่ซ่อนเลขบัญชีแล้ว)
class FundLoanListAPIView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = FundLoanSerializer

    def get_queryset(self):
        record_id = self.kwargs["record_id"]
        return FundLoan.objects.filter(
            fund_record_id=record_id
        )

#Admin API จัดการข้อมูล

#จัดการกับสถานที่สำคัญในหมู่บ้าน
class VillagePlaceAdminAPIView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = VillagePlaceSerializer

    def get_queryset(self):
        village = Village.objects.first()
        return VillagePlace.objects.filter(village=village)

    def perform_create(self, serializer):
        village = Village.objects.first()
        serializer.save(village=village)

#แก้ / ลบ สถานที่สำคัญในหมู่บ้าน
class VillagePlaceDetailAdminAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = VillagePlaceSerializer
    queryset = VillagePlace.objects.all()

#แก้ไข ข้อมูลหมู่บ้าน (Overview)
class VillageAdminAPIView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = VillageSerializer

    def get_object(self):
        return Village.objects.first()

#จัดการกับประวัติหมู่บ้าน
class VillageHistoryAdminAPIView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = VillageHistorySerializer

    def get_object(self):
        village = Village.objects.first()
        history, _ = VillageHistory.objects.get_or_create(village=village)
        return history

#จัดการกับข้อมูลเพิ่มเติม อาจจะมีการเพิ่มหรือลบข้อมูล
class VillageExtraSectionAdminAPIView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = VillageExtraSectionSerializer

    def get_queryset(self):
        village = Village.objects.first()
        return VillageExtraSection.objects.filter(village=village)

    def perform_create(self, serializer):
        village = Village.objects.first()
        serializer.save(village=village)

class VillageExtraSectionDetailAdminAPIView(
    generics.RetrieveUpdateDestroyAPIView
):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = VillageExtraSectionSerializer
    queryset = VillageExtraSection.objects.all()

#API โปรไฟล์ผู้นำ / กรรมการ / อสม ของแอดมิน
class CommunityProfileAdminAPIView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CommunityProfileSerializer

    def get_queryset(self):
        village = Village.objects.first()
        return CommunityProfile.objects.filter(
            village=village
        ).annotate(
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

class CommunityProfileDetailAdminAPIView(
    generics.RetrieveUpdateDestroyAPIView
):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CommunityProfileSerializer
    queryset = CommunityProfile.objects.all()

#Admin จัดการประเภทกองทุน
class FundTypeAdminAPIView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = FundTypeSerializer

    def get_queryset(self):
        village = Village.objects.first()
        return FundType.objects.filter(village=village)

    def perform_create(self, serializer):
        village = Village.objects.first()
        serializer.save(village=village)

#Admin แก้ / ลบ กองทุน
class FundTypeDetailAdminAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = FundTypeSerializer
    queryset = FundType.objects.all()

#Admin จัดการ กองทุนรายปี  ดอกเบี้ย
class FundRecordAdminAPIView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = FundRecordSerializer

    def get_queryset(self):
        fund_id = self.kwargs["fund_id"]
        return FundRecord.objects.filter(fund_type_id=fund_id)

    def perform_create(self, serializer):
        fund_type = FundType.objects.get(id=self.kwargs["fund_id"])
        serializer.save(fund_type=fund_type)

