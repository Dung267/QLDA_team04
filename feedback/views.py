from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Avg, Count
from django.utils import timezone
from .models import SystemFeedback
from .forms import FeedbackForm
from accounts.decorators import staff_required


def feedback_list(request):
    feedbacks = SystemFeedback.objects.exclude(status='hidden').order_by('-created_at')
    category = request.GET.get('category', '')
    rating = request.GET.get('rating', '')
    date_from = request.GET.get('date_from', '')
    q = request.GET.get('q', '')
    if category:
        feedbacks = feedbacks.filter(category=category)
    if rating:
        feedbacks = feedbacks.filter(rating=rating)
    if date_from:
        feedbacks = feedbacks.filter(created_at__date__gte=date_from)
    if q:
        feedbacks = feedbacks.filter(Q(title__icontains=q) | Q(content__icontains=q))
    paginator = Paginator(feedbacks, 20)
    page = paginator.get_page(request.GET.get('page', 1))
    avg_rating = SystemFeedback.objects.filter(rating__isnull=False).aggregate(avg=Avg('rating'))['avg']
    return render(request, 'feedback/list.html', {
        'page_obj': page,
        'category_choices': SystemFeedback.CATEGORY_CHOICES,
        'avg_rating': avg_rating,
        'page_title': 'Phản hồi & Đánh giá',
    })


def feedback_create(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            fb = form.save(commit=False)
            if request.user.is_authenticated and not fb.is_anonymous:
                fb.author = request.user
            fb.save()
            messages.success(request, 'Cảm ơn bạn đã gửi phản hồi!')
            return redirect('feedback:list')
    else:
        form = FeedbackForm()
    return render(request, 'feedback/form.html', {'form': form, 'page_title': 'Gửi phản hồi'})


def feedback_detail(request, pk):
    fb = get_object_or_404(SystemFeedback, pk=pk)
    return render(request, 'feedback/detail.html', {'fb': fb, 'page_title': fb.title})


@login_required
def feedback_like(request, pk):
    fb = get_object_or_404(SystemFeedback, pk=pk)
    fb.like_count += 1
    fb.save(update_fields=['like_count'])
    from django.http import JsonResponse
    return JsonResponse({'likes': fb.like_count})


@login_required
@staff_required
def feedback_reply(request, pk):
    fb = get_object_or_404(SystemFeedback, pk=pk)
    if request.method == 'POST':
        fb.admin_reply = request.POST.get('reply', '')
        fb.replied_by = request.user
        fb.replied_at = timezone.now()
        fb.status = 'resolved'
        fb.save()
        messages.success(request, 'Đã gửi phản hồi.')
    return redirect('feedback:detail', pk=pk)


@login_required
@staff_required
def feedback_hide(request, pk):
    fb = get_object_or_404(SystemFeedback, pk=pk)
    fb.status = 'hidden'
    fb.save()
    messages.success(request, 'Đã ẩn phản hồi.')
    return redirect('feedback:list')


def feedback_stats(request):
    stats = {
        'total': SystemFeedback.objects.count(),
        'avg_rating': SystemFeedback.objects.filter(rating__isnull=False).aggregate(avg=Avg('rating'))['avg'],
        'by_category': list(SystemFeedback.objects.values('category').annotate(c=Count('id'))),
        'by_status': list(SystemFeedback.objects.values('status').annotate(c=Count('id'))),
        'top_feedbacks': SystemFeedback.objects.order_by('-like_count')[:5],
    }
    return render(request, 'feedback/stats.html', {'stats': stats, 'page_title': 'Thống kê phản hồi'})
