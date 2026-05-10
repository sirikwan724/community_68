from rest_framework import serializers
from django.db import transaction
from .models import Item, BorrowItem, BorrowRequest, Location
from django.utils import timezone

# =========================
# MASTER DATA
# =========================

class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = "__all__"


class LocationSerializer(serializers.ModelSerializer):
    is_available = serializers.SerializerMethodField()

    class Meta:
        model = Location
        fields = ["id", "name", "is_available"]

    def get_is_available(self, obj):
        request = self.context.get("request")
        if not request:
            return True

        start = request.query_params.get("start_datetime")
        end = request.query_params.get("end_datetime")

        if not start or not end:
            return True  # ยังไม่เลือกวันเวลา ถือว่าว่าง

        conflict = BorrowRequest.objects.filter(
            borrow_type="LOCATION",
            location=obj,
            status__in=["approved", "borrowed"],
            start_datetime__lt=end,
            end_datetime__gt=start,
        ).exists()

        return not conflict

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
    items = BorrowItemSerializer(many=True, required=False)

    class Meta:
        model = BorrowRequest
        fields = "__all__"
        read_only_fields = [
            "user",
            "status",
            "borrower_name",
            "borrower_phone",]

    def validate(self, attrs):
        borrow_type = attrs.get("borrow_type")
        start = attrs.get("start_datetime")
        end = attrs.get("end_datetime")
        location = attrs.get("location")

        if start and start < timezone.now():
            raise serializers.ValidationError(
                {"start_datetime": "ไม่สามารถเลือกวันเวลาที่ผ่านมาแล้วได้"}
            )

        if start and end and end <= start:
            raise serializers.ValidationError(
                {"end_datetime": "วันเวลาสิ้นสุดต้องมาหลังวันเวลาเริ่มต้น"}
            )

        # ---- เช็กจองสถานที่ซ้อน ----
        if borrow_type == "LOCATION":
            conflict = BorrowRequest.objects.filter(
                borrow_type="LOCATION",
                location=location,
                status__in=["approved", "borrowed"],
                start_datetime__lt=end,
                end_datetime__gt=start,
            ).exists()

            if conflict:
                raise serializers.ValidationError(
                    {"location": "สถานที่นี้ถูกใช้งานในช่วงเวลาดังกล่าวแล้ว"}
                )

        return attrs
    
    def create(self, validated_data):
        request = self.context["request"]
        items_data = validated_data.pop("items", [])
        validated_data.pop("user", None)
        with transaction.atomic():
            borrow = BorrowRequest.objects.create(
                user=self.context["request"].user,
                borrower_name=self.context["request"].user.full_name,
                borrower_phone=self.context["request"].user.phone,
                **validated_data
            )

            if borrow.borrow_type == "ITEM":
                for item_data in items_data:
                    if item_data["quantity"] > item_data["item"].stock:
                        raise serializers.ValidationError(
                            f"{item_data['item'].name} มีจำนวนไม่เพียงพอ"
                        )
                    # เช็กสต๊อก
                for item_data in items_data:
                    BorrowItem.objects.create(
                        borrow_request=borrow,
                        item=item_data["item"],
                        quantity=item_data["quantity"],
                    )
            return borrow

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
