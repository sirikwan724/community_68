from django.shortcuts import get_object_or_404
from django.db import transaction
from django.db.models import Q

from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import BorrowRequest, Item, Location
from .serializers import BorrowRequestReadSerializer, BorrowRequestSerializer, ItemSerializer, LocationSerializer
from .permissions import IsAdmin


# ===============================
# USER VIEWS
# ===============================

class CreateBorrowRequestView(generics.CreateAPIView):
    """
    ผู้ใช้งานสร้างคำขอยืม
    - ดึงชื่อ + เบอร์จากบัญชีอัตโนมัติ (ทำใน serializer)
    """
    serializer_class = BorrowRequestSerializer
    permission_classes = [permissions.IsAuthenticated]


class MyBorrowRequestListView(generics.ListAPIView):
    """
    ผู้ใช้งานดูคำขอยืมของตัวเอง
    """
    serializer_class = BorrowRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return BorrowRequest.objects.filter(
            user=self.request.user
        ).order_by('-created_at')


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


# ===============================
# ADMIN VIEWS
# ===============================

class AdminBorrowRequestListView(generics.ListAPIView):
    """
    แอดมินดูคำขอยืมทั้งหมด
    """
    serializer_class = BorrowRequestSerializer
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
    queryset = Item.objects.filter(is_active=True)
    serializer_class = ItemSerializer
    permission_classes = [permissions.AllowAny]  

    def get_queryset(self):
        return Item.objects.filter(is_active=True)


class LocationListView(generics.ListAPIView):
    serializer_class = LocationSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return Location.objects.filter(is_active=True)

class MyBorrowRequestListView(generics.ListAPIView):
    serializer_class = BorrowRequestReadSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return BorrowRequest.objects.filter(
            user=self.request.user
        ).prefetch_related("items__item")
