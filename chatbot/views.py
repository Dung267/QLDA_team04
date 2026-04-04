from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Count
import json, uuid
from .models import ChatSession, ChatMessage, FAQ

@login_required
def chatbot_page(request):
    return render(request,'chatbot/chat.html',{'page_title':'Hỗ trợ chatbot'})

@csrf_exempt
def chat_api(request):
    if request.method != 'POST':
        return JsonResponse({'error':'Method not allowed'},status=405)
    data = json.loads(request.body)
    session_id = data.get('session_id') or str(uuid.uuid4())
    message = data.get('message','').strip()
    if not message:
        return JsonResponse({'error':'Empty message'},status=400)

    session, _ = ChatSession.objects.get_or_create(
        session_id=session_id,
        defaults={'user': request.user if request.user.is_authenticated else None}
    )
    ChatMessage.objects.create(session=session, sender='user', content=message)

    reply, understood = _get_bot_reply(message)
    ChatMessage.objects.create(session=session, sender='bot', content=reply, is_understood=understood)

    return JsonResponse({'reply': reply, 'session_id': session_id, 'understood': understood})

def popular_questions(request):
    faqs = FAQ.objects.filter(is_active=True).order_by('-view_count')[:10]
    data = [{'id':f.id,'question':f.question,'category':f.category} for f in faqs]
    return JsonResponse({'questions': data})

def chat_stats(request):
    from django.db.models import Count, Avg
    if not request.user.is_staff:
        return JsonResponse({'error':'Forbidden'},status=403)
    from datetime import date, timedelta
    today = date.today()
    stats = {
        'today_sessions': ChatSession.objects.filter(started_at__date=today).count(),
        'total_sessions': ChatSession.objects.count(),
        'understood_rate': ChatMessage.objects.filter(sender='bot').aggregate(
            rate=Avg('is_understood'))['rate'],
        'popular_categories': list(FAQ.objects.values('category').annotate(c=Count('id')).order_by('-c')[:5]),
    }
    return JsonResponse(stats)

def _get_bot_reply(msg):
    msg_lower = msg.lower()
    faqs = FAQ.objects.filter(is_active=True)
    for faq in faqs:
        keywords = [k.strip().lower() for k in faq.keywords.split(',') if k.strip()]
        if any(kw in msg_lower for kw in keywords) or faq.question.lower() in msg_lower:
            faq.view_count += 1
            faq.save(update_fields=['view_count'])
            return faq.answer, True

    # Simple rule-based replies
    if any(w in msg_lower for w in ['phản ánh','báo cáo','sự cố']):
        return 'Để gửi phản ánh, bạn vào mục "Bảo trì > Gửi phản ánh" và điền đầy đủ thông tin. Chúng tôi sẽ xử lý trong 24-48 giờ.', True
    if any(w in msg_lower for w in ['ngập','lũ','bão']):
        return 'Thông tin cảnh báo ngập lụt có tại mục "Cảnh báo ngập lụt". Nếu khẩn cấp hãy gọi 113.', True
    if any(w in msg_lower for w in ['đăng kiểm','phương tiện']):
        return 'Để đặt lịch đăng kiểm, vào mục "Đăng kiểm phương tiện > Đặt lịch".', True
    if any(w in msg_lower for w in ['giấy phép','thi công']):
        return 'Thủ tục xin giấy phép thi công có tại mục "Giấy phép thi công". Bạn cần tạo hồ sơ và đính kèm tài liệu.', True
    if any(w in msg_lower for w in ['xin chào','hello','hi','chào']):
        return 'Xin chào! Tôi là trợ lý của Hệ thống Quản lý Hạ tầng Đô thị. Tôi có thể giúp bạn gửi phản ánh, tra cứu thông tin và hướng dẫn sử dụng hệ thống.', True
    return 'Xin lỗi, tôi chưa hiểu câu hỏi của bạn. Bạn có thể hỏi về: gửi phản ánh, đăng kiểm xe, giấy phép thi công, cảnh báo ngập lụt.', False
