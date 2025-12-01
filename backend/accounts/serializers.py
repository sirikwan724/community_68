from rest_framework import serializers
from .models import RegistrationRequest, User, News
from django.contrib.auth.hashers import make_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class RegistrationRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegistrationRequest
        fields = [
            "id",
            "full_name",
            "phone",
            "address",
            "citizen_id",
            "house_owner_name",
            "password",
            "status",
            "created_at",
        ]
        read_only_fields = ["id", "status", "created_at"]

    # ทำการ hash password ก่อนบันทึกลง DB
    def create(self, validated_data):
        raw_password = validated_data.get("password")
        validated_data["password"] = make_password(raw_password)
        return super().create(validated_data)
    
class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["full_name", "address", "phone", "house_owner_name"]

    def update(self, instance, validated_data):
        instance.full_name = validated_data.get("full_name", instance.full_name)
        instance.address = validated_data.get("address", instance.address)
        instance.phone = validated_data.get("phone", instance.phone)
        instance.house_owner_name = validated_data.get("house_owner_name", instance.house_owner_name)
        instance.save()
        return instance


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['role'] = user.role
        token['full_name'] = user.full_name
        return token

    def validate(self, attrs):
        data = super().validate(attrs)

        # ส่งข้อมูลเพิ่มให้ frontend
        data.update({
            "role": self.user.role,
            "user": {
                "id": self.user.id,
                "username": self.user.username,
                "full_name": self.user.full_name,
                "phone": self.user.phone,
                "address": self.user.address,
                "role": self.user.role,
            }
        })
        return data

class NewsSerializer(serializers.ModelSerializer):
    # แปลงวันที่เป็นรูปแบบที่อ่านง่าย (เช่น 18 ม.ค. 2568)
    created_at_formatted = serializers.DateTimeField(source='created_at', format="%d/%m/%Y %H:%M", read_only=True)
    
    class Meta:
        model = News
        fields = ['id', 'title', 'content', 'image', 'created_at', 'created_at_formatted', 'author']
        read_only_fields = ['author', 'created_at']
