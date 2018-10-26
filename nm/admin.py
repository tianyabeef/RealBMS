from django.contrib import admin
from nm.models import DingtalkChat, ChatTemplates
from BMS.admin_bms import BMS_admin_site


class DingtalkChatAdmin(admin.ModelAdmin):
    list_per_page = 30
    list_display = (
        "chat_id", "chat_name", "chat_owner", "create_at", "is_valid"
    )
    list_display_links = ("chat_name", )
    filter_horizontal = ("members", )
    raw_id_fields = ("chat_owner", )
    search_fields = ("chat_id", "chat_name", )
    list_filter = ("is_valid", )


class ChatTemplatesAdmin(admin.ModelAdmin):
    list_per_page = 30
    list_display = (
        "name", "sign", "text", "link", "create_at", "is_valid"
    )
    list_display_links = ("name", )
    search_fields = ("name", "sign", "text", )
    list_filter = ("is_valid", "sign")
    


BMS_admin_site.register(ChatTemplates, ChatTemplatesAdmin)
BMS_admin_site.register(DingtalkChat, DingtalkChatAdmin)
