from django.db import models
from django.core.exceptions import ValidationError

# ---------------------------
# Village (ข้อมูลหมู่บ้านแกนหลัก)
# ---------------------------
class Village(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    address = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)

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

    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default="RICH")
    title = models.CharField(max_length=255)
    content = models.TextField(blank=True, default="")        # RICH
    description = models.TextField(blank=True, default="")    # PLACES
    order = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.type}: {self.title}"


def section_image_path(instance, filename):
    return f"village/sections/{instance.section_id}/{filename}"

class VillageSectionImage(models.Model):
    section = models.ForeignKey(
        VillageSection,
        on_delete=models.CASCADE,
        related_name="images"
    )
    image = models.ImageField(upload_to=section_image_path)
    caption = models.CharField(max_length=255, blank=True, default="")
    order = models.PositiveIntegerField(default=0)
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
    name = models.CharField(max_length=255)
    detail = models.TextField(blank=True, default="")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.name


def place_image_path(instance, filename):
    return f"village/places/{instance.place_id}/{filename}"


class VillagePlaceImage(models.Model):
    place = models.ForeignKey(
        VillagePlace,
        on_delete=models.CASCADE,
        related_name="images"
    )
    image = models.ImageField(upload_to=place_image_path)
    caption = models.CharField(max_length=255, blank=True, default="")
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order", "id"]


# ---------------------------
# Community Profiles
# ---------------------------
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
    position = models.CharField(max_length=100)
    level = models.PositiveIntegerField(default=3)

    full_name = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=50, blank=True)
    email = models.EmailField(blank=True, null=True)
    description = models.TextField(blank=True)

    image = models.ImageField(upload_to="village/profiles/", blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def clean(self):
        if self.level == 1:
            count = CommunityProfile.objects.filter(
                village=self.village, group=self.group, level=1
            ).exclude(id=self.id).count()
            if count >= 1:
                raise ValidationError("ในแต่ละกลุ่มมีตำแหน่งหลักได้เพียง 1 คน")

        if self.level == 2:
            count = CommunityProfile.objects.filter(
                village=self.village, group=self.group, level=2
            ).exclude(id=self.id).count()
            if count >= 3:
                raise ValidationError("ในแต่ละกลุ่มมีรองได้ไม่เกิน 3 คน")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.full_name} ({self.position})"


# ---------------------------
# Funds
# ---------------------------
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


class FundRecord(models.Model):
    fund_type = models.ForeignKey(
        FundType,
        on_delete=models.CASCADE,
        related_name="records"
    )
    year = models.PositiveIntegerField()
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, help_text="อัตราดอกเบี้ย (%)")

    last_uploaded_file = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("fund_type", "year")

    def __str__(self):
        return f"{self.fund_type.name} - {self.year}"


class FundLoan(models.Model):
    fund_record = models.ForeignKey(
        FundRecord,
        on_delete=models.CASCADE,
        related_name="loans"
    )

    full_name = models.CharField(max_length=255)
    bank_account = models.CharField(max_length=50)
    loan_amount = models.DecimalField(max_digits=12, decimal_places=2)
    interest_amount = models.DecimalField(max_digits=12, decimal_places=2, help_text="ดอกเบี้ยที่ระบบคำนวณให้")
    purpose = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def masked_account(self):
        if len(self.bank_account) >= 6:
            return self.bank_account[:3] + "***" + self.bank_account[-3:]
        return self.bank_account

    def __str__(self):
        return self.full_name