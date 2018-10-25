from django.contrib import admin
from BMS.admin_bms import BMS_admin_site
from pm.models import SubProject


class admin1(admin.ModelAdmin):
    fields = ("sample_types","pro_type")

    def pro_type(self, obj):
        return obj.sample_types.project_type

BMS_admin_site.register(SubProject,admin1)