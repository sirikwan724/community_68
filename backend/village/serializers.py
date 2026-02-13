from rest_framework import serializers
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

#ข้อมูลหมู่บ้าน (Overview)
class VillageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Village
        fields = [
            "id",
            "name",
            "description",
            "address",
            "updated_at",
        ]

#ประวัติหมู่บ้าน
class VillageHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = VillageHistory
        fields = [
            "id",
            "content",
            "image",
            "updated_at",
        ]

#สถานที่สาธารณะ
class VillagePlaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = VillagePlace
        fields = [
            "id",
            "name",
            "description",
            "image",
            "order",
        ]

#ข้อมูลเพิ่มเติม
class VillageExtraSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = VillageExtraSection
        fields = [
            "id",
            "title",
            "content",
            "image",
            "order",
            "is_active",
        ]

#โปรไฟล์ผู้นำ / กรรมการ / อสม.
class CommunityProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommunityProfile
        fields = "__all__"
        read_only_fields = ["village"]

    def validate(self, data):
        # -------- ดึง village ให้ถูกต้อง --------
        if self.instance:
            village = self.instance.village
        else:
            from .models import Village
            village = Village.objects.first()

        group = data.get("group")
        level = data.get("level")

        # -------- เช็คว่าซ้ำไหม --------
        queryset = CommunityProfile.objects.filter(
            village=village,
            group=group,
            level=level
        )

        # ถ้าเป็น edit ต้องตัดตัวเองออก
        if self.instance:
            queryset = queryset.exclude(id=self.instance.id)

        # -------- เงื่อนไขจำกัดจำนวน --------
        if level == 1 and queryset.count() >= 1:
            raise serializers.ValidationError(
                "ในแต่ละกลุ่มมีตำแหน่งหลักได้เพียง 1 คน"
            )

        if level == 2 and queryset.count() >= 3:
            raise serializers.ValidationError(
                "ในแต่ละกลุ่มมีรองได้ไม่เกิน 3 คน"
            )

        return data

#ประเภทกองทุน
class FundTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = FundType
        fields = [
            "id",
            "name",
            "description",
            "is_active",
        ]

#ข้อมูลกองทุนรายปี
class FundRecordSerializer(serializers.ModelSerializer):
    fund_name = serializers.CharField(
        source="fund_type.name",
        read_only=True
    )

    class Meta:
        model = FundRecord
        fields = [
            "id",
            "fund_type",
            "fund_name",
            "year",
            "interest_rate",
            "created_at",
            "updated_at",
            "last_uploaded_file",
        ]

#รายชื่อผู้กู้ (เลขบัญชี ยอดที่กู้ ดอกเบี้ย)
class FundLoanSerializer(serializers.ModelSerializer):
    masked_account = serializers.SerializerMethodField()

    class Meta:
        model = FundLoan
        fields = [
            "id",
            "full_name",
            "masked_account",
            "loan_amount",
            "interest_amount",
            "purpose",
            "created_at",
        ]

    def get_masked_account(self, obj):
        return obj.masked_account()

class FundLoanImportSerializer(serializers.Serializer):
    full_name = serializers.CharField()
    bank_account = serializers.CharField()
    loan_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    purpose = serializers.CharField(required=False, allow_blank=True)
