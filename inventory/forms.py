from django import forms
from .models import Material, StockTransaction, Supplier


class StockTransactionForm(forms.ModelForm):
    """
    Form nhập/xuất kho – chỉ dùng đúng các field trong model gốc:
    material, transaction_type, quantity, unit_price, reason, invoice_number, maintenance_request
    """

    class Meta:
        model = StockTransaction
        fields = [
            'material',
            'transaction_type',
            'quantity',
            'unit_price',
            'invoice_number',
            'reason',
        ]
        # maintenance_request ẩn – chỉ gán khi có context bảo trì
        widgets = {
            'reason': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['invoice_number'].required = False
        self.fields['reason'].required = False

    def clean(self):
        cleaned = super().clean()
        tx_type = cleaned.get('transaction_type')
        qty = cleaned.get('quantity')

        if qty is not None and qty <= 0:
            self.add_error('quantity', 'Số lượng phải lớn hơn 0.')

        # Kiểm tra không xuất quá tồn kho
        if tx_type == 'out':
            material = cleaned.get('material')
            if material and qty and material.current_stock < qty:
                self.add_error(
                    'quantity',
                    f'Số lượng xuất ({qty}) vượt quá tồn kho hiện tại ({material.current_stock}).'
                )
        return cleaned


class MaterialForm(forms.ModelForm):
    """Form tạo/chỉnh sửa vật tư – khớp với model gốc."""

    class Meta:
        model = Material
        fields = [
            'name', 'code', 'unit', 'unit_price',
            'current_stock', 'min_stock', 'supplier', 'description',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['supplier'].queryset = Supplier.objects.all()
        self.fields['supplier'].required = False
        self.fields['description'].required = False