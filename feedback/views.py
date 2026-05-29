from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.core.paginator import Paginator
from django.db.models import Avg, Count, Q
from django.urls import reverse_lazy
from django.views.generic import CreateView
from datetime import datetime
from .models import SystemFeedback
from .forms import FeedbackForm
from accounts.decorators import staff_required

@login_required
def feedback_list(request):
    qs = SystemFeedback.objects.filter(status__in=['new','reviewed','resolved'])
    rating = request.GET.get('rating', '').strip()
    keyword = request.GET.get('q', '').strip()
    from_date = request.GET.get('from_date', '').strip()
    to_date = request.GET.get('to_date', '').strip()

    if rating:
        qs = qs.filter(rating=rating)

    if keyword:
        qs = qs.filter(
            Q(content__icontains=keyword) |
            Q(category__icontains=keyword)
        )

    if from_date:
        try:
            start_date = datetime.strptime(from_date, '%Y-%m-%d').date()
            qs = qs.filter(created_at__date__gte=start_date)
        except ValueError:
            messages.warning(request, 'Ngày bắt đầu không hợp lệ. Định dạng đúng: YYYY-MM-DD.')

    if to_date:
        try:
            end_date = datetime.strptime(to_date, '%Y-%m-%d').date()
            qs = qs.filter(created_at__date__lte=end_date)
        except ValueError:
            messages.warning(request, 'Ngày kết thúc không hợp lệ. Định dạng đúng: YYYY-MM-DD.')

    paginator = Paginator(qs, 20)
    page = paginator.get_page(request.GET.get('page', 1))
    avg_rating = SystemFeedback.objects.aggregate(avg=Avg('rating'))['avg']

    query_params = request.GET.copy()
    query_params.pop('page', None)

    return render(request, 'feedback/list.html', {
        'page_obj': page,
        'avg_rating': avg_rating,
        'page_title': 'Phản hồi & Đánh giá',
        'selected_rating': rating,
        'keyword': keyword,
        'from_date': from_date,
        'to_date': to_date,
        'query_string': query_params.urlencode(),
    })

class FeedbackCreateView(SuccessMessageMixin, CreateView):
    model = SystemFeedback
    form_class = FeedbackForm
    template_name = 'feedback/systemfeedback_form.html'
    success_url = reverse_lazy('feedback:list')
    success_message = 'Cảm ơn bạn đã gửi phản hồi về hệ thống hạ tầng đô thị Đà Nẵng.'

    def form_valid(self, form):
        if self.request.user.is_authenticated:
            form.instance.author = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Gửi phản hồi & Đánh giá hệ thống'
        return context

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
