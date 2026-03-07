from rest_framework import serializers
from .models import RegistrationRequest, User, News
from django.contrib.auth.hashers import make_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class RegistrationRequestSerializer(serializers.ModelSerializer):
    created_at_formatted = serializers.DateTimeField(
        source="created_at",
        format="%d/%m/%Y",
        read_only=True
    )
    class Meta:
        model = RegistrationRequest
        fields = [
            "id",
            "username",         
            "full_name",
            "phone",
            "address",
            "citizen_id",        
            "house_owner_name",
            "password",
            "status",
            "created_at",
            "created_at_formatted",
        ]
        read_only_fields = ["id", "status", "created_at"]

    def validate_username(self, value):
        """
        ป้องกัน username ซ้ำกับ User ที่มีอยู่แล้ว
        """
        from django.contrib.auth import get_user_model
        User = get_user_model()

        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("ชื่อผู้ใช้งานนี้ถูกใช้แล้ว")

        return value

    # hash password ก่อนบันทึก
    def create(self, validated_data):
        raw_password = validated_data.get("password")
        validated_data["password"] = make_password(raw_password)
        return super().create(validated_data)
    
class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["full_name", "address", "phone", "house_owner_name", "citizen_id"]

    def update(self, instance, validated_data):
        instance.full_name = validated_data.get("full_name", instance.full_name)
        instance.address = validated_data.get("address", instance.address)
        instance.phone = validated_data.get("phone", instance.phone)
        instance.house_owner_name = validated_data.get("house_owner_name", instance.house_owner_name)
        instance.citizen_id = validated_data.get("citizen_id", instance.citizen_id)
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
                "citizen_id": self.user.citizen_id,
                "house_owner_name": self.user.house_owner_name,
                "role": self.user.role,
            }
        })
        return data

class NewsSerializer(serializers.ModelSerializer):
    # แปลงวันที่เป็นรูปแบบที่อ่านง่าย (เช่น 18 ม.ค. 2568)
    created_at_formatted = serializers.DateTimeField(source='created_at', format="%d/%m/%Y", read_only=True)
    
    class Meta:
        model = News
        fields = ['id', 'title', 'content', 'image', 'created_at', 'created_at_formatted', 'author']
        read_only_fields = ['author', 'created_at']
