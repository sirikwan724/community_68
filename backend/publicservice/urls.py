from django.urls import path
from .views import (
    PublicServiceListCreateView,
    PublicServiceDetailView
)

urlpatterns = [
    path("", PublicServiceListCreateView.as_view()),      # GET, POST
    path("<int:pk>/", PublicServiceDetailView.as_view()), # GET, PUT, DELETE
]
