from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.db.models import Count, Q, Avg
from django.utils import timezone
import json
import uuid
from .models import ChatSession, ChatMessage, FAQItem


def chat_widget(request):
    faqs = FAQItem.objects.filter(is_active=True).order_by('-view_count')[:10]
    return render(request, 'chatbot/widget.html', {'faqs': faqs, 'page_title': 'Trợ lý ảo'})


@csrf_exempt
def chat_api(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()
        session_id = data.get('session_id', str(uuid.uuid4()))
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    if not user_message:
        return JsonResponse({'error': 'Empty message'}, status=400)

    # Lấy hoặc tạo session
    session, _ = ChatSession.objects.get_or_create(
        session_id=session_id,
        defaults={'user': request.user if request.user.is_authenticated else None}
    )

    # Lưu tin nhắn người dùng
    ChatMessage.objects.create(session=session, role='user', content=user_message)

    # Tìm câu trả lời từ FAQ
    response_text, understood = _find_answer(user_message)

    # Lưu phản hồi bot
    ChatMessage.objects.create(
        session=session, role='bot', content=response_text,
        was_understood=understood
    )

    return JsonResponse({
        'reply': response_text,
        'session_id': session_id,
        'understood': understood,
        'suggestions': _get_suggestions(user_message),
    })


@csrf_exempt
def rate_session(request, session_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            session = ChatSession.objects.get(session_id=session_id)
            session.rating = data.get('rating', 3)
            session.feedback = data.get('feedback', '')
            session.ended_at = timezone.now()
            session.save()
            return JsonResponse({'success': True})
        except ChatSession.DoesNotExist:
            return JsonResponse({'error': 'Session not found'}, status=404)
    return JsonResponse({'error': 'Method not allowed'}, status=405)


def faq_list(request):
    from django.contrib.auth.decorators import login_required
    faqs = FAQItem.objects.all()
    q = request.GET.get('q', '')
    category = request.GET.get('category', '')
    if q:
        faqs = faqs.filter(Q(question__icontains=q) | Q(answer__icontains=q))
    if category:
        faqs = faqs.filter(category=category)
    return render(request, 'chatbot/faq_list.html', {
        'faqs': faqs,
        'category_choices': FAQItem.CATEGORY_CHOICES,
        'page_title': 'Câu hỏi thường gặp',
    })


def chatbot_stats(request):
    from django.contrib.auth.decorators import login_required
    today = timezone.now().date()
    stats = {
        'total_sessions': ChatSession.objects.count(),
        'today_messages': ChatMessage.objects.filter(created_at__date=today).count(),
        'avg_rating': ChatSession.objects.filter(rating__isnull=False).aggregate(avg=Avg('rating'))['avg'],
        'understood_rate': _get_understood_rate(),
        'popular_faqs': FAQItem.objects.filter(is_active=True).order_by('-view_count')[:5],
        'top_categories': list(ChatMessage.objects.values('topic').annotate(c=Count('id')).order_by('-c')[:5]),
    }
    return render(request, 'chatbot/stats.html', {'stats': stats, 'page_title': 'Thống kê chatbot'})


def _find_answer(message):
    """Tìm câu trả lời đơn giản từ FAQ và rules cứng."""
    msg_lower = message.lower()

    # Tìm trong FAQ
    faqs = FAQItem.objects.filter(is_active=True)
    for faq in faqs:
        keywords = [k.strip().lower() for k in faq.keywords.split(',') if k.strip()]
        if any(kw in msg_lower for kw in keywords):
            faq.view_count += 1
            faq.save(update_fields=['view_count'])
            return faq.answer, True

    # Rules cứng cơ bản
    if any(w in msg_lower for w in ['phản ánh', 'báo cáo', 'sự cố', 'hỏng']):
        return ('Để gửi phản ánh sự cố, bạn vào mục "Bảo trì" > "Gửi phản ánh". '
                'Điền đầy đủ thông tin và đính kèm ảnh để được xử lý nhanh hơn.'), True
    if any(w in msg_lower for w in ['ngập', 'lụt', 'nước']):
        return ('Thông tin ngập lụt và cảnh báo thiên tai có tại mục "Ngập lụt". '
                'Bạn cũng có thể xem bản đồ ngập lụt để biết khu vực ảnh hưởng.'), True
    if any(w in msg_lower for w in ['đăng kiểm', 'xe', 'phương tiện']):
        return ('Dịch vụ đăng kiểm phương tiện có tại mục "Đăng kiểm". '
                'Bạn có thể đặt lịch, theo dõi trạng thái và nhận nhắc nhở hết hạn.'), True
    if any(w in msg_lower for w in ['giấy phép', 'thi công', 'xây dựng']):
        return ('Để xin giấy phép thi công, truy cập mục "Giấy phép thi công" > "Tạo hồ sơ mới". '
                'Bạn cần đính kèm đủ tài liệu kỹ thuật và pháp lý.'), True
    if any(w in msg_lower for w in ['xin chào', 'hello', 'hi', 'chào']):
        return 'Xin chào! Tôi là trợ lý ảo hệ thống hạ tầng đô thị. Tôi có thể giúp gì cho bạn?', True

    return ('Xin lỗi, tôi chưa hiểu câu hỏi của bạn. Bạn có thể hỏi về: '
            'phản ánh sự cố, ngập lụt, đăng kiểm xe, giấy phép thi công, '
            'hoặc xem danh sách câu hỏi thường gặp.'), False


def _get_suggestions(message):
    msg_lower = message.lower()
    suggestions = []
    if 'đường' in msg_lower or 'hạ tầng' in msg_lower:
        suggestions = ['Xem danh sách tuyến đường', 'Báo cáo hư hỏng', 'Kiểm tra trạng thái đường']
    elif 'ngập' in msg_lower or 'lụt' in msg_lower:
        suggestions = ['Xem bản đồ ngập lụt', 'Hướng dẫn di tản', 'Tìm nơi trú ẩn']
    else:
        suggestions = ['Gửi phản ánh sự cố', 'Xem cảnh báo thiên tai', 'Hướng dẫn sử dụng']
    return suggestions


def _get_understood_rate():
    total = ChatMessage.objects.filter(role='bot').count()
    if not total:
        return 0
    understood = ChatMessage.objects.filter(role='bot', was_understood=True).count()
    return round(understood / total * 100, 1)
