from am.models import AnaExecute, WeeklyReport
from import_export import resources, fields


class AnaExecuteResource(resources.ModelResource):
    """The import_export resource class for model AnaSubmit"""
    class Meta:
        model = AnaExecute
        skip_unchanged = True
        fields = (
            "ana_submit", "analyst", "notes", "end_date", "baidu_link",
            "is_submit"
        )
        export_order = (
            "ana_submit", "analyst", "notes", "end_date", "baidu_link",
            "is_submit"
        )

    def get_export_headers(self):
        return [
            "分析子项目编号", "分析员", "备注", "实际结束日期", "分析确认单",
            "分析结果路径", "结果百度链接"
        ]


class WeeklyReportResource(resources.ModelResource):
    """The import_export resource class for model WeeklyReport"""
    id = fields.Field(attribute="id", column_name="样品编号", default=None)
    reporter = fields.Field(attribute="reporter_id", column_name="汇报人")
    start_date = fields.Field(attribute="start_date", column_name="起始日期")
    end_date = fields.Field(attribute="end_date", column_name="截止日期")
    content = fields.Field(attribute="content", column_name="汇报内容")
    
    class Meta:
        model = WeeklyReport
        skip_unchanged = True
        fields = ("id", "reporter", "start_date", "end_date", "content")
        export_order = ("id", "reporter", "start_date", "end_date", "content")
    
    def get_export_headers(self):
        return ["样品编号", "汇报人", "起始日期", "截止日期", "汇报内容"]


