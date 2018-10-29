from django.contrib import admin
from .models import SubProject, ExtSubmit, LibSubmit, SeqSubmit, AnaSubmit
from django import forms
from BMS.admin_bms import BMS_admin_site
from datetime import date, timedelta
from fm.models import Bill
from mm.models import Contract
from django.db.models import Sum
from django.utils.html import format_html
from import_export import resources
from import_export import fields
from decimal import Decimal

#
# # 添加工作日
# def add_business_days(from_date, number_of_days):
#     to_date = from_date
#     if number_of_days >= 0:
#         while number_of_days:
#             to_date += timedelta(1)
#             if to_date.weekday() < 5:
#                 number_of_days -= 1
#     else:
#         while number_of_days:
#             to_date -= timedelta(1)
#             if to_date.weekday() < 5:
#                 number_of_days += 1
#     return to_date
#
#
# # 期间的收入
# def is_period_income(contract, period):
#     income = Bill.objects.filter(invoice__invoice__contract=contract).filter(invoice__invoice__period=period)\
#             .aggregate(total_income=Sum('income'))['total_income']
#     if not income:
#         return 0.001  # 未开票
#     if period == 'FIS':
#         amount = Contract.objects.filter(contract_number=contract)[0].fis_amount
#     elif period == 'FIN':
#         amount = Contract.objects.filter(contract_number=contract)[0].fin_amount
#     return amount - income
#
#
# class StatusListFilter(admin.SimpleListFilter):
#     title = '项目状态'
#     parameter_name = 'status'
#
#     def lookups(self, request, model_admin):
#         return (
#             ('AE', '已立项'),  # Already established
#             ('WEXT', '待抽提'),  # SE(Stay extraction)#项目管理在抽提任务下单表中把每一个子项目的样品都添加好，并提交。
#             ('EXT', '抽提中'),  # EXT(Extraction)    #实验管理添加了实验员之后，并通过钉钉通知了实验员
#             ('CLIB', '抽提完成：待客户反馈建库'),  # WFCFTD(Wait for customer feedback to build the database) #实验管理导入了样品的抽提结果，并提交
#             ('WLIB', '待建库'),  # TBL(To build libraries)#项目管理在建库任务下单表中把每一个子项目的样品都添加好，并提交。
#             ('LIB', '建库中'),  # LIB(libraries) #实验管理添加了建库实验员之后，并通过钉钉通知了实验员
#             ('CSEQ', '建库完成：待客户反馈测序'),  # WFCFS(Waiting for customer feedback sequencing)#实验管理导入了样品的建库结果，并提交
#             ('WSEQ', '待测序'),  # TBS(To build sequencing)#项目管理在测序任务下单表中把每一个子项目的样品都添加好，并提交。
#             ('SEQ', '测序中'),  # SEQ(sequencing)#实验管理添加了实验员之后，并通过钉钉通知了实验员
#             ('CANA', '测序完成：待客户反馈分析'),  # WFCFA(Waiting for Customer feedback analysis)#项目管理把测序的结果导入到样品表中
#             ('WANA', '待分析'),  # TBA(To build analysis)#项目管理新建一个分析项目
#             ('ANA', '分析中'),  # ANA(analysis)#生信管理添加了分析员
#             ('END', "完成")
#         )
#
#     def queryset(self, request, queryset):
#         # 不能启动（没有合同号）
#         if self.value() == 'CNS':
#             return queryset.filter(contract__contract_number=None)
#         # 提前启动（低于70%的总金额）
#         if self.value() == 'ES':
#             return queryset.filter(contract__fis_amount_in=None)
#         # 正常启动（70%-100%的总金额）
#         # if self.value() == 'NS':
#         #     return queryset.filter(contract__fis_amount > (Decimal(0.7)*contract__all_amount))
#         if self.value() == 'FIS':
#             return queryset.filter(contract__fis_date=None)
#         if self.value() == 'SEQ':
#             return queryset.exclude(seq_start_date=None).filter(seq_end_date=None)
#         if self.value() == 'ANA':
#             return queryset.exclude(ana_start_date=None).filter(ana_end_date=None)
#         if self.value() == 'FIN':
#             return queryset.exclude(ana_start_date=None).exclude(ana_end_date=None).filter(contract__fin_date=None)
#
#
# # 项目提交表
# class ProjectForm(forms.ModelForm):
#     def clean_seq_start_date(self):
#         if not self.cleaned_data['seq_start_date']:
#             return
#         project = SubProject.objects.filter(contract=self.cleaned_data['contract']).\
#             filter(name=self.cleaned_data['name']).first()
#         if project.is_confirm == 0:
#             raise forms.ValidationError('项目尚未启动，请留空')
#         if not project.is_lib:
#             return self.cleaned_data['seq_start_date']
#         lib_date = project.lib_date
#         if not lib_date:
#             raise forms.ValidationError('尚未完成建库，无法记录测序时间')
#         elif lib_date > self.cleaned_data['seq_start_date']:
#             raise forms.ValidationError('测序开始日期不能早于建库完成日期')
#         return self.cleaned_data['seq_start_date']
#
#     def clean_ana_start_date(self):
#         if not self.cleaned_data['ana_start_date']:
#             return
#         if 'seq_end_date' not in self.cleaned_data.keys() or not self.cleaned_data['seq_end_date']:
#             raise forms.ValidationError('尚未完成测序，无法记录分析时间')
#         elif self.cleaned_data['seq_end_date'] > self.cleaned_data['ana_start_date']:
#             raise forms.ValidationError('分析开始日期不能早于测序完成日期')
#         return self.cleaned_data['ana_start_date']
#
#     def clean_seq_end_date(self):
#         if not self.cleaned_data['seq_end_date']:
#             return
#         if 'seq_start_date' not in self.cleaned_data.keys() or not self.cleaned_data['seq_start_date']:
#             raise forms.ValidationError('尚未记录测序开始日期')
#         elif self.cleaned_data['seq_end_date'] and self.cleaned_data['seq_start_date'] \
#                 > self.cleaned_data['seq_end_date']:
#             raise forms.ValidationError('完成日期不能早于开始日期')
#         return self.cleaned_data['seq_end_date']
#
#     def clean_ana_end_date(self):
#         if not self.cleaned_data['ana_end_date']:
#             return
#         if 'ana_start_date' not in self.cleaned_data.keys() or not self.cleaned_data['ana_start_date']:
#             raise forms.ValidationError('尚未记录分析开始日期')
#         elif self.cleaned_data['ana_start_date'] > self.cleaned_data['ana_end_date']:
#             raise forms.ValidationError('完成日期不能早于开始日期')
#         return self.cleaned_data['ana_end_date']
#
#     def clean_report_date(self):
#         if not self.cleaned_data['report_date']:
#             return
#         if 'ana_end_date' not in self.cleaned_data.keys() or not self.cleaned_data['ana_end_date']:
#             raise forms.ValidationError('分析尚未完成')
#         return self.cleaned_data['report_date']
#
#     def clean_result_date(self):
#         if not self.cleaned_data['result_date']:
#             return
#         if 'ana_end_date' not in self.cleaned_data.keys() or not self.cleaned_data['ana_end_date']:
#             raise forms.ValidationError('分析尚未完成')
#         return self.cleaned_data['result_date']
#
#     def clean_data_date(self):
#         if not self.cleaned_data['data_date']:
#             return
#         if not Contract.objects.filter(contract_number=self.cleaned_data['contract']).first().fin_date:
#             raise forms.ValidationError('尾款未到不能操作该记录')
#
#
# class ProjectResource(resources.ModelResource):
#
#     def init_instance(self, row=None):
#         instance = self._meta.model()
#         instance.project = SubProject.objects.get(id=row['contract__contract_number'])
#         return instance
#
#     class Meta:
#         model = SubProject
#         skip_unchanged = True
#         fields = ('id', 'contract__contract_number',)
#     # 按照合同号导出
#     sub_number = fields.Field(column_name="子项目编号", attribute="sub_number")
#
#     class Meta:
#         model = SubProject
#         skip_unchanged = True
#         fields = ('sub_number',)
#         export_order = ('sub_number',)


# 项目管理
# class ProjectAdmin(ImportExportModelAdmin):
class ProjectAdmin(admin.ModelAdmin):
    # resource_class = ProjectResource
    # form = ProjectForm
    list_display = ('id', 'contract_number', 'contract_name', 'sub_number', 'sub_project', 'project_manager', 'saleman',
                    'project_start_time', 'is_status', 'time_ext', 'time_lib', 'time_ana', 'income_notes',
                    'status', 'is_submit', 'file_to_start', 'sub_project_note', )
    # list_editable = ['is_confirm']
    # list_filter = [StatusListFilter]
    fieldsets = (
        ('合同信息', {
            'fields': (('contract', 'contract_name', 'income_notes', 'saleman',),),
        }),
        ('项目信息', {
            'fields': (('sampleInfoForm', 'customer_name', 'customer_phone', 'service_types',),
                       ('sub_number', 'sub_project',),
                       ('sub_project_note',),
                       ('is_ext', 'is_lib', 'is_seq', 'is_ana',),
                       ('file_to_start', 'is_submit',),),
        }),
    )
    readonly_fields = ['contract_name', 'income_notes', 'saleman', 'customer_name', 'customer_phone', 'service_types', ]
    raw_id_fields = ['contract', 'sampleInfoForm', 'project_manager', ]
    actions = ['make_confirm']
    search_fields = ['id', 'contract__contract_number', ]
    # change_list_template = "pm/chang_list_custom.html"

# 合同相关信息（合同号，合同名，到款，销售）
    def contract_number(self, obj):
        return obj.contract.contract_number
    contract_number.short_description = '合同编号'

    def contract_name(self, obj):
        return obj.contract.name
    contract_name.short_description = '合同名称'

    def income_notes(self, obj):
        return obj.contract.fis_amount
    income_notes.short_description = '到款的记录'

    def saleman(self, obj):
        return obj.contract.salesman
    saleman.short_description = '销售人员'

# 样品表相关信息（样品寄样人，样品寄样人电话，项目类型）
    def customer_name(self, obj):
        return obj.sampleInfoForm.transform_contact
    customer_name.short_description = '寄样人姓名'

    def customer_phone(self, obj):
        return obj.sampleInfoForm.transform_phone
    customer_phone.short_description = '寄样联系人电话'

    def service_types(self, obj):
        # return obj.sampleInfoForm.project_type
        return obj.sampleInfoForm.get_project_type_display()
    service_types.short_description = '项目类型'

    def get_list_display_links(self, request, list_display):
        if not request.user.has_perm('pm.add_project'):
            return
        return ['contract_name']

    # def get_queryset(self, request):
    #     # 只允许管理员和拥有该模型新增权限的人员才能查看所有样品
    #     qs = super(ProjectAdmin, self).get_queryset(request)
    #     if request.user.is_superuser or request.user.has_perm('pm.add_project'):
    #         return qs
    #     return qs.filter(contract__salesman=request.user)
    #
    # def get_actions(self, request):
    #     # 无权限人员取消actions
    #     actions = super(ProjectAdmin, self).get_actions(request)
    #     if not request.user.has_perm('pm.add_project'):
    #         actions = None
    #     return actions

    def save_model(self, request, obj, form, change):

        if obj.contract.fis_amount < (obj.contract.all_amount * Decimal(0.7)):
            SubProject.objects.filter(status=False).update(status=True)
        else:
            SubProject.objects.filter(status=False).update(status=False)
        super(ProjectAdmin, self).save_model(request, obj, form, change)
        if request.user.is_authenticated:
            SubProject.project_manager = request.user.username
        obj.save()


# 提取提交表
class ExtSubmitForm(forms.ModelForm):
    pass


# 提取提交管理
class ExtSubmitAdmin(admin.ModelAdmin):
    # form = ExtSubmitForm
    list_display = [
                    'subProject',
                    # 'save_number',
                    'ext_number', 'sample_count', 'ext_start_date',
                    # 'contract_count', 'project_count',
                    'is_submit', 'note', ]
    filter_horizontal = ('sample',)
    fields = (
              'subProject',
              # 'save_number',
              'ext_number', 'sample', 'sample_count', 'is_submit', 'note')
    raw_id_fields = [
                     'subProject',
                    ]

    # def save_number(self, obj):
    #     return obj.SubProject.get_sub_number_display()
    # save_number.short_description = '子项目号码'
    # def is_exts(self, obj):
    #     if Project.is_ext:
    #         # return [obj.is_ext.value,
    #         #         # obj.id, obj.contract_number,  obj.contract_name, obj.sub_number, obj.sub_project,
    #         #         # obj.customer_name, obj.saleman,
    #         #         # obj.project_personnel,
    #         #         ]
    #         return obj.is_exts is True
    # is_exts.short_description = '已经提取'

    # def contract_count(self, obj):
    #     pass
    #     # return len(set(i.project.contract.contract_number for i in obj.sample.all()))
    # contract_count.short_description = '合同数'

    # def project_count(self, obj):
    #     pass
    #     # return len(set([i.project.name for i in obj.sample.all()]))
    # project_count.short_description = '项目数'

    # def sample_count(self, obj):
    #     return obj.sample.all().count()
    # sample_count.short_description = '样品数'

    # def get_readonly_fields(self, request, obj=None):
    #     if obj and obj.is_submit:
    #         return ['slug', 'date', 'sample', 'is_submit']
    #     return ['slug', 'date', ]

    #  已经选定需提取的，并且提交确认的立项放在提取任务下单里
    # if request.SubProject.is_ext and request.SubProject.is_confirm:
    #     self.list_display =['contract','ext_slug', 'slug', 'ext_man', 'ext_cycle',
    #                         'contract_count', 'project_count', 'sample_count',
    #             'date', 'is_submit']
    #     # obj.sub_number = request.SubProject.sub_number
    # obj.save()

    # return ProjectAdmin.contract_number, ProjectAdmin.customer_name
    # contract_number=ProjectAdmin.contract_number()
    # def save_model(self, request, obj, form, change):
    #     if request.SubProject.is_ext and request.SubProject.is_submit:
    #         self.list_display = ['subProject', 'ext_number', 'sample_count', 'ext_start_date',
    #                              'contract_count', 'project_count', 'is_submit', 'note', ]
    #         obj.sub_number = request.SubProject.sub_number
    #     obj.save()
    # list_display = ['save_model', ]
    # filter_horizontal = []
    # fields = []
    # raw_id_fields = []
    #
    # def save_model(self, request, obj, form, change):
    #     super(ExtSubmitAdmin, self).save_model(request, obj, form, change)
    #     # print(SubProject.is_ext())
    #     # print(SubProject.is_submit())
    #     if SubProject.is_ext and SubProject.is_submit:
    #         return obj.SubProject.get_sub_number_display()
    #     # obj.save()


# 建库提交表
class LibSubmitForm(forms.ModelForm):
    pass


# 建库提交管理
class LibSubmitAdmin(admin.ModelAdmin):
    # form = LibSubmitForm
    list_display = ['subProject', 'lib_number', 'customer_sample_count', 'lib_start_date', 'customer_confirmation_time',
                    # 'contract_count', 'project_count',
                    'sample_count', 'is_submit', 'note', ]
    filter_horizontal = ('sample',)
    fields = ('subProject', 'lib_number', 'sample',
              'customer_confirmation_time', 'customer_sample_count', 'is_submit', 'note',)
    raw_id_fields = ['subProject', ]

    # def contract_count(self, obj):
    #     pass
    #     # return len(set(i.project.contract.contract_number for i in obj.sample.all()))
    # contract_count.short_description = '合同数'
    #
    # def project_count(self, obj):
    #     pass
    #     # return len(set([i.project.name for i in obj.sample.all()]))
    # project_count.short_description = '项目数'

    def sample_count(self, obj):
        pass
        # return obj.sample.all().count()
    sample_count.short_description = '样品数'


# 测序提交表
class SeqSubmitForm(forms.ModelForm):
    pass


# 测序提交管理
class SeqSubmitAdmin(admin.ModelAdmin):
    # form = SeqSubmitForm
    list_display = ['subProject', 'seq_number', 'customer_sample_count', 'seq_start_date', 'customer_confirmation_time',
                    'pooling_excel',
                    # 'contract_count',  'project_count',
                    'sample_count', 'is_submit', 'note',
                    ]
    filter_horizontal = ('sample',)
    fields = ('subProject', 'sample', 'seq_number', 'customer_confirmation_time',
              'customer_sample_count', 'pooling_excel', 'is_submit', 'note', )
    raw_id_fields = ['subProject', ]

    # def contract_count(self, obj):
    #     pass
    #     # return len(set(i.project.contract.contract_number for i in obj.sample.all()))
    # contract_count.short_description = '合同数'
    #
    # def project_count(self, obj):
    #     pass
    #     # return len(set([i.project.name for i in obj.sample.all()]))
    # project_count.short_description = '项目数'

    def sample_count(self, obj):
        pass
        # return obj.sample.all().count()
    sample_count.short_description = '样品数'


# 分析提交表
class AnaSubmitForm(forms.ModelForm):
    pass


# 分析提交管理
class AnaSubmitAdmin(admin.ModelAdmin):
    # form = AnaSubmitForm
    list_display = ['invoice_code', 'sample_count', 'ana_start_date', 'depart_data_path', 'data_analysis',
                    'contract_count', 'project_count',  'is_submit', 'note', ]
    fields = ('contract', 'invoice_code', 'note', 'sample_count', 'is_submit',
              'depart_data_path', 'data_analysis')
    # raw_id_fields = ['contract', ]
    filter_horizontal = ('contract',)

    def contract_count(self, obj):
        pass
        # return len(set(i.project.contract.contract_number for i in obj.contract.all()))
    contract_count.short_description = '合同数'

    def project_count(self, obj):
        pass
        # return len(set([i.project.name for i in obj.contract.all()]))
    project_count.short_description = '项目数'

    # def sample_count(self, obj):
    #     return obj.sample.all().count()
    # sample_count.short_description = '样品数'


BMS_admin_site.register(SubProject, ProjectAdmin)
BMS_admin_site.register(ExtSubmit, ExtSubmitAdmin)
BMS_admin_site.register(LibSubmit, LibSubmitAdmin)
BMS_admin_site.register(SeqSubmit, SeqSubmitAdmin)
BMS_admin_site.register(AnaSubmit, AnaSubmitAdmin)
