from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Location(models.Model):
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Item(models.Model):
    name = models.CharField(max_length=100)
    unit = models.CharField(max_length=50)  # หลัง / ลัง / ตัว / ชุด
    stock = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.stock} {self.unit})"


class BorrowRequest(models.Model):

    BORROW_TYPE = (
        ('ITEM', 'Item'),
        ('LOCATION', 'Location'),
    )

    STATUS = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('borrowed', 'Borrowed'),
        ('return_requested', 'Return Requested'),
        ('returned', 'Returned'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='borrow_requests'
    )

    # snapshot ข้อมูลผู้ยืม
    borrower_name = models.CharField(max_length=150)
    borrower_phone = models.CharField(max_length=20)

    borrow_type = models.CharField(max_length=10, choices=BORROW_TYPE)

    # กรณียืมสถานที่
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()

    pickup_datetime = models.DateTimeField(null=True, blank=True)
    expected_return_datetime = models.DateTimeField(null=True, blank=True)

    purpose = models.TextField()
    image = models.ImageField(upload_to='borrow/', null=True, blank=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS,
        default='pending'
    )

    admin_note = models.TextField(blank=True, default="")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.borrower_name} - {self.borrow_type} - {self.status}"


class BorrowItem(models.Model):
    borrow_request = models.ForeignKey(
        BorrowRequest,
        related_name='items',
        on_delete=models.CASCADE
    )
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.item.name} x {self.quantity}"
