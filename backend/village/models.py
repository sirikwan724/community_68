from django.db import models
from django.core.exceptions import ValidationError

# Create your models here.
#ข้อมูลหมู่บ้าน (แกนหลัก)
class Village(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    address = models.TextField(blank=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
#ประวัติความเป็นมา ประวัติหมู่บ้าน
class VillageHistory(models.Model):
    village = models.OneToOneField(
        Village,
        on_delete=models.CASCADE,
        related_name="history"
    )
    content = models.TextField()
    image = models.ImageField(
        upload_to="village/history/",
        blank=True,
        null=True
    )

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"History of {self.village.name}"

#สถานที่สำคัญ สถานที่สาธารณะ
class VillagePlace(models.Model):
    village = models.ForeignKey(
        Village,
        on_delete=models.CASCADE,
        related_name="places"
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    image = models.ImageField(
        upload_to="village/places/",
        blank=True,
        null=True
    )
    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name

#ข้อมูลเพิ่มเติม
class VillageExtraSection(models.Model):
    village = models.ForeignKey(
        Village,
        on_delete=models.CASCADE,
        related_name="extra_sections"
    )
    title = models.CharField(max_length=255)
    content = models.TextField()
    image = models.ImageField(
        upload_to="village/extra/",
        blank=True,
        null=True
    )
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

#โปรไฟล์ผู้นำ / กรรมการ / อสม.
class CommunityProfile(models.Model):
    GROUP_CHOICES = [
        ("leader", "ผู้นำชุมชน"),
        ("committee", "คณะกรรมการหมู่บ้าน"),
        ("volunteer", "อสม."),
    ]

    village = models.ForeignKey(
        Village,
        on_delete=models.CASCADE,
        related_name="profiles"
    )

    group = models.CharField(max_length=20, choices=GROUP_CHOICES)

    # ไม่ fix choice แล้ว
    position = models.CharField(max_length=100)

    # เพิ่ม level สำหรับ layout
    level = models.PositiveIntegerField(default=3)
    # 1 = ตรงกลาง
    # 2 = รอง
    # 3 = สมาชิกทั่วไป

    full_name = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True, null=True)
    description = models.TextField(blank=True)

    image = models.ImageField(
        upload_to="village/profiles/",
        blank=True,
        null=True
    )

    is_active = models.BooleanField(default=True)

    def clean(self):
        # จำกัด level 1 ไม่เกิน 1 คนต่อ group ต่อ village
        if self.level == 1:
            count = CommunityProfile.objects.filter(
                village=self.village,
                group=self.group,
                level=1
            ).exclude(id=self.id).count()

            if count >= 1:
                raise ValidationError("ในแต่ละกลุ่มมีตำแหน่งหลักได้เพียง 1 คน")

        # จำกัด level 2 ไม่เกิน 3 คนต่อ group ต่อ village
        if self.level == 2:
            count = CommunityProfile.objects.filter(
                village=self.village,
                group=self.group,
                level=2
            ).exclude(id=self.id).count()

            if count >= 3:
                raise ValidationError("ในแต่ละกลุ่มมีรองได้ไม่เกิน 3 คน")
            
    def save(self, *args, **kwargs):
        self.full_clean()  # เรียก clean() ก่อน save
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.full_name} ({self.position})"

#ประเภทกองทุน
class FundType(models.Model):
    village = models.ForeignKey(
        Village,
        on_delete=models.CASCADE,
        related_name="fund_types"
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

#ข้อมูลกองทุนรายปี
class FundRecord(models.Model):
    fund_type = models.ForeignKey(
        FundType,
        on_delete=models.CASCADE,
        related_name="records"
    )
    year = models.PositiveIntegerField()
    interest_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="อัตราดอกเบี้ย (%)"
    )

    last_uploaded_file = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("fund_type", "year")

    def __str__(self):
        return f"{self.fund_type.name} - {self.year}"

#รายชื่อผู้กู้ (ข้อมูลจากไฟล์ Excel)
class FundLoan(models.Model):
    fund_record = models.ForeignKey(
        FundRecord,
        on_delete=models.CASCADE,
        related_name="loans"
    )

    full_name = models.CharField(max_length=255)
    bank_account = models.CharField(max_length=50)
    loan_amount = models.DecimalField(max_digits=12, decimal_places=2)

    interest_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="ดอกเบี้ยที่ระบบคำนวณให้"
    )

    purpose = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def masked_account(self):
        if len(self.bank_account) >= 6:
            return (
                self.bank_account[:3]
                + "***"
                + self.bank_account[-3:]
            )
        return self.bank_account

    def __str__(self):
        return self.full_name

