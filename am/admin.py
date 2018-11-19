from am.forms import AnaExecuteModelForm, WeeklyReportModelForm
from am.models import AnaExecute, WeeklyReport
from am.resources import AnaExecuteResource, WeeklyReportResource
from am.views import AnaAutocompleteJsonView
from django.contrib.auth.models import Group, User
from django.contrib.auth.admin import UserAdmin
from django.utils import timezone
from django.utils.html import format_html
from import_export.admin import ImportExportModelAdmin
from BMS.admin_bms import BMS_admin_site
from BMS.notice_mixin import NotificationMixin
from BMS.settings import DINGTALK_APPKEY, DINGTALK_SECRET, DINGTALK_AGENT_ID


class UserForAutocompleteAdmin(UserAdmin):
    """User define user admin for the queryset filtration"""
    
    def autocomplete_view(self, request):
        return AnaAutocompleteJsonView.as_view(model_admin=self)(request)


BMS_admin_site.unregister(User)
BMS_admin_site.register(User, UserForAutocompleteAdmin)


class AnaExecuteAdmin(ImportExportModelAdmin, NotificationMixin):
    appkey = DINGTALK_APPKEY
    appsecret = DINGTALK_SECRET
    autocomplete_fields = ("analyst", )
    change_list_template = "admin/am/change_list_am.html"
    fields = (
        "ana_submit", "analyst", "end_date", "baidu_link", "is_submit", "notes"
    )
    form = AnaExecuteModelForm
    list_per_page = 30
    list_display = (
        "ana_submit", "analyst", "notes", "end_date", "confirmation_sheet",
        "depart_data_path", "baidu_link", "is_submit"
    )
    list_display_links = ('ana_submit', )
    list_filter = ("is_submit", )
    resource_class = AnaExecuteResource
    save_as_continue = False
    search_fields = ("analyst__username", "ana_submit__ana_number", )

    def depart_data_path(self, obj):
        return obj.ana_submit.depart_data_path
    depart_data_path.short_description = '数据分析路径'
    
    def confirmation_sheet(self, obj):
        field = obj.ana_submit.confirmation_sheet
        html = "<a href='%s'>下载</a>" % field.url if field else "未上传"
        return format_html(html)
    confirmation_sheet.short_description = '分析确认单'
    
    def get_actions(self, request):
        actions = super().get_actions(request)
        if not request.user.is_superuser and "delete_selected" in actions:
            actions.pop("delete_selected")
        return actions
    
    def get_readonly_fields(self, request, obj=None):
        self.readonly_fields = (
            "ana_submit", "analyst", "end_date", "baidu_link", "is_submit",
            "notes",
        ) if obj and obj.is_submit else ("ana_submit", )
        return self.readonly_fields
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        manager_qs = User.objects.filter(groups__id=10)
        current_qs = User.objects.filter(pk=request.user.pk)
        if not request.user.is_superuser and not current_qs & manager_qs:
            queryset = queryset.filter(analyst=request.user)
        return queryset
        
    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name == "ana_submit":
            kwargs["queryset"] = AnaExecute.objects.filter(
                ana_submit__subProject__is_status=11
            )
        elif db_field.name == "analyst":
            analyst_group = Group.objects.get(id=9)
            kwargs["queryset"] = analyst_group.user_set.all()
        return super().formfield_for_dbfield(db_field, request, **kwargs)
    
    def get_changeform_initial_data(self, request):
        initial = super().get_changeform_initial_data(request)
        initial["analyst"] = request.user
        return initial
    
    def render_change_form(self, request, context, add=False, change=False,
                           form_url='', obj=None):
        initial = context["adminform"].form.initial
        initial["analyst"] = initial.get("analyst", request.user)
        if obj and obj.is_submit:
            context['show_save'] = False
            context['show_delete'] = False
            context['show_save_and_continue'] = False
        return super().render_change_form(
            request, context, add=add, change=change, form_url=form_url,
            obj=obj
        )

    def save_model(self, request, obj, form, change):
        super(AnaExecuteAdmin, self).save_model(request, obj, form, change)
        ana_number = obj.ana_submit.ana_number
        ana_execute = AnaExecute.objects.get(ana_submit__ana_number=ana_number)
        ana_submit = ana_execute.ana_submit
        if obj and obj.is_submit:
            ana_submit.subProject.all().update(
                is_status=13, time_ana=obj.end_date
            )
            name_list = [n.sub_project for n in ana_submit.subProject.all()]
            content = "项目【%s】状态已变更为【完成】" % "，".join(name_list)
            self.send_work_notice(content, DINGTALK_AGENT_ID, "03561038053843")
            call_back = self.send_dingtalk_result
            message = "已钉钉通知项目管理进度" if call_back else "钉钉通知失败"
            self.message_user(request, message)
        else:
            ana_submit.subProject.all().update(is_status=12)
            self.message_user(request, "项目状态已变更为【分析中】，请及时跟进")
    

class WeeklyReportAdmin(ImportExportModelAdmin, NotificationMixin):
    appkey = DINGTALK_APPKEY
    appsecret = DINGTALK_SECRET
    autocomplete_fields = ("reporter", )
    form = WeeklyReportModelForm
    resource_class = WeeklyReportResource
    list_per_page = 30
    save_as_continue = False
    save_on_top = False
    list_display = (
        "reporter", "start_date", "end_date", "content", "attachment",
        "is_submit",
    )
    list_display_links = ('reporter', )
    list_filter = ("is_submit", "start_date", "end_date", )
    
    def get_readonly_fields(self, request, obj=None):
        self.readonly_fields = (
            "reporter", "start_date", "end_date", "content", "attachment",
            "is_submit"
        ) if obj and obj.is_submit else ()
        return self.readonly_fields

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        manager_qs = User.objects.filter(groups__id=10)
        current_qs = User.objects.filter(pk=request.user.pk)
        if not request.user.is_superuser and not current_qs & manager_qs:
            queryset = queryset.filter(reporter=request.user)
        return queryset

    def get_changeform_initial_data(self, request):
        initial = super().get_changeform_initial_data(request)
        initial["reporter"] = request.user.id
        initial["content"] = "【1】\n【2】\n"
        initial["start_date"] = timezone.now()
        return initial

    def render_change_form(self, request, context, add=False, change=False,
                           form_url='', obj=None):
        initial = context["adminform"].form.initial
        initial["reporter"] = initial.get("reporter", request.user)
        initial["content"] = initial.get("content", "【1】\n【2】\n")
        if obj and obj.is_submit:
            context['show_save'] = False
            context['show_delete'] = False
            context['show_save_and_continue'] = False
        return super().render_change_form(
            request, context, add=add, change=change, form_url=form_url,
            obj=obj
        )
        
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if obj and obj.is_submit:
            content = "【%s】周报已提交" % request.user.username
            self.send_work_notice(content, DINGTALK_AGENT_ID, "03561038053843")
            call_back = self.send_dingtalk_result
            message = "已钉钉通知项目部门总监" if call_back else "钉钉通知失败"
            self.message_user(request, message)
        else:
            self.message_user(request, "周报记录已保存，请及时跟进")


BMS_admin_site.register(AnaExecute, AnaExecuteAdmin)
BMS_admin_site.register(WeeklyReport, WeeklyReportAdmin)
