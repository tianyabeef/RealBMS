from am.forms import AnaExecuteModelForm, WeeklyReportModelForm
from am.models import AnaExecute, WeeklyReport
from am.resources import AnaExecuteResource, WeeklyReportResource
from am.views import AnaAutocompleteJsonView
from django.contrib.auth.models import Group, User
from django.contrib.auth.admin import UserAdmin
from django.db.models import Q
from django.utils import timezone
from django.utils.html import format_html
from import_export.admin import ImportExportModelAdmin
from BMS.admin_bms import BMS_admin_site
from BMS.notice_mixin import NotificationMixin
from BMS.settings import DINGTALK_APPKEY, DINGTALK_SECRET, DINGTALK_AGENT_ID
from em.models import Employees
from nm.models import DingtalkChat


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
        "ana_submit", "analyst", "sample_count", "ana_start_date", "end_date",
        "depart_data_path", "baidu_link", "is_submit", "notes",
    )
    form = AnaExecuteModelForm
    list_per_page = 30
    list_display = (
        "ana_submit", "contract_name", "analyst", "notes",
        "end_date", "confirmation_sheet",  "baidu_link",
        "is_submit", "submit_date",
    )
    list_display_links = ('ana_submit', )
    list_filter = ("is_submit", )
    resource_class = AnaExecuteResource
    save_as_continue = False
    search_fields = ("analyst__username", "ana_submit__ana_number", )

    def depart_data_path(self, obj):
        return obj.ana_submit.depart_data_path if obj else None
    depart_data_path.short_description = '数据分析路径'

    def sample_count(self, obj):
        return obj.ana_submit.sample_count if obj else None
    sample_count.short_description = '样品数量'

    def ana_start_date(self, obj):
        return obj.ana_submit.ana_start_date if obj else None
    ana_start_date.short_description = '分析开始日期'

    def confirmation_sheet(self, obj):
        field = obj.ana_submit.confirmation_sheet
        html = "<a href='%s'>下载</a>" % field.url if field else "未上传"
        return format_html(html)
    confirmation_sheet.short_description = '分析确认单'
    
    def contract_name(self, obj):
        all_projects = obj.ana_submit.subProject.all()
        contracts = ', '.join(set(["%s" % n.contract for n in all_projects]))
        return contracts
    contract_name.short_description = '合同名称'
    
    def get_actions(self, request):
        actions = super().get_actions(request)
        if not request.user.is_superuser and "delete_selected" in actions:
            actions.pop("delete_selected")
        return actions
    
    def get_readonly_fields(self, request, obj=None):
        self.readonly_fields = (
            "ana_submit", "analyst", "end_date", "baidu_link", "is_submit",
            "notes", "depart_data_path", "sample_count", "ana_start_date"
        ) if obj and obj.is_submit else ("ana_submit", "depart_data_path",
                                         "sample_count", "ana_start_date")
        return self.readonly_fields
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        manager_qs = User.objects.filter(groups__id=10)
        current_qs = User.objects.filter(pk=request.user.pk)
        if not request.user.is_superuser and not current_qs & manager_qs:
            condition = Q(analyst=request.user) | Q(analyst=None)
            queryset = queryset.filter(condition)
        return queryset
        
    def get_changeform_initial_data(self, request):
        initial = super().get_changeform_initial_data(request)
        initial["analyst"] = request.user
        return initial
    
    def render_change_form(self, request, context, add=False, change=False,
                           form_url='', obj=None):
        initial = context["adminform"].form.initial
        if initial.get("analyst", None):
            analyst = initial.get("analyst")
        else:
            analyst = request.user
        initial["analyst"] = analyst
        if obj and obj.is_submit:
            context['show_save'] = False
            context['show_delete'] = False
            context['show_save_and_continue'] = False
        return super().render_change_form(
            request, context, add=add, change=change, form_url=form_url,
            obj=obj
        )
    
    @staticmethod
    def get_last_30_days_submit(queryset=None):
        count = []
        for index in range(30):
            interval = timezone.now() - timezone.timedelta(index)
            count.append(queryset.filter(submit_date=interval).count())
        count.reverse()
        return count
    
    @staticmethod
    def get_last_30_days_end(queryset=None):
        count = []
        for index in range(30):
            interval = timezone.now() - timezone.timedelta(index)
            count.append(queryset.filter(end_date=interval).count())
        count.reverse()
        return count
    
    @staticmethod
    def get_figure_label():
        figure_label = []
        for index in range(30):
            interval = timezone.now() - timezone.timedelta(index)
            figure_label.append(interval.strftime("%Y-%m-%d"))
        figure_label.reverse()
        return figure_label
    
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        queryset = self.get_queryset(request)
        last_30_days_submit = self.get_last_30_days_submit(queryset=queryset)
        last_30_days_end = self.get_last_30_days_end(queryset=queryset)
        extra_context["last_30_days_submit"] = last_30_days_submit
        extra_context["last_30_days_end"] = last_30_days_end
        extra_context["figure_label"] = self.get_figure_label()
        return super().changelist_view(request, extra_context=extra_context)
    
    def save_model(self, request, obj, form, change):
        super(AnaExecuteAdmin, self).save_model(request, obj, form, change)
        if obj and obj.is_submit:
            all_sub_project = obj.ana_submit.subProject.all()
            all_sub_project.update(is_status=13, time_ana=obj.end_date)
            name_list = set([n.sub_project for n in all_sub_project])
            content = "项目【%s】状态已变更为【完成】" % "，".join(name_list)
            dingdingid = DingtalkChat.objects.get(chat_name="项目管理钉钉群-BMS")
            dingdingid_ = DingtalkChat.objects.get(chat_name="生信分析钉钉群-BMS")
            send_to = [dingdingid, dingdingid_]
            self.send_work_notice(content, DINGTALK_AGENT_ID, send_to)
            call_back = self.send_dingtalk_result
            message = "已钉钉通知项目管理进度" if call_back else "钉钉通知失败"
            self.message_user(request, message)
        else:
            if change:
                all_sub_project = obj.ana_submit.subProject.all()
                all_sub_project.update(is_status=13, time_ana=obj.end_date)
                name_list = set([n.sub_project for n in all_sub_project])
                analyst = form.cleaned_data["analyst"]
                analyst_dingid = Employees.objects.get(dingtalk_name=analyst.username)
                content = "项目：{}待分析，请在BMS系统中查看详细信息，辛苦开展分析".format(name_list)
                self.send_work_notice(content, DINGTALK_AGENT_ID, analyst_dingid)
                call_back = self.send_dingtalk_result
                message = "已钉钉通知分析员{}".format(analyst.username) if call_back else "钉钉通知失败"
                self.message_user(request, message)
            obj.ana_submit.subProject.all().update(is_status=12)
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
            content = "{0}:{1}---{2}周报已提交".format(
                request.user.username, obj.start_date, obj.end_date
            )
            self.send_work_notice(content, DINGTALK_AGENT_ID, "03561038053843")
            call_back = self.send_dingtalk_result
            message = "已钉钉通知项目部门总监" if call_back else "钉钉通知失败"
            self.message_user(request, message)
        else:
            self.message_user(request, "周报记录已保存，请及时跟进")


BMS_admin_site.register(AnaExecute, AnaExecuteAdmin)
BMS_admin_site.register(WeeklyReport, WeeklyReportAdmin)
