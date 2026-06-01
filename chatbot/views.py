from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Avg
from datetime import date
import json, uuid
from .models import ChatSession, ChatMessage, FAQ

@login_required
def chatbot_page(request):
    return render(request, 'chatbot/chat.html', {'page_title': 'Hỗ trợ chatbot'})

@csrf_exempt
def chat_api(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    data = json.loads(request.body)
    session_id = data.get('session_id') or str(uuid.uuid4())
    message = data.get('message', '').strip()
    
    if not message:
        return JsonResponse({'error': 'Empty message'}, status=400)

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
    data = [{'id': f.id, 'question': f.question, 'category': f.category} for f in faqs]
    return JsonResponse({'questions': data})

def chat_stats(request):
    if not request.user.is_staff:
        return JsonResponse({'error': 'Forbidden'}, status=403)
    
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
    
    # 1. Kiểm tra Database FAQ trước tiên
    for faq in faqs:
        keywords = [k.strip().lower() for k in faq.keywords.split(',') if k.strip()]
        if any(kw in msg_lower for kw in keywords) or faq.question.lower() in msg_lower:
            faq.view_count += 1
            faq.save(update_fields=['view_count'])
            return faq.answer, True

    # 2. Xử lý các câu hỏi thường gặp (Rule-based)
    
    # Giao tiếp cơ bản
    if any(w in msg_lower for w in ['xin chào', 'hello', 'hi', 'chào']):
        return 'Xin chào! Tôi là trợ lý ảo của Hệ thống Quản lý Hạ tầng Đô thị. Tôi có thể giúp bạn tra cứu thông tin ngập lụt, báo cáo ổ gà, hỏng đèn đường hoặc thủ tục cấp phép.', True
    
    if any(w in msg_lower for w in ['cảm ơn', 'thanks', 'thank you']):
        return 'Không có chi! Nếu bạn cần hỗ trợ thêm gì, cứ nhắn cho tôi nhé.', True
        
    if any(w in msg_lower for w in ['tạm biệt', 'bye', 'hẹn gặp lại']):
        return 'Tạm biệt bạn! Chúc bạn một ngày tốt lành.', True

    # Nhóm: Đường sá, Mặt đường, Ổ gà
    if any(w in msg_lower for w in ['ổ gà', 'nứt đường', 'sụt lún', 'mặt đường']):
        return 'Để báo cáo ổ gà hoặc mặt đường xuống cấp, bạn hãy vào mục "Bảo trì > Gửi phản ánh". Nếu có ảnh chụp đính kèm, hệ thống AI của chúng tôi sẽ tự động nhận diện mức độ nghiêm trọng.', True

    # Nhóm: Đèn chiếu sáng, Đèn giao thông
    if any(w in msg_lower for w in ['đèn', 'chiếu sáng', 'tối', 'tắt', 'hỏng đèn']):
        return 'Nếu phát hiện đèn giao thông hoặc đèn đường IoT bị hỏng/tắt, vui lòng gửi phản ánh tại mục "Bảo trì". Chúng tôi sẽ điều phối đơn vị quản lý khu vực đến kiểm tra ngay.', True

    # Nhóm: Cây xanh đô thị
    if any(w in msg_lower for w in ['cây xanh', 'cắt tỉa', 'cây đổ', 'cây ngã']):
        return 'Về vấn đề cây xanh đô thị (cần cắt tỉa trước mùa mưa bão hoặc cây gãy đổ), bạn có thể gửi yêu cầu hỗ trợ qua mục "Gửi phản ánh" để công ty Công viên Cây xanh xử lý.', True

    # Nhóm: Ngập lụt, Mưa bão
    if any(w in msg_lower for w in ['ngập', 'lũ', 'bão', 'thoát nước', 'cống']):
        return 'Bạn có thể xem bản đồ các điểm đen ngập úng tại mục "Cảnh báo ngập lụt". Hệ thống cống thoát nước đang được theo dõi liên tục. Nếu khẩn cấp, hãy gọi số hotline cứu hộ 113 hoặc 114.', True

    # Nhóm: Đăng kiểm
    if any(w in msg_lower for w in ['đăng kiểm', 'phương tiện', 'ô tô', 'xe tải']):
        return 'Bạn có thể tra cứu lịch sử kiểm định hoặc đặt lịch hẹn đăng kiểm mới tại mục "Dịch vụ công > Đăng kiểm xe".', True

    # Nhóm: Giấy phép xây dựng/thi công
    if any(w in msg_lower for w in ['giấy phép', 'thi công', 'xây dựng', 'cấp phép', 'hồ sơ']):
        return 'Để xin giấy phép thi công, bạn cần nộp hồ sơ tại mục "Giấy phép thi công". Cán bộ sở sẽ tiếp nhận, yêu cầu bổ sung hoặc phê duyệt trực tiếp trên hệ thống.', True

    # Nhóm: Khảo sát, Đánh giá
    if any(w in msg_lower for w in ['khảo sát', 'đánh giá', 'ý kiến', 'góp ý']):
        return 'Chúng tôi rất trân trọng ý kiến của bạn. Mời bạn tham gia các biểu mẫu đánh giá chất lượng tại mục "Báo cáo > Khảo sát".', True
        
    # Nhóm: Bản đồ
    if any(w in msg_lower for w in ['bản đồ', 'vị trí', 'bản đồ hạ tầng']):
        return 'Toàn bộ dữ liệu tuyến đường, đèn giao thông và các công trình cầu hầm đều được trực quan hóa tại mục "Bản đồ".', True

    # 3. Fallback (Không hiểu)
    return 'Xin lỗi, tôi chưa hiểu ý bạn. Bạn có thể diễn đạt lại hoặc hỏi về các chủ đề: gửi phản ánh (ổ gà, đèn đường, cây xanh), đăng kiểm xe, xin giấy phép, hoặc xem cảnh báo ngập lụt không?', False