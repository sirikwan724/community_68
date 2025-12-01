from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from rest_framework_simplejwt.views import TokenRefreshView
from .views import headman_status, update_headman_status

# 1. สร้าง Router สำหรับ News
router = DefaultRouter()
router.register(r'news', views.NewsViewSet)

urlpatterns = [
    # URL ของ Router (News: /news/, /news/{pk}/, /news/{pk}/delete)
    path('', include(router.urls)),

    # Authentication
    path('login/', views.MyTokenObtainPairView.as_view(), name='login'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register-request/', views.register_request, name='register_request'),

    # User Profile
    path('me/', views.me, name='me'),
    # Admin Actions
    path('admin/users/', views.list_users, name='list_users'),
    path('admin/requests/', views.request_list, name='request_list'),
    path('admin/requests/all/', views.request_all, name='request_all'),
    path('admin/requests/<int:pk>/', views.request_detail, name='request_detail'),
    path('admin/requests/<int:pk>/approve/', views.request_approve, name='request_approve'),
    path('admin/requests/<int:pk>/reject/', views.request_reject, name='request_reject'),

    path("status/headman/", headman_status),
    path("status/headman/update/", update_headman_status),
]