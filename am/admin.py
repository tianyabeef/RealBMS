from am.models import AnaExecute, WeeklyReport
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from BMS.admin_bms import BMS_admin_site


class AnaExecuteResource(resources.ModelResource):
    """The import_export resource class for model AnaSubmit"""
    class Meta:
        model = AnaExecute
        skip_unchanged = True
        fields = (
            "ana_submit", "analyst", "notes", "end_date", "confirmation_sheet",
            "ana_result_path", "baidu_link", "is_submit"
        )
        export_order = (
            "ana_submit", "analyst", "notes", "end_date", "confirmation_sheet",
            "ana_result_path", "baidu_link", "is_submit"
        )

    def get_export_headers(self):
        return [
            "分析子项目编号", "分析员", "备注", "实际结束日期", "分析确认单",
            "分析结果路径", "结果百度链接"
        ]


class AnaExecuteAdmin(ImportExportModelAdmin):
    resource_class = AnaExecuteResource
    list_per_page = 30
    save_as_continue = False
    save_on_top = False
    list_display = (
        "ana_submit", "analyst", "notes", "end_date", "confirmation_sheet",
        "ana_result_path", "baidu_link", "is_submit"
    )
    list_display_links = ('ana_submit',)

    def get_readonly_fields(self, request, obj=None):
        self.readonly_fields = (
            "ana_submit", "analyst", "end_date", "confirmation_sheet",
            "ana_result_path", "baidu_link", "is_submit"
        ) if obj and obj.is_submit else ()
        return self.readonly_fields
    
    def save_model(self, request, obj, form, change):
        super(AnaExecuteAdmin, self).save_model(request, obj, form, change)
        if obj.is_submit:
            # TODO: dingtalk request
            self.save_as = False
            pass


class WeeklyReportResource(resources.ModelResource):
    """The import_export resource class for model WeeklyReport"""
    class Meta:
        model = WeeklyReport
        skip_unchanged = True
        fields = ("reporter", "start_date", "end_date", "content")
        export_order = ("reporter", "start_date", "end_date", "content")

    def get_export_headers(self):
        return ["汇报人", "起始日期", "截止日期", "汇报内容"]


class WeeklyReportAdmin(ImportExportModelAdmin):
    resource_class = WeeklyReportResource
    list_per_page = 30
    save_as_continue = False
    save_on_top = False
    list_display = (
        "reporter", "start_date", "end_date", "content", "attachment",
        "is_submit",
    )
    list_display_links = ('reporter', )
    
    def get_readonly_fields(self, request, obj=None):
        self.readonly_fields = (
            "reporter", "start_date", "end_date", "content", "attachment",
            "is_submit"
        ) if obj and obj.is_submit else ()
        return self.readonly_fields
    
    def save_model(self, request, obj, form, change):
        super(WeeklyReportAdmin, self).save_model(request, obj, form, change)
        if obj.is_submit:
            # TODO: dingtalk request
            pass


BMS_admin_site.register(AnaExecute, AnaExecuteAdmin)
BMS_admin_site.register(WeeklyReport, WeeklyReportAdmin)
