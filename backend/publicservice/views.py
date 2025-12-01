from rest_framework import generics
from .models import PublicService
from .serializers import PublicServiceSerializer


class PublicServiceListCreateView(generics.ListCreateAPIView):
    queryset = PublicService.objects.all()
    serializer_class = PublicServiceSerializer


class PublicServiceDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = PublicService.objects.all()
    serializer_class = PublicServiceSerializer
