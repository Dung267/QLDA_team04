from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()


class Supplier(models.Model):
    name = models.CharField('Tên nhà cung cấp', max_length=200)
    contact_name = models.CharField('Người liên hệ', max_length=100, blank=True)
    phone = models.CharField('Điện thoại', max_length=20, blank=True)
    email = models.EmailField('Email', blank=True)
    address = models.TextField('Địa chỉ', blank=True)
    is_active = models.BooleanField('Đang hợp tác', default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Nhà cung cấp'
        verbose_name_plural = 'Nhà cung cấp'

    def __str__(self):
        return self.name


class MaterialCategory(models.Model):
    name = models.CharField('Tên danh mục', max_length=100)
    code = models.CharField('Mã', max_length=20, unique=True)

    class Meta:
        verbose_name = 'Danh mục vật tư'

    def __str__(self):
        return self.name


class Material(models.Model):
    UNIT_CHOICES = [
        ('kg', 'Kilogram'), ('ton', 'Tấn'), ('m', 'Mét'),
        ('m2', 'M²'), ('m3', 'M³'), ('piece', 'Cái'),
        ('liter', 'Lít'), ('box', 'Hộp'),
    ]

    name = models.CharField('Tên vật tư', max_length=200)
    code = models.CharField('Mã vật tư', max_length=50, unique=True)
    category = models.ForeignKey(MaterialCategory, on_delete=models.CASCADE, verbose_name='Danh mục')
    unit = models.CharField('Đơn vị', max_length=10, choices=UNIT_CHOICES)
    unit_price = models.DecimalField('Đơn giá (VNĐ)', max_digits=15, decimal_places=0, default=0)
    quantity_in_stock = models.FloatField('Tồn kho', default=0)
    minimum_stock = models.FloatField('Mức tồn tối thiểu', default=0)
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Nhà cung cấp')
    description = models.TextField('Mô tả', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Vật tư'
        verbose_name_plural = 'Vật tư'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.code})"

    @property
    def is_low_stock(self):
        return self.quantity_in_stock <= self.minimum_stock

    @property
    def total_value(self):
        return self.quantity_in_stock * float(self.unit_price)


class StockTransaction(models.Model):
    TYPE_CHOICES = [
        ('import', 'Nhập kho'),
        ('export', 'Xuất kho'),
        ('adjust', 'Điều chỉnh'),
        ('return', 'Trả lại'),
    ]

    material = models.ForeignKey(Material, on_delete=models.CASCADE, related_name='transactions', verbose_name='Vật tư')
    transaction_type = models.CharField('Loại', max_length=10, choices=TYPE_CHOICES)
    quantity = models.FloatField('Số lượng')
    unit_price = models.DecimalField('Đơn giá', max_digits=15, decimal_places=0, default=0)
    maintenance_request = models.ForeignKey('maintenance.MaintenanceRequest', on_delete=models.SET_NULL,
                                             null=True, blank=True, related_name='material_transactions',
                                             verbose_name='Yêu cầu bảo trì')
    reference_number = models.CharField('Số chứng từ', max_length=50, blank=True)
    note = models.TextField('Ghi chú', blank=True)
    performed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Giao dịch kho'
        verbose_name_plural = 'Giao dịch kho'
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if self.transaction_type == 'import':
            self.material.quantity_in_stock += self.quantity
        elif self.transaction_type in ('export', 'return'):
            self.material.quantity_in_stock -= self.quantity
        self.material.save(update_fields=['quantity_in_stock'])
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_transaction_type_display()} - {self.material.name} ({self.quantity})"


class MaintenanceMaterialUsage(models.Model):
    maintenance_request = models.ForeignKey('maintenance.MaintenanceRequest', on_delete=models.CASCADE,
                                             related_name='material_usages')
    material = models.ForeignKey(Material, on_delete=models.CASCADE, verbose_name='Vật tư')
    quantity_used = models.FloatField('Số lượng sử dụng')
    unit_price = models.DecimalField('Đơn giá', max_digits=15, decimal_places=0)
    note = models.CharField('Ghi chú', max_length=200, blank=True)
    recorded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Vật tư sử dụng'
        verbose_name_plural = 'Vật tư sử dụng'

    @property
    def total_cost(self):
        return float(self.unit_price) * self.quantity_used
