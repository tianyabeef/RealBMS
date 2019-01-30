from django.contrib import admin, messages
from django.utils.html import format_html

from docx_parsing_gmdzy2010.renderer import DocxProduce, ContextFields
from docx_parsing_gmdzy2010.utilities import Price2UpperChinese

from datetime import date
from BMS.admin_bms import BMS_admin_site
from crm.models import Customer, Intention, IntentionRecord, Analyses, \
    ContractApplications
from crm.forms import IntentionForm
from BMS.settings import TEMPLATE_FROM_PATH, TEMPLATE_TO_PATH


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
        'amount', 'closing_date', 'price'
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
    }
    search_fields = ['union_id', 'analysis_name', 'analysis_type']
    filter_horizontal = ("analyses", )
    fieldsets = (
        ("变更信息", {
            'fields': (
                'contract_name', 'project_type', 'pay_type',
                ('extract_sample_counts', 'sequence_sample_counts'),
                'total_price', 'sequence_single_price', 'sequence_total_price',
                'extract_total_price', ('first_payment', 'final_payment'),
                'analyses',
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
        analyses_init = initial.get("analyses")
        analyses_objs = Analyses.objects.filter(union_id__contains="SE")
        analyses = analyses_init if analyses_init else analyses_objs
        initial["analyses"] = analyses
        return super().render_change_form(
            request, context, add=add, change=change, form_url=form_url,
            obj=obj
        )
    
    def save_model(self, request, obj, form, change):
        table_context = {
            "storage_select": {
                "attr": {"style": "Table Grid", "rows": 6, "cols": 4, },
                "data": (
                    ("选择", "存储设备", "存储量", "售价（元）"),
                    ("", "百度网盘", "<50G", "0.00（零圆整）"),
                    ("", "U盘", "16G", "70.00（柒拾圆整）"),
                    ("", "U盘", "32G", "150.00（壹佰伍拾圆整）"),
                    ("", "硬盘", "500G", "500.00（伍佰圆整）"),
                    ("", "硬盘", "1T", "700.00（柒佰圆整）"),
                )
            },
            "delivery_type": {
                "attr": {"style": "Table Grid", "rows": 5, "cols": 2, },
                "data": (
                    ("存储设备", "存储量"), ("U盘", "16G"), ("U盘", "32G"),
                    ("硬盘", "500G"), ("硬盘", "1T"),
                ),
            },
        }
        
        # 从文本模板读取字段总列表，并从数据库表中获取可能的字段值
        template_text = "{}{}".format(TEMPLATE_FROM_PATH, "template_text.txt")
        template_docx = "{}{}".format(TEMPLATE_FROM_PATH, "template_docx.docx")
        fields = ContextFields(template_text=template_text).fields
        
        # 准备上下文字典，特殊的字段用单独的字典集中更新
        paragraph_context = {f: getattr(obj, f, "") for f in fields}
        price_upper = {
            "pay_type": obj.get_pay_type_display(),
            "second_party": obj.get_second_party_display(),
            "total_price_upper": Price2UpperChinese(obj.total_price),
            "sequence_total_price_upper": Price2UpperChinese(
                obj.sequence_total_price
            ),
            "extract_total_price_upper": Price2UpperChinese(
                obj.extract_total_price
            ),
            "first_payment_upper": Price2UpperChinese(obj.first_payment),
            "final_payment_upper": Price2UpperChinese(obj.final_payment),
        }
        
        # TODO: 需要从数据库表中读取选择的分析条目，并生成分析条目字典，作为上下文更新到
        # 总的字典当中
        analyses = {
            # optional: advanced analysis
            "advanced_a": "a. 物种STAMP差异分析（每组样品数≥5）",
            "advanced_b": "b. 功能STAMP差异分析（每组样品数≥5）",
            "advanced_c": "c. Network网络分析（总样本量≥30）",
            "advanced_d": "d. 差异物种与代谢通路关联分析（总样品数≥30）",
            "advanced_e": "e. GraPhlAn分析每组样品数≥5）",
            "advanced_f": "f. 典范相关/冗余分析（CCA/RDA）（总样品数≥5，环境因子数≤6）",
    
            # optional: personalized analysis
            "personalized_a": "a. 疾病监测模型分析（Random Forest-ROC曲线）（总样本量≥60）",
            "personalized_b": "b. 肠型分析（总样本量≥100）",
            "personalized_c": "c. 阴道分型分析（总样本量≥60）",
            "personalized_d": "d. Fishtaco分析（每组样品数≥10，展示代谢通路≤5）",
            "personalized_e": "e. SourceTracker分析",
            "personalized_f": "f. （Partial）Mantel test分析（每组样品数≥5）",
            "personalized_g": "g. 个性化PCA分析（每组样品数≥5）",
        }
        paragraph_context.update(price_upper)
        paragraph_context.update(analyses)
        
        # 加载所有上下文数据，在选定路径下生成合同模板
        contract = DocxProduce(
            template_text=template_text, template_docx=template_docx,
            paragraph_context=paragraph_context, table_context=table_context,
        )
        to_path, file_name = TEMPLATE_TO_PATH, "{}".format(request.user)
        contract.save(file_name=file_name, to_path=to_path)
        
        # 最后将合同模板路径存入数据库表
        obj.contract_file = "uploads/{}.docx".format(request.user)
        return super().save_model(request, obj, form, change)


BMS_admin_site.register(Analyses, AnalysesAdmin)
BMS_admin_site.register(ContractApplications, ContractApplicationsAdmin)
BMS_admin_site.register(Intention, IntentionAdmin)
BMS_admin_site.register(Customer, CustomerAdmin)
