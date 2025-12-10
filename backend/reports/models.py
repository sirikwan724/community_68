from django.db import models
from django.conf import settings
from django.conf import settings
User = settings.AUTH_USER_MODEL

class Report(models.Model):
    CATEGORY_CHOICES = [
        ("ไฟฟ้า", "ไฟฟ้า"),
        ("น้ำ", "น้ำ"),
        ("ถนน", "ถนน"),
        ("บุคคล", "บุคคล"),
        ("เสียง", "เสียง"),
        ("กลิ่น", "กลิ่น"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    fullname = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    category = models.CharField(max_length=50)
    description = models.TextField()
    area = models.CharField(max_length=255)
    image = models.ImageField(upload_to="reports/", null=True, blank=True)

    status = models.CharField(
        max_length=20,
        default="pending",
        choices=[
            ("pending", "รอตรวจสอบ"),
            ("processing", "กำลังดำเนินการ"),
            ("resolved", "แก้ไขแล้ว"),
        ]
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.category} - {self.fullname}"
    

class ReportNote(models.Model):
    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name="notes")
    text  = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Note for report {self.report.id}"
    
class RequestHelp(models.Model):
    STATUS_CHOICES = [
        ("pending", "รอตรวจสอบ"),
        ("approved", "อนุมัติ"),
        ("rejected", "ปฏิเสธ"),
        ("done", "ดำเนินการเสร็จสิ้น"),
    ]

    TYPE_CHOICES = [
        ("เสียง", "เสียง"),
        ("ปิดทาง", "ปิดทาง"),
        ("ทั้งสองอย่าง", "ทั้งสองอย่าง"),
        ("อื่นๆ", "อื่นๆ"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.SET_NULL, null=True)

    request_type = models.CharField(max_length=100, choices=TYPE_CHOICES, null=True, blank=True)
    start_datetime = models.DateTimeField(null=True, blank=True)
    end_datetime = models.DateTimeField(null=True, blank=True)

    detail = models.TextField()
    area = models.CharField(max_length=255)

    file = models.FileField(upload_to="help_files/", null=True, blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Appointment(models.Model):
    MEET_WITH_CHOICES = [
        ("headman", "ผู้ใหญ่บ้าน"),
        ("assistant_headman", "ผู้ช่วยผู้ใหญ่บ้าน"),
    ]

    PLACE_CHOICES = [
        ("village_hall", "ศาลากลางหมู่บ้าน"),
        ("temple", "วัด"),
        ("headman_office", "สถานที่ทำการผู้ใหญ่บ้าน"),
        ("learning_center", "ศูนย์ให้ความรู้หมู่บ้าน"),
    ]

    STATUS_CHOICES = [
        ("pending", "รอดำเนินการ"),
        ("approved", "ยืนยันนัดหมาย"),
        ("canceled", "ยกเลิกโดยผู้ใช้"),
        ("rejected", "ผู้ใหญ่บ้านปฏิเสธ"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    meet_with = models.CharField(max_length=30, choices=MEET_WITH_CHOICES)
    meeting_place = models.CharField(max_length=30, choices=PLACE_CHOICES)

    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()

    reason = models.TextField()

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    admin_note = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Appointment by {self.user} on {self.date}"
