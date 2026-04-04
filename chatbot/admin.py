from django.contrib import admin
from .models import FAQ, ChatSession

@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ['question','category','view_count','is_active']
    list_filter = ['category','is_active']
    search_fields = ['question','answer','keywords']

@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ['session_id','user','started_at','rating']
    list_filter = ['rating']
