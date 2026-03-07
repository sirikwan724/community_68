from rest_framework import generics, permissions, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils.timezone import make_aware
from datetime import datetime
from django.db import transaction
from .models import PublicService, PublicServiceReport
from .serializers import PublicServiceSerializer, PublicServiceReportSerializer

# -------------------------
# Public Services
# -------------------------
class PublicServiceListCreateView(generics.ListCreateAPIView):
    queryset = PublicService.objects.all()
    serializer_class = PublicServiceSerializer


class PublicServiceDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = PublicService.objects.all()
    serializer_class = PublicServiceSerializer


# -------------------------
# Service Reports (User)
# -------------------------
class PublicServiceReportCreateView(generics.CreateAPIView):
    serializer_class = PublicServiceReportSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# เอาไปแสดงในหน้า MyHistory
class MyPublicServiceReportsView(generics.ListAPIView):
    serializer_class = PublicServiceReportSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return PublicServiceReport.objects.filter(user=self.request.user).order_by("-created_at")


# รายละเอียดรายงานของฉัน (GET) + แก้ไข (PUT/PATCH)
class MyPublicServiceReportDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = PublicServiceReportSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        return PublicServiceReport.objects.filter(user=self.request.user)

    def perform_update(self, serializer):
        report = self.get_object()
        if report.status != "pending":
            raise PermissionDenied("รายงานนี้ถูกรับเรื่องแล้ว ไม่สามารถแก้ไขได้")
        serializer.save()


# ยกเลิกรายงานของฉัน (PATCH)
class CancelMyPublicServiceReportView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, pk):
        try:
            report = PublicServiceReport.objects.get(pk=pk, user=request.user)
        except PublicServiceReport.DoesNotExist:
            return Response({"detail": "ไม่พบรายงานนี้"}, status=status.HTTP_404_NOT_FOUND)

        if report.status != "pending":
            return Response(
                {"detail": "ไม่สามารถยกเลิกรายงานที่ถูกรับเรื่องแล้ว"},
                status=status.HTTP_400_BAD_REQUEST
            )

        report.status = "canceled"
        report.save()
        return Response({"detail": "ยกเลิกรายงานสำเร็จ"})


# -------------------------
# Service Reports (Admin)
# -------------------------
class AdminPublicServiceReportsView(generics.ListAPIView):
    serializer_class = PublicServiceReportSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = (
            PublicServiceReport.objects.select_related("service", "user", "user__profile")
            .all()
            .order_by("-created_at")
        )

        # ---- filters ----
        service_id = self.request.query_params.get("service")   # service id
        st = self.request.query_params.get("status")           # pending/processing/resolved/canceled
        category = self.request.query_params.get("category")   # water/washer
        month = self.request.query_params.get("month")         # "01".."12"
        year = self.request.query_params.get("year")           # "2026"

        if service_id:
            qs = qs.filter(service_id=service_id)

        if st:
            qs = qs.filter(status=st)

        if category:
            qs = qs.filter(service__category=category)

        # filter ตามเดือน/ปีจาก created_at
        # ใช้วิธี __month / __year ได้เลย (ง่ายและเร็ว)
        if month and month.isdigit():
            qs = qs.filter(created_at__month=int(month))

        if year and year.isdigit():
            qs = qs.filter(created_at__year=int(year))

        return qs

class AdminUpdatePublicServiceReportStatusView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, pk):
        try:
            report = PublicServiceReport.objects.select_related("service").get(pk=pk)
        except PublicServiceReport.DoesNotExist:
            return Response({"detail": "ไม่พบรายงานนี้"}, status=status.HTTP_404_NOT_FOUND)

        # ล็อก: ถ้าปิดงานแล้ว ห้ามแก้
        if report.status in ["resolved", "canceled"]:
            return Response(
                {"detail": "รายงานนี้ปิดงานแล้ว ไม่สามารถเปลี่ยนสถานะได้"},
                status=status.HTTP_400_BAD_REQUEST
            )

        new_status = request.data.get("status")
        allowed = ["pending", "processing", "resolved", "canceled"]
        if new_status not in allowed:
            return Response({"detail": "invalid status"}, status=status.HTTP_400_BAD_REQUEST)

        service = report.service

        with transaction.atomic():
            report.status = new_status
            report.save(update_fields=["status"])

            # sync สถานะตู้ + กันหลายรายงาน
            if new_status == "processing":
                if service.status != "maintenance":
                    service.status = "maintenance"
                    service.save(update_fields=["status"])

            elif new_status == "resolved":
                # ถ้ายังมีรายงานอื่นค้างอยู่ (pending/processing) -> ยัง maintenance
                has_open_reports = PublicServiceReport.objects.filter(
                    service=service
                ).exclude(
                    status__in=["resolved", "canceled"]
                ).exists()

                if has_open_reports:
                    if service.status != "maintenance":
                        service.status = "maintenance"
                        service.save(update_fields=["status"])
                else:
                    if service.status != "normal":
                        service.status = "normal"
                        service.save(update_fields=["status"])

            elif new_status == "canceled":
                # รายงานไม่ถูกต้อง -> ไม่แตะสถานะตู้
                pass

        return Response(PublicServiceReportSerializer(report).data)