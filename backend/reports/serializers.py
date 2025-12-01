from rest_framework import serializers
from .models import Report, ReportNote, RequestHelp

# --------------------------
# 1) Serializer สำหรับ Note
# --------------------------
class ReportNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportNote
        fields = ["id", "text", "created_at"]


# --------------------------
# 2) Serializer สำหรับ Report
# --------------------------
class ReportSerializer(serializers.ModelSerializer):
    user_data = serializers.SerializerMethodField()

    class Meta:
        model = Report
        fields = "__all__"

    def get_user_data(self, obj):
        user = getattr(obj, "user", None)
        if not user:
            return None

        return {
            "id": user.id,
            "full_name": user.full_name,
            "phone": user.phone,
            "address": user.address,
            "avatar": user.avatar.url if getattr(user, "avatar", None) else None,
        }


class RequestHelpSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequestHelp
        fields = "__all__"
        read_only_fields = ["user", "created_at"]

