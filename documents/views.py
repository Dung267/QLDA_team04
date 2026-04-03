from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Document, DocumentCategory
from accounts.decorators import staff_required


@login_required
@staff_required
def document_list(request):
    documents = Document.objects.select_related('category', 'uploaded_by').all()
    q = request.GET.get('q', '')
    category = request.GET.get('category', '')
    if q:
        documents = documents.filter(Q(title__icontains=q) | Q(description__icontains=q))
    if category:
        documents = documents.filter(category_id=category)
    paginator = Paginator(documents, 20)
    page = paginator.get_page(request.GET.get('page', 1))
    return render(request, 'documents/list.html', {
        'page_obj': page,
        'categories': DocumentCategory.objects.all(),
        'page_title': 'Tài liệu',
    })


@login_required
@staff_required
def document_upload(request):
    from .forms import DocumentForm
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            doc = form.save(commit=False)
            doc.uploaded_by = request.user
            doc.save()
            messages.success(request, 'Đã tải lên tài liệu.')
            return redirect('documents:list')
    else:
        form = DocumentForm()
    return render(request, 'documents/upload.html', {'form': form, 'page_title': 'Tải lên tài liệu'})


@login_required
@staff_required
def document_detail(request, pk):
    doc = get_object_or_404(Document, pk=pk)
    return render(request, 'documents/detail.html', {'doc': doc, 'page_title': doc.title})