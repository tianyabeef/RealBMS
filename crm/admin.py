from django.contrib import admin, messages
from django.utils.html import format_html
from django.contrib.auth.models import User

from docx_parsing_gmdzy2010.renderer import DocxProduce, ContextFields
from datetime import date

from BMS.admin_bms import BMS_admin_site
from BMS.settings import TEMPLATE_FROM_PATH, TEMPLATE_TO_PATH, TABLE_CONTEXT
from crm.models import Customer, Intention, IntentionRecord, Analyses, \
    ContractApplications
from crm.forms import IntentionForm, ContractApplicationsForm
from crm.clauses import clauses_decision


class CustomerAdmin(admin.ModelAdmin):
    """Admin class for customer"""
    list_display = (
        'name', 'organization', 'department', 'address', 'title', 'contact',
        'email', 'level'
    )
    ordering = ['name']
    list_filter = ['organization', 'level']
    search_fields = ['name', 'organization', 'contact']
    fieldsets = (
        (None, {
            'fields': (
                'name', ('organization', 'department'), 'address', 'title',
                'contact', 'email', 'level'
            )
        }),
    )

    def get_queryset(self, request):
        # 只允许管理员和拥有该模型删除权限的人员才能查看所有样品
        qs = super(CustomerAdmin, self).get_queryset(request)
        perm = 'crm.delete_customer'
        if request.user.is_superuser or request.user.has_perm(perm):
            return qs
        return qs.filter(linker=request.user)

    def save_model(self, request, obj, form, change):
        obj.linker = request.user
        obj.save()


class IntentionRecordInline(admin.StackedInline):
    model = IntentionRecord
    extra = 1
    exclude = ['record_date']

    def get_readonly_fields(self, request, obj=None):
        # 没有新增意向权限人员仅能查看信息
        if not request.user.has_perm('crm.add_intention'):
            return [f.name for f in self.model._meta.fields]
        return self.readonly_fields


class IntentionAdmin(admin.ModelAdmin):
    """Admin class for intention"""
    form = IntentionForm
    list_display = (
        'customer_organization', 'customer_name', 'project_name',
        'project_type', 'amount', 'closing_date', 'price', 'status'
    )
    list_filter = ['project_type', 'closing_date', 'amount']
    inlines = [
        IntentionRecordInline,
    ]
    fields = (
        'customer_organization', 'customer', 'project_name', 'project_type',
        'amount', 'price'
    )
    raw_id_fields = ('customer',)

    def get_list_display_links(self, request, list_display):
        # 没有新增意向权限人员，入口设置为状态，否则为项目名
        if not request.user.has_perm('crm.add_intention'):
            return ['status']
        return ['project_name']

    def customer_organization(self, obj):
        return obj.customer.organization
    customer_organization.short_description = '单位'

    def customer_name(self, obj):
        return obj.customer.name
    customer_name.short_description = '客户姓名'

    def status(self, obj):
        records = IntentionRecord.objects.filter(intention_id=obj.id)
        return records.last().status if records.last() else "无"
    status.short_description = '最新进展'

    def get_queryset(self, request):
        # 只允许管理员和拥有该模型删除权限的人员才能查看所有样品
        qs = super(IntentionAdmin, self).get_queryset(request)
        perm = 'crm.delete_intention'
        if request.user.is_superuser or request.user.has_perm(perm):
            return qs
        return qs.filter(customer__linker=request.user)

    def get_actions(self, request):
        # 无删除权限人员取消actions
        actions = super(IntentionAdmin, self).get_actions(request)
        if not request.user.has_perm('crm.delete_intention'):
            actions = None
        return actions

    def get_readonly_fields(self, request, obj=None):
        # 没有新增意向权限人员仅能查看信息
        if not request.user.has_perm('crm.add_intention'):
            return [
                'customer_organization', 'customer', 'project_name',
                'project_type', 'amount', 'closing_date', 'price'
            ]
        return ['customer_organization']

    def change_view(self, request, object_id, form_url='', extra_context=None):
        # 没有新增意向权限人员查看页面时隐藏所有按钮
        extra_context = extra_context or {}
        if not request.user.has_perm('crm.add_intention'):
            extra_context['show_save'] = False
            extra_context['show_save_as_new'] = False
            # extra_context['show_save_and_add_another'] = False
            extra_context['show_save_and_continue'] = False
        return super(IntentionAdmin, self).change_view(
            request, object_id, form_url, extra_context=extra_context
        )

    def save_formset(self, request, form, formset, change):
        # 历史记录禁止修改
        instances = formset.save(commit=False)
        for obj in formset.deleted_objects:
            obj.delete()
        if instances:
            for instance in instances:
                if instance.record_date < date.today():
                    msg = '%s 历史进展记录未被允许修改' % instance.record_date
                    self.message_user(request, msg, level=messages.WARNING)
                    continue
                instance.save()
            formset.save_m2m()


class AnalysesAdmin(admin.ModelAdmin):
    list_display = ('union_id', 'analysis_name', 'analysis_type')
    ordering = ['union_id']
    list_filter = ['analysis_type', ]
    radio_fields = {'analysis_type': admin.VERTICAL}
    search_fields = ['union_id', 'analysis_name', 'analysis_type']


class ContractApplicationsAdmin(admin.ModelAdmin):
    autocomplete_fields = ("second_party_contact", )
    form = ContractApplicationsForm
    list_display = (
        'second_party_contact', 'contract_name', 'project_type', 'pay_type',
        'first_party', 'second_party', 'total_price', 'signed_date',
        'contract_download',
    )
    ordering = ['signed_date']
    list_filter = ['project_type', 'pay_type', ]
    radio_fields = {
        'second_party': admin.VERTICAL,
        'project_type': admin.HORIZONTAL,
        'pay_type': admin.HORIZONTAL,
        'data_delivery_type': admin.VERTICAL,
    }
    search_fields = ['union_id', 'analysis_name', 'analysis_type']
    filter_horizontal = ('analyses_aa', 'analyses_pa', )
    fieldsets = (
        ("变更信息", {
            'fields': (
                'contract_name', 'project_type', 'pay_type',
                ('extract_sample_counts', 'sequence_sample_counts'),
                'total_price', 'sequence_single_price', 'sequence_total_price',
                'extract_total_price', 'sample_return_price',
                ('first_payment', 'final_payment'),
                'analyses_aa', 'analyses_pa', 'data_delivery_type',
                ('signed_date', 'valid_date')
            )
        }), ("甲方信息", {
            'fields': (
                'first_party', 'first_party_contact',
                'first_party_contact_phone', 'first_party_contact_email',
                'first_party_address',
            )
        }), ("其它信息", {
            'fields': (
                'second_party', 'second_party_contact',
                'second_party_contact_phone', 'second_party_contact_email',
                'second_party_company_email', 'second_party_address',
                'platform', 'reads_minimum', 'start_delay_sample_counts',
                'databasing_upper_limit', 'delivery_upper_limit',
            )
        }),
    )
    
    def contract_download(self, obj):
        field = obj.contract_file
        html = "<a href='%s'>下载</a>" % field.url if field else "无"
        return format_html(html)
    contract_download.short_description = '合同下载'
    
    def get_readonly_fields(self, request, obj=None):
        users_qs = User.objects.filter(groups__id=3).order_by("id")
        self.readonly_fields = (
            'start_delay_sample_counts', 'databasing_upper_limit',
            'delivery_upper_limit',
        ) if obj and request.user in users_qs else ()
        return self.readonly_fields
    
    def render_change_form(self, request, context, add=False, change=False,
                           form_url='', obj=None):
        initial = context["adminform"].form.initial
        
        # 默认设置当前登陆用户为乙方联系人
        contact_init = initial.get("second_party_contact")
        contact = contact_init if contact_init else request.user
        initial["second_party_contact"] = contact
        
        # 默认当前登陆用户的邮箱为乙方联系人邮箱
        email_init = initial.get("second_party_contact_email")
        email = email_init if email_init else request.user.email
        initial["second_party_contact_email"] = email
        
        # 默认当前分析项目包含所有高级分析项目
        analyses_init = initial.get("analyses_aa")
        analyses_objs = Analyses.objects.filter(union_id__contains="AA")
        analyses_aa = analyses_init if analyses_init else analyses_objs
        initial["analyses_aa"] = analyses_aa
        return super().render_change_form(
            request, context, add=add, change=change, form_url=form_url,
            obj=obj
        )
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        manager_qs = User.objects.filter(groups__id=7)
        current_qs = User.objects.filter(pk=request.user.pk)
        if not request.user.is_superuser and not current_qs & manager_qs:
            queryset = queryset.filter(second_party_contact=request.user)
        return queryset

    @staticmethod
    def date_format(_date):
        return _date.strftime('%Y{y}%m{m}%d{d}').format(y='年', m='月', d='日')
    
    def contract_produce(self, obj):
        template_text = "{}{}".format(TEMPLATE_FROM_PATH, "template_text.txt")
        template_docx = "{}{}".format(TEMPLATE_FROM_PATH, "template_docx.docx")
        fields = ContextFields(template_text=template_text).fields
        paragraph_context = {f: getattr(obj, f, "") for f in fields}
        extra_fields = {
            "signed_date": self.date_format(obj.signed_date),
            "pay_type": obj.get_pay_type_display(),
            "data_delivery_type": obj.get_data_delivery_type_display(),
            "second_party": obj.get_second_party_display(),
            "valid_period": "{}至{}".format(
                self.date_format(obj.signed_date),
                self.date_format(obj.valid_date),
            ),
        }
        clauses = clauses_decision(obj)
        aa = {a.union_id: a.analysis_name for a in obj.analyses_aa.all()}
        pa = {a.union_id: a.analysis_name for a in obj.analyses_pa.all()}
        paragraph_context.update(extra_fields)
        paragraph_context.update(aa)
        paragraph_context.update(pa)
        paragraph_context.update(clauses)
        contract = DocxProduce(
            template_text=template_text, template_docx=template_docx,
            paragraph_context=paragraph_context, table_context=TABLE_CONTEXT,
        )
        contract_name = "{}-{}".format(
            obj.contract_name, self.date_format(obj.signed_date)
        )
        contract.save(to_path=TEMPLATE_TO_PATH, file_name=contract_name)
        obj.contract_file = "uploads/{}.docx".format(contract_name)
        obj.save()
    
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        obj.analyses_aa.add(*form.cleaned_data["analyses_aa"])
        obj.analyses_pa.add(*form.cleaned_data["analyses_pa"])
        obj.save()
        form.save_m2m()
        self.contract_produce(obj)


BMS_admin_site.register(Analyses, AnalysesAdmin)
BMS_admin_site.register(ContractApplications, ContractApplicationsAdmin)
BMS_admin_site.register(Intention, IntentionAdmin)
BMS_admin_site.register(Customer, CustomerAdmin)
