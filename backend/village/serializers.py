from rest_framework import serializers
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

# ---------------------------
# Image serializers
# ---------------------------
class VillageSectionImageSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = VillageSectionImage
        fields = ["id", "url", "caption", "order"]

    def get_url(self, obj):
        req = self.context.get("request")
        return req.build_absolute_uri(obj.image.url) if req else obj.image.url


class VillagePlaceImageSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = VillagePlaceImage
        fields = ["id", "url", "caption", "order"]

    def get_url(self, obj):
        req = self.context.get("request")
        return req.build_absolute_uri(obj.image.url) if req else obj.image.url


# ---------------------------
# Village serializers
# ---------------------------
class VillageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Village
        # ============================================================
        # [เพิ่มใหม่] เพิ่ม "latitude" และ "longitude" เข้า fields
        # ============================================================
        # ก่อนหน้าคือ: fields = ["id", "name", "description", "address", "updated_at"]
        # ตอนนี้เพิ่มอีก 2 field ท้ายสุด
        # ผลลัพธ์ที่ Frontend จะได้รับ (JSON):
        # {
        #   "id": 1,
        #   "name": "บ้านสร้างขุนศรี",
        #   "description": "...",
        #   "address": "...",
        #   "updated_at": "2026-04-30T...",
        #   "latitude": "15.228700",   <-- ใหม่
        #   "longitude": "104.856100"  <-- ใหม่
        # }
        fields = ["id", "name", "description", "address", "updated_at", "latitude", "longitude"]


class VillagePlaceSerializer(serializers.ModelSerializer):
    images = VillagePlaceImageSerializer(many=True, read_only=True)

    class Meta:
        model = VillagePlace
        fields = ["id", "section", "name", "detail", "order", "images"]
        read_only_fields = ["section"]


class VillageSectionSerializer(serializers.ModelSerializer):
    images = VillageSectionImageSerializer(many=True, read_only=True)
    places = VillagePlaceSerializer(many=True, read_only=True)

    class Meta:
        model = VillageSection
        fields = ["id", "type", "title", "content", "description", "order", "images", "places"]


# ---------------------------
# Community / Fund serializers
# ---------------------------
class CommunityProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommunityProfile
        fields = "__all__"
        read_only_fields = ["village"]

    def validate(self, data):
        from .models import POSITION_CONFIG

        village = self.instance.village if self.instance else Village.objects.first()
        group = data.get("group", getattr(self.instance, "group", None))
        position = data.get("position", getattr(self.instance, "position", None))

        group_positions = POSITION_CONFIG.get(group, [])
        for pos_config in group_positions:
            if position == pos_config["name"] and pos_config["max"] is not None:
                queryset = CommunityProfile.objects.filter(
                    village=village, group=group, position=position
                )
                if self.instance:
                    queryset = queryset.exclude(id=self.instance.id)
                if queryset.count() >= pos_config["max"]:
                    raise serializers.ValidationError(
                        f"ตำแหน่ง {position} มีได้ไม่เกิน {pos_config['max']} คน"
                    )
        return data


class FundTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model  = FundType
        fields = ["id", "name", "description", "is_active"]


class FundRecordSerializer(serializers.ModelSerializer):
    fund_name = serializers.CharField(source="fund_type.name", read_only=True)

    class Meta:
        model  = FundRecord
        fields = [
            "id", "fund_type", "fund_name", "year",
            "interest_rate", "created_at", "updated_at", "last_uploaded_file",
        ]


class FundLoanSerializer(serializers.ModelSerializer):
    masked_account = serializers.SerializerMethodField()

    class Meta:
        model  = FundLoan
        fields = ["id", "full_name", "masked_account", "loan_amount", "interest_amount", "purpose", "created_at"]

    def get_masked_account(self, obj):
        return obj.masked_account()


class FundLoanImportSerializer(serializers.Serializer):
    full_name    = serializers.CharField()
    bank_account = serializers.CharField()
    loan_amount  = serializers.DecimalField(max_digits=12, decimal_places=2)
    purpose      = serializers.CharField(required=False, allow_blank=True)