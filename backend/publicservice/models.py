from django.db import models
from django.conf import settings

class PublicService(models.Model):
    CATEGORY_CHOICES = [
        ("water", "ตู้กดน้ำ"),
        ("washer", "เครื่องซักผ้า"),
        ("other", "บริการอื่นๆ"),
    ]

    STATUS_CHOICES = [
        ("normal", "ใช้งานได้ปกติ"),
        ("maintenance", "กำลังซ่อมบำรุง"),
        ("broken", "ชำรุด"),
    ]

    name = models.CharField(max_length=255)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    location = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="normal")
    image = models.ImageField(upload_to="services/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name}"


class PublicServiceReport(models.Model):
    STATUS_CHOICES = [
        ("pending", "รอดำเนินการ"),
        ("processing", "กำลังดำเนินการ"),
        ("resolved", "เสร็จสิ้น"),
        ("canceled", "ยกเลิกแล้ว"),
    ]

    service = models.ForeignKey(PublicService, on_delete=models.CASCADE, related_name="reports")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="service_reports")

    title = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to="service_reports/", blank=True, null=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.service.name} - {self.title}"