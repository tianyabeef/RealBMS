from django.contrib import admin
from em.models import Lv1Departments, Lv2Departments, Employees
from BMS.admin_bms import BMS_admin_site


class Lv1DepartmentsAdmin(admin.ModelAdmin):
    autocomplete_fields = ("manager", )
    list_per_page = 30
    list_display = (
        "name", "manager", "created_at", "is_valid",
    )
    list_display_links = ("name", )
    search_fields = ("name", "manager__username", )
    list_filter = ("is_valid", )
    fields = (
        "name", "manager", "is_valid",
    )

    def get_readonly_fields(self, request, obj=None):
        self.readonly_fields = (
            "name", "manager", "is_valid",
        ) if not request.user.is_superuser else ()
        return self.readonly_fields


class Lv2DepartmentsAdmin(admin.ModelAdmin):
    autocomplete_fields = ("manager", "superior")
    list_per_page = 30
    list_display = (
        "name", "superior", "manager", "created_at", "is_valid",
    )
    list_display_links = ("name", )
    search_fields = ("name", "manager", )
    list_filter = ("is_valid", )
    fields = (
        "name", "superior", "manager", "is_valid",
    )

    def get_readonly_fields(self, request, obj=None):
        self.readonly_fields = (
            "name", "superior", "manager", "is_valid",
        ) if not request.user.is_superuser else ()
        return self.readonly_fields


class EmployeesAdmin(admin.ModelAdmin):
    autocomplete_fields = ("user", "department",)
    list_per_page = 30
    list_display = (
        "dingtalk_name", "user", "dingtalk_id", "is_on_job", "department",
        "submit_date",
    )
    list_display_links = ("dingtalk_name", )
    search_fields = ("dingtalk_id", "dingtalk_name", "user__username", )
    list_filter = ("is_on_job", "department", )
    fields = (
        "user", "department", "dingtalk_name", "dingtalk_id", "is_on_job",
    )
    
    def get_readonly_fields(self, request, obj=None):
        self.readonly_fields = (
            "dingtalk_name", "dingtalk_id", "is_on_job", "department", "user",
            "submit_date",
        ) if not request.user.is_superuser else ()
        return self.readonly_fields


BMS_admin_site.register(Lv1Departments, Lv1DepartmentsAdmin)
BMS_admin_site.register(Lv2Departments, Lv2DepartmentsAdmin)
BMS_admin_site.register(Employees, EmployeesAdmin)
