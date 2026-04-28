from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from .models import Document, DocumentCategory
from infrastructure.models import Road, Infrastructure
from .forms import DocumentForm


@login_required
def list_documents(request):
    """Danh sách tài liệu với filter, tìm kiếm, phân trang"""
    documents = Document.objects.select_related('category', 'uploaded_by', 'road', 'infrastructure')
    
    # Filter by category
    category_id = request.GET.get('category')
    if category_id:
        documents = documents.filter(category_id=category_id)
    
    # Filter by scope (public/private)
    scope = request.GET.get('scope')
    if scope == 'public':
        documents = documents.filter(is_public=True)
    elif scope == 'private':
        documents = documents.filter(is_public=False)
    
    # Search by title or description
    search_query = request.GET.get('q')
    if search_query:
        documents = documents.filter(
            Q(title__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(documents, 10)  # 10 items per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get all categories for dropdown
    categories = DocumentCategory.objects.all().order_by('name')
    
    context = {
        'documents': page_obj,
        'page_obj': page_obj,
        'categories': categories,
    }
    return render(request, 'documents/list.html', context)


@login_required
def upload_document(request):
    """Form upload tài liệu mới"""
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.uploaded_by = request.user
            
            # Auto-fill title if not provided
            if not document.title and request.FILES.get('file'):
                document.title = request.FILES['file'].name.rsplit('.', 1)[0]
            
            document.save()
            messages.success(request, f'Tài liệu "{document.title}" đã được upload thành công!')
            return redirect('documents:list')
        else:
            # Show validation errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = DocumentForm()
    
    # Get data for dropdowns
    categories = DocumentCategory.objects.all().order_by('name')
    roads = Road.objects.all().order_by('name')
    infrastructures = Infrastructure.objects.all().order_by('name')
    
    # Get recent uploads for sidebar
    recent_documents = Document.objects.filter(
        uploaded_by=request.user
    ).order_by('-created_at')[:5]
    
    context = {
        'form': form,
        'categories': categories,
        'roads': roads,
        'infrastructures': infrastructures,
        'recent_documents': recent_documents,
    }
    return render(request, 'documents/upload.html', context)


@login_required
def document_detail(request, pk):
    """Chi tiết tài liệu"""
    document = get_object_or_404(Document, pk=pk)
    
    # Check permissions - nếu private thì chỉ staff và owner được xem
    if not document.is_public and not request.user.is_staff and document.uploaded_by != request.user:
        messages.error(request, 'Bạn không có quyền xem tài liệu này!')
        return redirect('documents:list')
    
    context = {
        'document': document,
    }
    return render(request, 'documents/detail.html', context)


@login_required
def edit_document(request, pk):
    """Chỉnh sửa tài liệu (chỉ staff)"""
    document = get_object_or_404(Document, pk=pk)
    
    # Check permissions
    if not request.user.is_staff and document.uploaded_by != request.user:
        messages.error(request, 'Bạn không có quyền chỉnh sửa tài liệu này!')
        return redirect('documents:list')
    
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES, instance=document)
        if form.is_valid():
            document = form.save()
            messages.success(request, f'Tài liệu "{document.title}" đã được cập nhật!')
            return redirect('documents:detail', pk=document.id)
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = DocumentForm(instance=document)
    
    # Get data for dropdowns
    categories = DocumentCategory.objects.all().order_by('name')
    roads = Road.objects.all().order_by('name')
    infrastructures = Infrastructure.objects.all().order_by('name')
    
    context = {
        'form': form,
        'document': document,
        'categories': categories,
        'roads': roads,
        'infrastructures': infrastructures,
        'is_edit': True,
    }
    return render(request, 'documents/upload.html', context)


@login_required
def delete_document(request, pk):
    """Xóa tài liệu (chỉ staff)"""
    document = get_object_or_404(Document, pk=pk)
    
    # Check permissions
    if not request.user.is_staff and document.uploaded_by != request.user:
        messages.error(request, 'Bạn không có quyền xóa tài liệu này!')
        return redirect('documents:list')
    
    if request.method == 'POST':
        title = document.title
        document.delete()
        messages.success(request, f'Tài liệu "{title}" đã được xóa!')
        return redirect('documents:list')
    
    context = {
        'document': document,
    }
    return render(request, 'documents/confirm_delete.html', context)


@login_required
def download_document(request, pk):
    """Download file tài liệu"""
    document = get_object_or_404(Document, pk=pk)
    
    # Check permissions
    if not document.is_public and not request.user.is_staff and document.uploaded_by != request.user:
        messages.error(request, 'Bạn không có quyền download tài liệu này!')
        return redirect('documents:list')
    
    # Redirect to file URL (Django sẽ handle download)
    if document.file:
        return redirect(document.file.url)
    else:
        messages.error(request, 'Tệp không tồn tại!')
        return redirect('documents:list')