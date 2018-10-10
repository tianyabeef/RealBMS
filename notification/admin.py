from django.contrib import admin

from BMS.admin_bms import BMS_admin_site
from .models import Notification


class NotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'actor',
                    'level', 'target', 'unread', 'public')
    list_filter = ('level', 'unread', 'public', 'timestamp', )

BMS_admin_site.register(Notification, NotificationAdmin)

# Register your models here.
