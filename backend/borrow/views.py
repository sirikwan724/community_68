from django.shortcuts import get_object_or_404
from django.db import transaction
from django.db.models import Q, Count, Sum

from publicservice.serializers import serializers
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes

from .models import BorrowRequest, Item, Location
from .serializers import BorrowRequestReadSerializer, BorrowRequestSerializer, ItemSerializer, LocationSerializer
from .permissions import IsAdmin

# ===============================
# USER VIEWS
# ===============================

class CreateBorrowRequestView(generics.CreateAPIView):
    serializer_class = BorrowRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        borrow = serializer.save(user=self.request.user)

        # ---- กรณีจองสถานที่ ----
        if borrow.borrow_type == 'LOCATION':
            conflict = BorrowRequest.objects.filter(
                borrow_type='LOCATION',
                location=borrow.location,
                status__in=['approved', 'borrowed'],
                start_datetime__lt=borrow.end_datetime,
                end_datetime__gt=borrow.start_datetime,
            ).exists()

            if conflict:
                raise serializers.ValidationError(
                    "สถานที่นี้ถูกใช้งานในช่วงเวลาดังกล่าวแล้ว"
                )

        # ---- กรณียืมสิ่งของ ----
        if borrow.borrow_type == 'ITEM':
            for bi in borrow.items.select_related('item').all():
                if bi.quantity > bi.item.stock:
                    raise serializers.ValidationError(
                        f"{bi.item.name} มีจำนวนไม่เพียงพอ"
                    )

class RequestReturnView(APIView):
    """
    ผู้ใช้งานกดแจ้งคืนของ
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        borrow = get_object_or_404(
            BorrowRequest,
            pk=pk,
            user=request.user
        )

        if borrow.status != 'approved':
            return Response(
                {"error": "ยังไม่สามารถแจ้งคืนรายการนี้ได้"},
                status=status.HTTP_400_BAD_REQUEST
            )

        borrow.status = 'return_requested'
        borrow.save()

        return Response(
            {"message": "แจ้งคืนเรียบร้อย รอแอดมินตรวจสอบ"},
            status=status.HTTP_200_OK
        )

@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def cancel_borrow_request(request, pk):
    borrow = get_object_or_404(
        BorrowRequest,
        pk=pk,
        user=request.user
    )

    # ยกเลิกได้เฉพาะสถานะ pending
    if borrow.status != "pending":
        return Response(
            {"error": "ไม่สามารถยกเลิกรายการนี้ได้"},
            status=status.HTTP_400_BAD_REQUEST
        )

    borrow.status = "cancelled"
    borrow.save()

    return Response(
        {"message": "ยกเลิกคำขอเรียบร้อย"},
        status=status.HTTP_200_OK
    )

# ===============================
# ADMIN VIEWS
# ===============================

class AdminBorrowRequestListView(generics.ListAPIView):
    """
    แอดมินดูคำขอยืมทั้งหมด
    """
    serializer_class = BorrowRequestSerializer
    serializer_class = BorrowRequestReadSerializer
    permission_classes = [IsAdmin]

    def get_queryset(self):
        return BorrowRequest.objects.all().order_by('-created_at')


def is_location_time_conflict(borrow_request):
    """
    ตรวจสอบว่าสถานที่เดียวกัน มีการจองซ้อนเวลาหรือไม่
    """
    return BorrowRequest.objects.filter(
        borrow_type='LOCATION',
        location=borrow_request.location,
        status__in=['approved', 'borrowed'],
        start_datetime__lt=borrow_request.end_datetime,
        end_datetime__gt=borrow_request.start_datetime,
    ).exclude(pk=borrow_request.pk).exists()


class AdminApproveBorrowView(APIView):
    """
    แอดมินอนุมัติคำขอยืม
    - สิ่งของ → หักสต๊อก
    - สถานที่ → เช็กเวลาซ้อน
    """
    permission_classes = [IsAdmin]

    def post(self, request, pk):
        borrow = get_object_or_404(BorrowRequest, pk=pk)

        if borrow.status != 'pending':
            return Response(
                {"error": "สถานะไม่ถูกต้อง ไม่สามารถอนุมัติได้"},
                status=status.HTTP_400_BAD_REQUEST
            )

        with transaction.atomic():

            # ---- กรณียืมสถานที่ ----
            if borrow.borrow_type == 'LOCATION':
                if is_location_time_conflict(borrow):
                    return Response(
                        {"error": "ช่วงเวลานี้มีการจองสถานที่แล้ว"},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            # ---- กรณียืมสิ่งของ ----
            if borrow.borrow_type == 'ITEM':
                # ตรวจสต๊อกก่อน
                for bi in borrow.items.select_related('item').all():
                    if bi.quantity > bi.item.stock:
                        return Response(
                            {"error": f"{bi.item.name} ในสต๊อกไม่พอ"},
                            status=status.HTTP_400_BAD_REQUEST
                        )

                # หักสต๊อกจริง
                for bi in borrow.items.select_related('item').all():
                    item = bi.item
                    item.stock -= bi.quantity
                    item.save()

            borrow.status = 'approved'
            borrow.save()

        return Response(
            {"message": "อนุมัติคำขอยืมเรียบร้อย"},
            status=status.HTTP_200_OK
        )


class AdminRejectBorrowView(APIView):
    """
    แอดมินปฏิเสธคำขอยืม
    """
    permission_classes = [IsAdmin]

    def post(self, request, pk):
        borrow = get_object_or_404(BorrowRequest, pk=pk)

        if borrow.status != 'pending':
            return Response(
                {"error": "ไม่สามารถปฏิเสธคำขอนี้ได้"},
                status=status.HTTP_400_BAD_REQUEST
            )

        borrow.status = 'rejected'
        borrow.save()

        return Response(
            {"message": "ปฏิเสธคำขอเรียบร้อย"},
            status=status.HTTP_200_OK
        )


class AdminConfirmReturnView(APIView):
    """
    แอดมินยืนยันการคืนของ
    - เพิ่มสต๊อกกลับ
    """
    permission_classes = [IsAdmin]

    def post(self, request, pk):
        borrow = get_object_or_404(BorrowRequest, pk=pk)

        if borrow.status != 'return_requested':
            return Response(
                {"error": "ยังไม่มีการแจ้งคืนจากผู้ใช้งาน"},
                status=status.HTTP_400_BAD_REQUEST
            )

        with transaction.atomic():

            if borrow.borrow_type == 'ITEM':
                for bi in borrow.items.select_related('item').all():
                    item = bi.item
                    item.stock += bi.quantity
                    item.save()

            borrow.status = 'returned'
            borrow.save()

        return Response(
            {"message": "ยืนยันการคืนเรียบร้อย"},
            status=status.HTTP_200_OK
        )

# ===============================
# MASTER DATA (ITEM / LOCATION)
# ===============================

class ItemListView(generics.ListAPIView):
    serializer_class = ItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Item.objects.filter(
            is_active=True,
            stock__gt=0
        )

class LocationListView(generics.ListAPIView):
    serializer_class = LocationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Location.objects.filter(is_active=True)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

class MyBorrowRequestListView(generics.ListAPIView):
    serializer_class = BorrowRequestReadSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return BorrowRequest.objects.filter(
            user=self.request.user
        ).prefetch_related("items__item")

# ===============================
# ADMIN STATS
# ===============================
class AdminBorrowItemStatsView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        SUCCESS_STATUSES = ['approved', 'return_requested', 'returned', 'borrowed']
        year = request.GET.get("year")

        qs = BorrowRequest.objects.filter(
            borrow_type='ITEM',
            status__in=SUCCESS_STATUSES
        )

        if year:
            qs = qs.filter(created_at__year=year)

        data = (
            qs.values('items__item__name')
            .annotate(total=Sum('items__quantity'))
        )

        result = {
            row['items__item__name']: row['total']
            for row in data
            if row['items__item__name']
        }

        return Response(result)

class AdminBorrowLocationStatsView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        year = request.GET.get("year")

        qs = BorrowRequest.objects.filter(
            borrow_type='LOCATION',
            status='approved'
        )

        if year:
            qs = qs.filter(created_at__year=year)

        data = (
            qs.values('location__name')
            .annotate(total=Count('id'))
        )

        result = {
            row['location__name']: row['total']
            for row in data
            if row['location__name']
        }

        return Response(result)

class AdminBorrowSummaryStatsView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        SUCCESS_STATUSES = ['approved', 'return_requested', 'returned', 'borrowed']
        year = request.GET.get("year")

        qs = BorrowRequest.objects.filter(status__in=SUCCESS_STATUSES)

        if year:
            qs = qs.filter(created_at__year=year)

        result = qs.aggregate(
            success_total=Count('id'),
            success_item=Count('id', filter=Q(borrow_type='ITEM')),
            success_location=Count('id', filter=Q(borrow_type='LOCATION')),
        )

        return Response(result)

