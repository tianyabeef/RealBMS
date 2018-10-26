from django.contrib import admin
from em.models import Lv1Departments, Lv2Departments, Employees
from BMS.admin_bms import BMS_admin_site


class Lv1DepartmentsAdmin(admin.ModelAdmin):
    list_per_page = 30
    list_display = (
        "name", "manager", "created_at", "is_valid",
    )
    list_display_links = ("name", )
    raw_id_fields = ("manager", )
    search_fields = ("name", "manager", )
    list_filter = ("is_valid", )


class Lv2DepartmentsAdmin(admin.ModelAdmin):
    list_per_page = 30
    list_display = (
        "name", "superior", "manager", "created_at", "is_valid",
    )
    list_display_links = ("name", )
    raw_id_fields = ("manager", "superior")
    search_fields = ("name", "manager", )
    list_filter = ("is_valid", )


class EmployeesAdmin(admin.ModelAdmin):
    list_per_page = 30
    list_display = (
        "dingtalk_id", "dingtalk_name", "is_on_job", "department", "user",
        "submit_date",
    )
    list_display_links = ("dingtalk_id", )
    raw_id_fields = ("department", "user")
    search_fields = ("dingtalk_id", "dingtalk_name", "user", )
    list_filter = ("is_on_job", "department", )


BMS_admin_site.register(Lv1Departments, Lv1DepartmentsAdmin)
BMS_admin_site.register(Lv2Departments, Lv2DepartmentsAdmin)
BMS_admin_site.register(Employees, EmployeesAdmin)
