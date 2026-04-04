from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Avg, Count
from .models import SystemFeedback
from accounts.decorators import staff_required

@login_required
def feedback_list(request):
    qs = SystemFeedback.objects.filter(status__in=['new','reviewed','resolved'])
    rating = request.GET.get('rating','')
    if rating: qs = qs.filter(rating=rating)
    paginator = Paginator(qs, 20)
    page = paginator.get_page(request.GET.get('page',1))
    avg_rating = SystemFeedback.objects.aggregate(avg=Avg('rating'))['avg']
    return render(request,'feedback/list.html',{
        'page_obj':page,'avg_rating':avg_rating,'page_title':'Phản hồi & Đánh giá'})

@login_required
def feedback_create(request):
    if request.method=='POST':
        rating = int(request.POST.get('rating',3))
        content = request.POST.get('content','').strip()
        is_anonymous = request.POST.get('is_anonymous')=='on'
        category = request.POST.get('category','')
        if not content:
            messages.error(request,'Vui lòng nhập nội dung phản hồi.')
            return redirect('feedback:create')
        SystemFeedback.objects.create(
            author=None if is_anonymous else request.user,
            is_anonymous=is_anonymous, rating=rating,
            content=content, category=category
        )
        messages.success(request,'Cảm ơn bạn đã gửi phản hồi!')
        return redirect('feedback:list')
    return render(request,'feedback/form.html',{'page_title':'Gửi phản hồi'})

@login_required
def feedback_detail(request, pk):
    fb = get_object_or_404(SystemFeedback, pk=pk)
    return render(request,'feedback/detail.html',{'fb':fb,'page_title':'Chi tiết phản hồi'})

@login_required
def feedback_like(request, pk):
    from django.http import JsonResponse
    fb = get_object_or_404(SystemFeedback, pk=pk)
    fb.likes += 1
    fb.save(update_fields=['likes'])
    return JsonResponse({'likes':fb.likes})

@login_required
@staff_required
def feedback_reply(request, pk):
    fb = get_object_or_404(SystemFeedback, pk=pk)
    if request.method=='POST':
        fb.admin_reply = request.POST.get('reply','')
        fb.status = 'resolved'
        fb.save()
        messages.success(request,'Đã gửi phản hồi tới người dùng.')
    return redirect('feedback:detail', pk=pk)

@login_required
@staff_required
def toggle_important(request, pk):
    from django.http import JsonResponse
    fb = get_object_or_404(SystemFeedback, pk=pk)
    fb.is_important = not fb.is_important
    fb.save(update_fields=['is_important'])
    return JsonResponse({'is_important':fb.is_important})

@login_required
@staff_required
def hide_feedback(request, pk):
    fb = get_object_or_404(SystemFeedback, pk=pk)
    fb.status = 'hidden'
    fb.save()
    messages.success(request,'Đã ẩn phản hồi.')
    return redirect('feedback:list')

@login_required
@staff_required
def feedback_stats(request):
    stats = {
        'total': SystemFeedback.objects.count(),
        'avg_rating': SystemFeedback.objects.aggregate(avg=Avg('rating'))['avg'],
        'by_rating': list(SystemFeedback.objects.values('rating').annotate(count=Count('id')).order_by('rating')),
        'by_status': list(SystemFeedback.objects.values('status').annotate(count=Count('id'))),
    }
    return render(request,'feedback/stats.html',{'stats':stats,'page_title':'Thống kê phản hồi'})
