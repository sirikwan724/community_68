from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings

class User(AbstractUser):
    ROLE_CHOICES = [
        ('guest', 'Guest'),
        ('user', 'Verified User'),
        ('admin', 'Village Admin'),
        ('superadmin', 'System Admin'),
    ]

    full_name = models.CharField(max_length=200, blank=True, null=True)
    address = models.TextField(blank=True)
    citizen_id = models.CharField(max_length=11, blank=True, null=True)
    house_owner_name = models.CharField(max_length=200, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='guest')
    verified = models.BooleanField(default=False)

    def __str__(self):
        return self.username

class RegistrationRequest(models.Model):
    full_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
    address = models.TextField()
    citizen_id = models.CharField(max_length=11)  # รหัสทะเบียนบ้าน
    house_owner_name = models.CharField(max_length=200)
    password = models.CharField(max_length=200)  # เก็บ hash
    status = models.CharField(max_length=20, default="pending")  # pending / approved / rejected
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} ({self.status})"

class News(models.Model):
    title = models.CharField(max_length=200, verbose_name="หัวข้อข่าว")
    content = models.TextField(verbose_name="เนื้อหาข่าว")
    image = models.ImageField(upload_to='news_images/', blank=True, null=True, verbose_name="รูปภาพประกอบ")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="วันที่ประกาศ")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="แก้ไขล่าสุดเมื่อ")
    
    # เชื่อมว่าใครเป็นคนโพสต์ (Admin คนไหน)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        verbose_name="ผู้ประกาศ"
    )

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at'] # เรียงจากใหม่ไปเก่าเสมอ
        verbose_name_plural = "ข่าวสารประชาสัมพันธ์"

class HeadmanStatus(models.Model):
    is_online = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "ออนไลน์" if self.is_online else "ออฟไลน์"
