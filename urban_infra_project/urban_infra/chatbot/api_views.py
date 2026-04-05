from rest_framework.decorators import api_view, permission_classes
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework import generics
from .models import FAQ, ChatSession, ChatMessage
from .serializers import FAQSerializer, ChatSessionSerializer


class FAQListAPIView(generics.ListAPIView):
    queryset = FAQ.objects.filter(is_active=True).order_by('-view_count')
    serializer_class = FAQSerializer
    permission_classes = [permissions.AllowAny]


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def chat_message_api(request):
    import uuid
    session_id = request.data.get('session_id') or str(uuid.uuid4())
    message = request.data.get('message', '').strip()
    if not message:
        return Response({'error': 'Empty message'}, status=status.HTTP_400_BAD_REQUEST)

    session, _ = ChatSession.objects.get_or_create(
        session_id=session_id,
        defaults={'user': request.user if request.user.is_authenticated else None}
    )
    ChatMessage.objects.create(session=session, sender='user', content=message)

    # Import reply logic from views
    from .views import _get_bot_reply
    reply, understood = _get_bot_reply(message)
    ChatMessage.objects.create(session=session, sender='bot', content=reply, is_understood=understood)

    return Response({
        'reply': reply,
        'session_id': session_id,
        'understood': understood,
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def chatbot_stats_api(request):
    from django.db.models import Count, Avg
    if not request.user.is_staff:
        return Response({'error': 'Forbidden'}, status=403)
    from django.utils import timezone
    today = timezone.now().date()
    stats = {
        'today_sessions': ChatSession.objects.filter(started_at__date=today).count(),
        'total_sessions': ChatSession.objects.count(),
        'total_messages': ChatMessage.objects.count(),
        'understood_rate': ChatMessage.objects.filter(sender='bot').aggregate(
            rate=Avg('is_understood'))['rate'],
        'top_faqs': list(FAQ.objects.filter(is_active=True).order_by('-view_count')
                         .values('question', 'category', 'view_count')[:5]),
        'popular_categories': list(
            FAQ.objects.values('category').annotate(c=Count('id')).order_by('-c')[:5]),
    }
    return Response(stats)
