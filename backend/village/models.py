from django.db import models
from django.core.exceptions import ValidationError

# ---------------------------
# Village (ข้อมูลหมู่บ้านแกนหลัก)
# ---------------------------
class Village(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True) # เก็บตัวเลขทศนิยมที่แม่นยำ (ไม่ใช้ Float เพราะ Float มีปัญหาเรื่องความแม่นยำ)
    address = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    # ========================================
    # [เพิ่มใหม่] พิกัดที่ตั้งหมู่บ้าน
    # ========================================
    # ใช้ DecimalField แทน FloatField เพราะ:
    #   - DecimalField เก็บเลขทศนิยมแม่นยำกว่า (ไม่มีปัญหา floating-point rounding)
    #   - max_digits=9  หมายถึงตัวเลขรวมทั้งหมดไม่เกิน 9 หลัก เช่น 15.228700 = 8 หลัก
    #   - decimal_places=6 หมายถึงทศนิยม 6 ตำแหน่ง ซึ่งแม่นยำระดับ ~0.1 เมตร เพียงพอ
    #   - null=True, blank=True เพื่อให้ยังไม่กรอกพิกัดก็ได้
    #     (ถ้าไม่ใส่ null=True Django จะบังคับกรอกตั้งแต่แรก migrate)

    latitude = models.DecimalField(
        max_digits=9, #ตัวเลขรวมกันได้ไม่เกิน 9 หลัก เช่น 15.234567
        decimal_places=6, #ทศนิยม 6 ตำแหน่ง — พิกัดโลกต้องการแค่นี้
        null=True, #ยอมให้เป็น NULL ใน database ได้ (ยังไม่ตั้งพิกัด)
        blank=True, #ยอมให้ส่งค่าว่างจาก Form/API ได้
        verbose_name="ละติจูด"
    )
    longitude = models.DecimalField(
        max_digits=9, #ตัวเลขรวมกันได้ไม่เกิน 9 หลัก เช่น 15.234567
        decimal_places=6, #ทศนิยม 6 ตำแหน่ง — พิกัดโลกต้องการแค่นี้
        null=True, #ยอมให้เป็น NULL ใน database ได้ (ยังไม่ตั้งพิกัด)
        blank=True, #ยอมให้ส่งค่าว่างจาก Form/API ได้
        verbose_name="ลองจิจูด"
    )
    # (ถ้าไม่ใส่ null=True Django จะบังคับกรอกในขั้นตอนตั้งแต่แรกการmigrate)
    # ========================================

    def __str__(self):
        return self.name


# ---------------------------
# Sections (หัวข้อข้อมูลหมู่บ้าน)
# ---------------------------
class VillageSection(models.Model):
    TYPE_CHOICES = (
        ("RICH", "Rich Content"),
        ("PLACES", "Places List"),
    )

    type        = models.CharField(max_length=20, choices=TYPE_CHOICES, default="RICH")
    title       = models.CharField(max_length=255)
    content     = models.TextField(blank=True, default="")        # RICH
    description = models.TextField(blank=True, default="")        # PLACES
    order       = models.PositiveIntegerField(default=0)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.type}: {self.title}"


def section_image_path(instance, filename):
    return f"village/sections/{instance.section_id}/{filename}"

class VillageSectionImage(models.Model):
    section    = models.ForeignKey(VillageSection, on_delete=models.CASCADE, related_name="images")
    image      = models.ImageField(upload_to=section_image_path)
    caption    = models.CharField(max_length=255, blank=True, default="")
    order      = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order", "id"]


# ---------------------------
# Places (รายการสถานที่ในหัวข้อ PLACES)
# ---------------------------
class VillagePlace(models.Model):
    section = models.ForeignKey(
        VillageSection,
        on_delete=models.CASCADE,
        related_name="places",
        null=True,
        blank=True,
    )
    name   = models.CharField(max_length=255)
    detail = models.TextField(blank=True, default="")
    order  = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.name


def place_image_path(instance, filename):
    return f"village/places/{instance.place_id}/{filename}"


class VillagePlaceImage(models.Model):
    place      = models.ForeignKey(VillagePlace, on_delete=models.CASCADE, related_name="images")
    image      = models.ImageField(upload_to=place_image_path)
    caption    = models.CharField(max_length=255, blank=True, default="")
    order      = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order", "id"]

POSITION_CONFIG = {
    "leader": [
        {"name": "ผู้ใหญ่บ้าน",          "max": 1,    "level": 1},
        {"name": "ผู้ช่วยผู้ใหญ่บ้าน",   "max": 3,    "level": 2},
        {"name": "อาสาเกษตรหมู่บ้าน",    "max": 1,    "level": 2},
        {"name": "อบต.",                   "max": 1,    "level": 2},
        {"name": "อปพร.",                  "max": None, "level": 3},
    ],
    "volunteer": [
        {"name": "ประธานอาสาสาธารณสุขประจำหมู่บ้าน",      "max": 1,    "level": 1},
        {"name": "รองประธานอาสาสาธารณสุขประจำหมู่บ้าน",   "max": 2,    "level": 2},
        {"name": "อาสาสาธารณสุขประจำหมู่บ้าน",             "max": None, "level": 3},
    ],
    "committee": [
        {"name": "ประธานคณะกรรมการหมู่บ้าน",  "max": 1,    "level": 1},
        {"name": "รองประธานคณะกรรมการ",        "max": 2,    "level": 2},
        {"name": "กรรมการหมู่บ้าน",            "max": None, "level": 3},
    ],
}

# ---------------------------
# Community Profiles
# ---------------------------
class CommunityProfile(models.Model):
    GROUP_CHOICES = [
        ("leader", "ผู้นำชุมชน"),
        ("committee", "คณะกรรมการหมู่บ้าน"),
        ("volunteer", "อสม."),
    ]

    village     = models.ForeignKey(Village, on_delete=models.CASCADE, related_name="profiles")
    group       = models.CharField(max_length=20, choices=GROUP_CHOICES)
    prefix      = models.CharField(max_length=50, blank=True, default="")
    position    = models.CharField(max_length=100)
    level       = models.PositiveIntegerField(default=3)
    full_name   = models.CharField(max_length=255, blank=True)
    phone       = models.CharField(max_length=50, blank=True)
    email       = models.EmailField(blank=True, null=True)
    description = models.TextField(blank=True)
    image       = models.ImageField(upload_to="village/profiles/", blank=True, null=True)
    is_active   = models.BooleanField(default=True)

    def clean(self):
        group_positions = POSITION_CONFIG.get(self.group, [])
        for pos_config in group_positions:
            if self.position == pos_config["name"]:
                self.level = pos_config["level"]
                if pos_config["max"] is not None:
                    count = CommunityProfile.objects.filter(
                        village=self.village,
                        group=self.group,
                        position=self.position,
                    ).exclude(id=self.id).count()
                    if count >= pos_config["max"]:
                        raise ValidationError(
                            f"ตำแหน่ง {self.position} มีได้ไม่เกิน {pos_config['max']} คน"
                        )
                break

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.full_name} ({self.position})"


# ---------------------------
# Funds
# ---------------------------
class FundType(models.Model):
    village     = models.ForeignKey(Village, on_delete=models.CASCADE, related_name="fund_types")
    name        = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    is_active   = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class FundRecord(models.Model):
    fund_type          = models.ForeignKey(FundType, on_delete=models.CASCADE, related_name="records")
    year               = models.PositiveIntegerField()
    interest_rate      = models.DecimalField(max_digits=5, decimal_places=2, help_text="อัตราดอกเบี้ย (%)")
    last_uploaded_file = models.CharField(max_length=255, blank=True, null=True)
    created_at         = models.DateTimeField(auto_now_add=True)
    updated_at         = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("fund_type", "year")

    def __str__(self):
        return f"{self.fund_type.name} - {self.year}"


class FundLoan(models.Model):
    fund_record     = models.ForeignKey(FundRecord, on_delete=models.CASCADE, related_name="loans")
    full_name       = models.CharField(max_length=255)
    bank_account    = models.CharField(max_length=50)
    loan_amount     = models.DecimalField(max_digits=12, decimal_places=2)
    interest_amount = models.DecimalField(max_digits=12, decimal_places=2, help_text="ดอกเบี้ยที่ระบบคำนวณให้")
    purpose         = models.TextField(blank=True)
    created_at      = models.DateTimeField(auto_now_add=True)

    def masked_account(self):
        if len(self.bank_account) >= 6:
            return self.bank_account[:3] + "***" + self.bank_account[-3:]
        return self.bank_account

    def __str__(self):
        return self.full_name