# inventory/models.py
from django.db import models
from common.models import TimeStampedModel


class Material(TimeStampedModel):
    name = models.CharField(max_length=255)
    sku = models.CharField(max_length=50, unique=True)
    unit = models.CharField(max_length=30)
    quantity_in_stock = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    reorder_level = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    unit_cost = models.DecimalField(max_digits=14, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.name} ({self.sku})"


class StockTransaction(TimeStampedModel):
    TRANSACTION_CHOICES = [
        ("IN", "Nhập kho"),
        ("OUT", "Xuất kho"),
        ("ADJUST", "Điều chỉnh"),
    ]

    material = models.ForeignKey(
        Material,
        on_delete=models.CASCADE,
        related_name="transactions"
    )
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_CHOICES)
    quantity = models.DecimalField(max_digits=12, decimal_places=2)
    note = models.TextField(blank=True)

    def __str__(self):
        return f"{self.material.name} - {self.transaction_type} - {self.quantity}"