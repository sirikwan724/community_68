from rest_framework import serializers
from .models import Item, BorrowItem, BorrowRequest, Location


# =========================
# MASTER DATA
# =========================

class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = "__all__"


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = "__all__"


# =========================
# BORROW ITEM (ย่อย)
# =========================

class BorrowItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = BorrowItem
        fields = ["item", "quantity"]

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "จำนวนที่ยืมต้องมากกว่า 0"
            )
        return value


# =========================
# BORROW REQUEST (ตัวหลัก)
# =========================

class BorrowRequestSerializer(serializers.ModelSerializer):
    items = BorrowItemSerializer(many=True)
    borrower_name = serializers.CharField(read_only=True)
    borrower_phone = serializers.CharField(read_only=True)

    class Meta:
        model = BorrowRequest
        fields = [
            "id",
            "borrow_type",
            "location",
            "items",
            "start_datetime",
            "end_datetime",
            "pickup_datetime",
            "expected_return_datetime",
            "purpose",
            "status",
            "borrower_name",
            "borrower_phone",
            "created_at",
        ]

    def validate(self, attrs):
        borrow_type = attrs.get("borrow_type")
        items = attrs.get("items", [])

        # ---- ตรวจวันเวลา ----
        start = attrs.get("start_datetime")
        end = attrs.get("end_datetime")

        if start and end and start >= end:
            raise serializers.ValidationError(
                "วันเวลาเริ่มต้องน้อยกว่าวันเวลาสิ้นสุด"
            )

        # ---- กรณียืมสิ่งของ ----
        if borrow_type == "ITEM" and not items:
            raise serializers.ValidationError(
                "กรุณาเลือกสิ่งของอย่างน้อย 1 รายการ"
            )

        # ---- กรณียืมสถานที่ ----
        if borrow_type == "LOCATION" and not attrs.get("location"):
            raise serializers.ValidationError(
                "กรุณาเลือกสถานที่"
            )

        return attrs

    def create(self, validated_data):
        request = self.context["request"]
        user = request.user

        profile = getattr(user, "profile", None)
        if not profile:
            raise serializers.ValidationError(
                "ไม่พบข้อมูลโปรไฟล์ผู้ใช้งาน"
            )

        items_data = validated_data.pop("items")

        borrow_request = BorrowRequest.objects.create(
            user=user,
            borrower_name=profile.full_name,
            borrower_phone=profile.phone_number,
            **validated_data
        )

        for item_data in items_data:
            BorrowItem.objects.create(
                borrow_request=borrow_request,
                item=item_data["item"],
                quantity=item_data["quantity"]
            )

        return borrow_request

class BorrowItemReadSerializer(serializers.ModelSerializer):
    item_name = serializers.CharField(source="item.name")
    unit = serializers.CharField(source="item.unit")

    class Meta:
        model = BorrowItem
        fields = ["item_name", "unit", "quantity"]

class BorrowRequestReadSerializer(serializers.ModelSerializer):
    items = BorrowItemReadSerializer(many=True, read_only=True)
    location_name = serializers.CharField(
        source="location.name",
        read_only=True
    )

    class Meta:
        model = BorrowRequest
        fields = [
            "id",
            "borrow_type",
            "status",
            "borrower_name",            
            "borrower_phone",
            "items",
            "location_name",
            "start_datetime",
            "end_datetime",
            "pickup_datetime",              
            "expected_return_datetime",    
            "purpose",                      
            "created_at",
        ]
