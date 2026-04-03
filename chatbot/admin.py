from django.contrib import admin
from .models import ChatSession, ChatMessage, FAQItem


class ChatMessageInline(admin.TabularInline):
    model = ChatMessage
    extra = 0
    readonly_fields = ['created_at']


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ['session_id', 'user', 'rating', 'started_at']
    inlines = [ChatMessageInline]


@admin.register(FAQItem)
class FAQItemAdmin(admin.ModelAdmin):
    list_display = ['question', 'category', 'view_count', 'is_active']
    list_filter = ['category', 'is_active']
    search_fields = ['question', 'keywords']
