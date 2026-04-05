from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()

class Supplier(models.Model):
    name = models.CharField('Tên nhà cung cấp', max_length=200)
    contact = models.CharField('Người liên hệ', max_length=100, blank=True)
    phone = models.CharField('SĐT', max_length=15, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Nhà cung cấp'
        verbose_name_plural = 'Nhà cung cấp'

    def __str__(self): return self.name

class Material(models.Model):
    UNIT_CHOICES = [('kg','kg'),('m','m'),('m2','m²'),('m3','m³'),('cai','Cái'),('cuon','Cuộn'),('thung','Thùng')]
    name = models.CharField('Tên vật tư', max_length=200)
    code = models.CharField('Mã', max_length=50, unique=True)
    unit = models.CharField('Đơn vị', max_length=10, choices=UNIT_CHOICES, default='cai')
    unit_price = models.DecimalField('Đơn giá (VNĐ)', max_digits=15, decimal_places=0, default=0)
    current_stock = models.FloatField('Tồn kho', default=0)
    min_stock = models.FloatField('Tồn kho tối thiểu', default=10)
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Vật tư'
        verbose_name_plural = 'Vật tư'

    def __str__(self): return f"{self.name} ({self.code})"

    @property
    def is_low_stock(self): return self.current_stock <= self.min_stock

class StockTransaction(models.Model):
    TYPE_CHOICES = [('in','Nhập kho'),('out','Xuất kho'),('adjust','Điều chỉnh')]
    material = models.ForeignKey(Material, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField('Loại', max_length=10, choices=TYPE_CHOICES)
    quantity = models.FloatField('Số lượng')
    unit_price = models.DecimalField('Đơn giá', max_digits=15, decimal_places=0, default=0)
    reason = models.CharField('Lý do', max_length=300, blank=True)
    maintenance_request = models.ForeignKey('maintenance.MaintenanceRequest', on_delete=models.SET_NULL,
                                             null=True, blank=True, related_name='material_usages')
    performed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    invoice_number = models.CharField('Số hóa đơn', max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Giao dịch kho'
        verbose_name_plural = 'Giao dịch kho'
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        mat = self.material
        if self.transaction_type == 'in':
            mat.current_stock += self.quantity
        elif self.transaction_type == 'out':
            mat.current_stock -= self.quantity
        else:
            mat.current_stock = self.quantity
        mat.save(update_fields=['current_stock'])
