from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Document, DocumentCategory
from accounts.decorators import staff_required

@login_required
def document_list(request):
    docs = Document.objects.select_related('category','uploaded_by').all()
    if request.user.role == 'citizen':
        docs = docs.filter(is_public=True)
    paginator = Paginator(docs, 20)
    page = paginator.get_page(request.GET.get('page',1))
    categories = DocumentCategory.objects.all()
    return render(request,'documents/list.html',{'page_obj':page,'categories':categories,'page_title':'Tài liệu'})

@login_required
@staff_required
def document_upload(request):
    from .forms import DocumentForm
    if request.method=='POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            doc = form.save(commit=False)
            doc.uploaded_by = request.user
            doc.save()
            messages.success(request,'Đã tải lên tài liệu.')
            return redirect('documents:list')
    else:
        form = DocumentForm()
    return render(request,'documents/upload.html',{'form':form,'page_title':'Tải lên tài liệu'})
