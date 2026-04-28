from django import forms
from .models import Document, DocumentCategory


class DocumentForm(forms.ModelForm):
    """Form upload/edit tài liệu"""
    
    class Meta:
        model = Document
        fields = ['title', 'category', 'description', 'file', 'version', 'road', 'infrastructure', 'is_public']
        
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ví dụ: Bản vẽ thiết kế đường A',
                'maxlength': '300',
                'required': True
            }),
            'category': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Nhập mô tả thêm về tài liệu...'
            }),
            'file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx,.xls,.xlsx,.ppt,.pptx,.jpg,.jpeg,.png,.gif',
                'required': False  # Không bắt buộc khi chỉnh sửa
            }),
            'version': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ví dụ: 1.0, 1.1, 2.0',
                'maxlength': '20',
                'value': '1.0'
            }),
            'road': forms.Select(attrs={
                'class': 'form-select'
            }),
            'infrastructure': forms.Select(attrs={
                'class': 'form-select'
            }),
            'is_public': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        
        labels = {
            'title': 'Tiêu đề tài liệu',
            'category': 'Danh mục',
            'description': 'Mô tả',
            'file': 'Chọn tài liệu',
            'version': 'Phiên bản',
            'road': 'Tuyến đường',
            'infrastructure': 'Hạ tầng',
            'is_public': 'Công khai',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Làm field file optional khi edit (khi instance đã tồn tại)
        if self.instance and self.instance.pk:
            self.fields['file'].required = False
            self.fields['title'].required = False
        
        # Thêm class cho select fields
        self.fields['category'].empty_label = "-- Chọn danh mục --"
        self.fields['road'].empty_label = "-- Không chọn --"
        self.fields['infrastructure'].empty_label = "-- Không chọn --"
        
        # Order categories, roads, infrastructures
        self.fields['category'].queryset = self.fields['category'].queryset.order_by('name')
        self.fields['road'].queryset = self.fields['road'].queryset.order_by('name')
        self.fields['infrastructure'].queryset = self.fields['infrastructure'].queryset.order_by('name')
    
    def clean(self):
        cleaned_data = super().clean()
        file = cleaned_data.get('file')
        title = cleaned_data.get('title')
        
        # Validate file size
        if file and file.size > 52428800:  # 50MB
            raise forms.ValidationError('Dung lượng file vượt quá giới hạn 50MB!')
        
        # Validate that title or file exists (khi create)
        if not self.instance or not self.instance.pk:
            if not title:
                raise forms.ValidationError('Tiêu đề không được để trống!')
            if not file:
                raise forms.ValidationError('Bạn phải chọn file!')
        
        return cleaned_data
    
    def clean_file(self):
        file = self.cleaned_data.get('file')
        
        if file:
            # Validate file extension
            allowed_extensions = ['pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'jpg', 'jpeg', 'png', 'gif']
            file_extension = file.name.split('.')[-1].lower()
            
            if file_extension not in allowed_extensions:
                raise forms.ValidationError(f'Loại file "{file_extension.upper()}" không được hỗ trợ!')
            
            # Validate file size
            if file.size > 52428800:  # 50MB
                raise forms.ValidationError('Dung lượng file vượt quá giới hạn 50MB!')
        
        return file