from rest_framework import serializers
from .models import PublicService, PublicServiceReport


class PublicServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = PublicService
        fields = "__all__"


class PublicServiceReportSerializer(serializers.ModelSerializer):
    service_name = serializers.CharField(source="service.name", read_only=True)
    service_id = serializers.IntegerField(source="service.id", read_only=True)
    service_location = serializers.CharField(source="service.location", read_only=True)
    service_category = serializers.CharField(source="service.category", read_only=True)

    user_id = serializers.IntegerField(source="user.id", read_only=True)
    user_full_name = serializers.SerializerMethodField()
    user_phone = serializers.SerializerMethodField()

    class Meta:
        model = PublicServiceReport
        fields = [
            "id",
            "service",
            "service_id",
            "service_name",
            "service_location",
            "service_category",
            "user_id",
            "user_full_name",
            "user_phone",
            "title",
            "description",
            "image",
            "status",
            "created_at",
        ]
        read_only_fields = ["status", "created_at"]

    def get_user_full_name(self, obj):
        u = obj.user
        # 1) ถ้าเป็น CustomUser ที่มี first_name/last_name ใช้ get_full_name()
        if hasattr(u, "get_full_name"):
            name = (u.get_full_name() or "").strip()
            if name:
                return name

        # 2) ถ้ามี profile.full_name
        p = getattr(u, "profile", None)
        if p:
            for attr in ["full_name", "fullname", "name"]:
                if hasattr(p, attr):
                    val = (getattr(p, attr) or "").strip()
                    if val:
                        return val

        # 3) fallback: username/email
        return getattr(u, "username", None) or getattr(u, "email", "") or "-"

    def get_user_phone(self, obj):
        u = obj.user
        p = getattr(u, "profile", None)
        if p:
            for attr in ["phone", "phone_number", "tel", "mobile", "phoneNo"]:
                if hasattr(p, attr):
                    val = (getattr(p, attr) or "").strip()
                    if val:
                        return val
        return ""