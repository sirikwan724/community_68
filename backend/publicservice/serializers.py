from rest_framework import serializers
from .models import PublicService

class PublicServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = PublicService
        fields = '__all__'
