from am.models import AnaExecute, WeeklyReport, ProjectTask, DevelopmentTask, \
    OtherTask
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


class ProjectTaskResource(resources.ModelResource):
    """The import_export resource class for model ProjectTask"""
    id = fields.Field(attribute="id", column_name="项目任务编号", default=None)
    contract = fields.Field(
        column_name='合同号', attribute='contract', default=None
    )
    product_name = fields.Field(
        column_name='产品名称', attribute='product_name', default=None
    )
    category = fields.Field(
        column_name='类别', attribute='category', default=None
    )
    type = fields.Field(
        column_name='项目类型', attribute='type', default=None
    )
    project_name = fields.Field(
        column_name='项目名称', attribute='project_name', default=None
    )
    analysis_type = fields.Field(
        column_name='分析类别', attribute='analysis_type', default=None
    )
    begin_time = fields.Field(
        column_name='开始时间', attribute='begin_time', default=None
    )
    finish_time = fields.Field(
        column_name='结束时间', attribute='finish_time', default=None
    )
    is_finish = fields.Field(
        column_name='完成情况', attribute='is_finish', default=None
    )
    comparison_scheme = fields.Field(
        column_name='比较方案', attribute='comparison_scheme', default=None
    )
    sample_number = fields.Field(
        column_name='样品数量', attribute='sample_number', default=None
    )
    data_path = fields.Field(
        column_name='数据分析路径', attribute='data_path', default=None
    )
    pan_path = fields.Field(
        column_name='百度网盘路径', attribute='pan_path', default=None
    )
    analyst = fields.Field(
        column_name='分析员', attribute='analyst', default=None
    )
    review_user = fields.Field(
        column_name='复核人员', attribute='review_user', default=None
    )
    after_sales = fields.Field(
        column_name='售后分析内容', attribute='after_sales', default=None
    )
    history_date = fields.Field(
        column_name='历史填写日期', attribute='history_date', default=None
    )
    write_date = fields.Field(
        column_name='填写日期', attribute='write_date', default=None
    )
    note = fields.Field(
        column_name='备注', attribute='note', default=None
    )

    class Meta:
        model = ProjectTask
        skip_unchanged = True
        fields = ("id", "contract", "product_name", "category", "type",
                  "project_name", "analysis_type", "begin_time", "finish_time",
                  "is_finish", "comparison_scheme", "sample_number",
                  "data_path", "pan_path", "analyst", "review_user",
                  "after_sales", "history_date", "write_date", "note"
                  )
        export_order = ("id", "contract", "product_name", "category", "type",
                        "project_name", "analysis_type", "begin_time",
                        "finish_time",
                        "is_finish", "comparison_scheme", "sample_number",
                        "data_path", "pan_path", "analyst", "review_user",
                        "after_sales", "history_date", "write_date", "note"
                        )


class DevelopmentTaskResource(resources.ModelResource):
    """The import_export resource class for model DevelopmentTask"""
    id = fields.Field(attribute="id", column_name="开发任务编号", default=None)
    product_name = fields.Field(
        column_name='产品名称', attribute='product_name', default=None
    )
    rd_tasks = fields.Field(
        column_name='研发任务', attribute='rd_tasks', default=None
    )
    cycle = fields.Field(
        column_name='周期', attribute='cycle', default=None
    )
    test_path = fields.Field(
        column_name='测试路径', attribute='test_path', default=None
    )
    finish_time = fields.Field(
        column_name='完成时间', attribute='finish_time', default=None
    )
    finish_status = fields.Field(
        column_name='完成情况简述', attribute='finish_status', default=None
    )
    note = fields.Field(
        column_name='备注', attribute='note', default=None
    )
    is_finish = fields.Field(
        column_name='完成情况', attribute='is_finish', default=None
    )
    writer = fields.Field(
        column_name='填写人', attribute='writer', default=None
    )

    class Meta:
        model = DevelopmentTask
        skip_unchanged = True
        fields = ("id", "product_na me", "rd_tasks", "cycle", "test_path",
                  "finish_time", "finish_status", "note", "is_finish",
                  "writer"
                  )
        export_order = ("id", "product_name", "rd_tasks", "cycle", "test_path",
                        "finish_time", "finish_status", "note", "is_finish",
                        "writer"
                        )


class OtherTaskResource(resources.ModelResource):
    """The import_export resource class for model OtherTask"""
    id = fields.Field(attribute="id", column_name="开发任务编号", default=None)
    task_detail = fields.Field(
        column_name='任务内容', attribute='task_detail', default=None
    )
    start_time = fields.Field(
        column_name='开始时间', attribute='start_time', default=None
    )
    end_time = fields.Field(
        column_name='结束时间', attribute='end_time', default=None
    )
    finish_status = fields.Field(
        column_name='完成情况简述', attribute='finish_status', default=None
    )
    note = fields.Field(
        column_name='备注', attribute='note', default=None
    )
    is_finish = fields.Field(
        column_name='完成情况', attribute='is_finish', default=None
    )
    user_in_charge = fields.Field(
        column_name='负责人', attribute='user_in_charge', default=None
    )
    writer = fields.Field(
        column_name='填写人', attribute='writer', default=None
    )

    class Meta:
        model = OtherTask
        skip_unchanged = True
        fields = ("id", "task_detail", "start_time", "end_time",
                  "finish_status", "note", "is_finish", "user_in_charge",
                  "writer"
                  )
        export_order = ("id", "task_detail", "start_time", "end_time",
                        "finish_status", "note", "is_finish", "user_in_charge",
                        "writer"
                        )
