from django.db import models

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
