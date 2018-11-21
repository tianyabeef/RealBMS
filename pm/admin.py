from BMS.admin_bms import BMS_admin_site
from .models import SubProject, ExtSubmit, LibSubmit, SeqSubmit,AnaSubmit
from django.contrib import admin
from sample.models import SampleInfoForm
from mm.models import Contract
from mm.models import Invoice as mm_Invoice
from fm.models import Invoice as fm_Invoice
from decimal import Decimal
from django.contrib import messages
from sample.models import SampleInfo
from django.contrib.auth.models import Group,User
from django import forms
import datetime
from lims.models import ExtExecute as lims_ExtExecute
from lims.models import LibExecute as lims_LibExecute
from lims.models import SeqExecute as lims_SeqExecute
from am.models import AnaExecute as am_anaExecute
from lims.models import SampleInfoExt as lims_SampleInfoExt
from lims.models import SampleInfoLib as lims_SampleInfoLib
from lims.models import SampleInfoSeq as lims_SampleInfoSeq
from import_export import resources
from import_export.admin import ImportExportModelAdmin, ImportExportActionModelAdmin
from datetime import date
from daterange_filter.filter import DateRangeFilter
from BMS.settings import DINGTALK_APPKEY, DINGTALK_SECRET
from BMS.notice_mixin import NotificationMixin
from django.forms import fields
from django.db import models


class SubProjectForm(forms.ModelForm):
    def clean_sample_count(self):
        sample_count = self.cleaned_data['sample_count']
        if sample_count == 0:
            raise forms.ValidationError('样品数量不能为0')
        return self.cleaned_data['sample_count']

    def clean_sampleInfoForm(self):
        sampleInfoForm = self.cleaned_data['sampleInfoForm']
        if not sampleInfoForm:
            raise forms.ValidationError("样品表单需要添加")
        return self.cleaned_data['sampleInfoForm']


class SalemanListFilter(admin.SimpleListFilter):
    title = "销售人员"
    parameter_name = 'salesman'

    def lookups(self, request, model_admin):
        qs_sale = User.objects.filter(groups__name='业务员（销售）')
        value = ['contract__salesman'] + list(qs_sale.values_list('username', flat=True))
        label = ['销售人员'] + ['——' + i.last_name + i.first_name for i in qs_sale]
        return tuple(zip(value, label))

    def queryset(self, request, queryset):
        if self.value() == 'contract__salesman':
            return queryset.filter(contract__salesman__in=list(User.objects.filter(groups__name="业务员（销售）")))
        qs = User.objects.filter(groups__name="业务员（销售）")
        for i in qs:
            if self.value() == i.username:
                return queryset.filter(contract__salesman=i)


class StatusListFilter(admin.SimpleListFilter):
    title = '项目管理员'
    parameter_name = 'project_manager'
    def lookups(self, request, model_admin):
        qs_sale = User.objects.filter(groups__name="项目管理")
        value = ['project_manager'] + list(qs_sale.values_list('username', flat=True))
        label = ['项目管理员'] + ['——' + i.last_name + i.first_name for i in qs_sale]
        return tuple(zip(value, label))

    def queryset(self, request, queryset):
        if self.value() == 'project_manager':
            return queryset.filter(project_manager__in = list(User.objects.filter(groups__name="项目管理")))
        qs = User.objects.filter(groups__name="项目管理")
        for i in qs:
            if self.value() == i.username:
                return queryset.filter(project_manager=i)

def creat_uniq_number(request,instance,name):
    if instance.objects.all().count() == 0:
        uniq_number = request.user.username + \
                               '-' + str(datetime.datetime.now().year) + \
                               str(datetime.datetime.now().month) + str(datetime.datetime.now().day) + '-'+name+'-' + \
                               "1"
    else:
        uniq_number = request.user.username + \
                               '-' + str(datetime.datetime.now().year) + \
                               str(datetime.datetime.now().month) + str(datetime.datetime.now().day) + '-'+name+'-' + \
                               str(int(instance.objects.latest("id").id) + 1)
    return uniq_number


def create_submit_table(request,obj, states):
    ##新建执行表
    ext_number = creat_uniq_number(request, ExtSubmit, 'Ext')
    lib_number = creat_uniq_number(request, LibSubmit, 'Lib')
    seq_number = creat_uniq_number(request, SeqSubmit, 'Seq')
    ana_number = creat_uniq_number(request, AnaSubmit, 'Ana')

    for i, v in enumerate(states):
        if v == True:
            if i == 0:
                sampleInfoForms = SampleInfoForm.objects.filter(subproject__id=obj.id)
                extSubmit = ExtSubmit.objects.create(subProject=obj, sample_count=obj.sample_count, ext_number=ext_number, project_manager=request.user)
                for sampleInfoForm in sampleInfoForms:
                    sampleInfos = SampleInfo.objects.filter(sampleinfoform__id=sampleInfoForm.id)
                    for sampleInfo in sampleInfos:
                        extSubmit.sample.add(sampleInfo)
            elif i == 1:
                sampleInfoForms = SampleInfoForm.objects.filter(subproject__id=obj.id)
                libSubmit = LibSubmit.objects.create(subProject=obj, customer_sample_count=obj.sample_count, lib_number=lib_number, project_manager=request.user)
                for sampleInfoForm in sampleInfoForms:
                    sampleInfos = SampleInfo.objects.filter(sampleinfoform__id=sampleInfoForm.id)
                    for sampleInfo in sampleInfos:
                        libSubmit.sample.add(sampleInfo)
            elif i == 2:
                sampleInfoForms = SampleInfoForm.objects.filter(subproject__id=obj.id)
                seqSubmit = SeqSubmit.objects.create(subProject=obj, customer_sample_count=obj.sample_count, seq_number=seq_number, project_manager=request.user)
                for sampleInfoForm in sampleInfoForms:
                    sampleInfos = SampleInfo.objects.filter(sampleinfoform__id=sampleInfoForm.id)
                    for sampleInfo in sampleInfos:
                        seqSubmit.sample.add(sampleInfo)
            elif i == 3:
                sampleInfoForms = SampleInfoForm.objects.filter(subproject__id=obj.id)
                anaSubmit = AnaSubmit.objects.create(sample_count=obj.sample_count, ana_number=ana_number, project_manager=request.user)
                anaSubmit.subProject.add(obj)
            else:
                pass
            break


class SubProject_Resource(resources.ModelResource):
    # pass
    class Meta:
        model = SubProject
        skip_unchanged = True
        report_skipped = False
        fields = ('contract__contract_number', 'contract__name', 'sub_number', 'sub_project', 'contract__contacts',
                  'contract__salesman__username', 'project_manager__username', 'is_submit', 'status', 'file_to_start',
                  'is_status', )
        export_order = ('contract__contract_number', 'contract__name', 'sub_number', 'sub_project',
                        'contract__contacts', 'contract__salesman__username', 'project_manager__username', 'is_submit',
                        'status', 'file_to_start', 'is_status', )

    def get_export_headers(self):
        return ['合同号', '合同名称', '子项目编号', '子项目的名称', '合同联系人姓名', '销售人员', '项目管理人员',
                '是否确认(0-否，1-是)', '项目是否提前启动(0-否，1-是)', '已上传信息',
                '状态（1-已立项，2-待抽提，3-抽提中，4-抽提完成：待客户反馈建库，5-待建库，6-建库中，7-建库完成：待客户反馈测序，8-待测序，9-测序中，10-测序完成：待客户反馈分析，11-待分析，12-分析中，13-完成，14-终止）',]

    def get_diff_headers(self):
        return ['合同号', '合同名称', '子项目编号', '子项目的名称', '合同联系人姓名', '销售人员', '项目管理人员',
                '是否确认(0-否，1-是)', '项目是否提前启动(0-否，1-是)', '已上传信息',
                '状态（1-已立项，2-待抽提，3-抽提中，4-抽提完成：待客户反馈建库，5-待建库，6-建库中，7-建库完成：待客户反馈测序，8-待测序，9-测序中，10-测序完成：待客户反馈分析，11-待分析，12-分析中，13-完成，14-终止）',]


# class SubProjectAdmin(admin.ModelAdmin,NotificationMixin):
class SubProjectAdmin(ImportExportActionModelAdmin, NotificationMixin):
    resource_class = SubProject_Resource
    form = SubProjectForm

    appkey = DINGTALK_APPKEY
    appsecret = DINGTALK_SECRET
    list_display = ('contract_number', 'contract_name', 'sub_number', 'sub_project', 'contacts', 'saleman',
                    'project_manager', 'is_submit', 'status','file_link','is_status',  'project_start_time', 'time_ext', 'time_lib', 'time_ana')
    list_display_links = ['sub_number', ]
    actions = ['make_submit', 'make_subProject_submit']
    fieldsets = (
        ('合同信息', {
           'fields': (('contract','contract_name',),
                      ( 'contacts','contacts_phone', 'saleman','company','project_type'),)
        }),
        ('到款记录', {
            'fields': ('income_notes',)
        }),
        ('样品信息', {
            'fields': ('sampleInfoForm',
                       ('customer_name', 'customer_phone', 'service_types',),
                       ('sample_receiver','arrive_time',)),
        }),
        ('子项目信息', {
            'fields': ('sub_number','sub_project','sample_count','file_to_start',)
        }),
        ('任务信息', {
                'fields': (('is_ext', 'is_lib','is_seq', 'is_ana'),
                           ('sub_project_note',),)
        }),
    )
    readonly_fields = ['contract_number', 'contract_name', 'contacts','contacts_phone', 'saleman','company',
                       'project_type','income_notes','customer_name', 'customer_phone', 'service_types',
                       'sample_receiver','arrive_time']
    raw_id_fields = ['contract', ]
    filter_horizontal = ['sampleInfoForm', ]
    search_fields = ['contract__contract_number', 'contract__name', 'sub_number', "sub_project", 'contract__contacts',
                     'contract__salesman__username', 'project_manager__username',  'project_start_time', 'time_ext', 'time_lib', 'time_ana']
    autocomplete_fields = ('contract',)
    ordering = ['-sub_number', ]
    # change_list_template = "pm/chang_list_custom.html"
    list_per_page = 50
    def make_subProject_submit(self, request,queryset):
        """
        终止任务
        """
        for obj in queryset:
            obj.is_status = 14
            obj.save()
        # 项目中止的时候，给项目管理和实验发钉钉通知
        self.send_group_message("编号{0}中止------，中止人员:{1}".format(obj.sub_number, obj.project_manager),
                                "chat62dbddc59ef51ae0f4a47168bdd2a65b")
        print(self.send_dingtalk_result)
    make_subProject_submit.short_description = '终止'

    def contract_number(self, obj):
        return obj.contract.contract_number
    contract_number.short_description = '合同号'

    def contract_name(self, obj):
        return obj.contract.name
    contract_name.short_description = '合同名称'

    def contacts(self, obj):
        return obj.contract.contacts
    contacts.short_description = '合同联系人姓名'

    def contacts_phone(self, obj):
        return obj.contract.contact_phone
    contacts_phone.short_description = '合同联系人电话'

    def company(self, obj):
        return obj.contract.partner_company
    company.short_description = '合作伙伴单位'

    def saleman(self, obj):
        return obj.contract.salesman
    saleman.short_description = '销售人员'

    def project_type(self,obj):
        return obj.contract.get_type_display()
    project_type.short_description = '项目类型'

    def income_notes(self, obj):
        return_content = "款期\t到账日期\t到账金额\t合同金额\n"
        mm_invoices = mm_Invoice.objects.filter(contract__id=obj.contract.id)
        for mm_invoice in mm_invoices:
            fm_invoice = fm_Invoice.objects.get(invoice__id=mm_invoice.id)
            return_content = "%s%s\t%s\t%s\t%s\n" % (
            return_content, mm_invoice.get_period_display(), fm_invoice.income_date, fm_invoice.income, Contract.all_amount)
        return return_content
    income_notes.short_description = '到款的记录'

    # def income_notes(self, obj):
    #     return_content = "款期\t到账日期\t到账金额\n"
    #     mm_invoices = mm_Invoice.objects.filter(contract__id=obj.contract.id)
    #     for mm_invoice in mm_invoices:
    #         fm_invoice = fm_Invoice.objects.get(invoice__id=mm_invoice.id)
    #         return_content = "%s%s\t%s\t%s\n" % (
    #         return_content, mm_invoice.get_period_display(), fm_invoice.income_date, fm_invoice.income)
    #     return return_content
    # income_notes.short_description = '到款的记录'

    # 样品表相关信息（样品寄样人，样品寄样人电话，项目类型）
    def customer_name(self, obj):
        sampleInfoForms = SampleInfoForm.objects.filter(subproject__id=obj.id)
        if not obj.sub_number:
            return "-"
        else:
            return "\t".join([sampleInfoForm.transform_contact for sampleInfoForm in sampleInfoForms])
    customer_name.short_description = '寄样人姓名'

    def customer_phone(self, obj):
        sampleInfoForms = SampleInfoForm.objects.filter(subproject__id=obj.id)
        if not obj.sub_number:
            return "-"
        else:
            return [sampleInfoForm.transform_phone for sampleInfoForm in sampleInfoForms]
    customer_phone.short_description = '寄样联系人电话'

    def service_types(self, obj):
        sampleInfoForms = SampleInfoForm.objects.filter(subproject__id=obj.id)
        if not obj.sub_number:
            return "-"
        else:
            return "\t".join([sampleInfoForm.get_project_type_display() for sampleInfoForm in sampleInfoForms])
    service_types.short_description = '项目类型'

    def sample_receiver(self, obj):
        sampleInfoForms = SampleInfoForm.objects.filter(subproject__id=obj.id)
        if not obj.sub_number:
            return "-"
        else:
            return ["%s %s"%(sampleInfoForm.sample_receiver.last_name,sampleInfoForm.sample_receiver.first_name) for sampleInfoForm in sampleInfoForms]
    sample_receiver.short_description = '样品接收人'

    def arrive_time(self, obj):
        sampleInfoForms = SampleInfoForm.objects.filter(subproject__id=obj.id)
        if not obj.sub_number:
            return "-"
        else:
            return [sampleInfoForm.arrive_time for sampleInfoForm in sampleInfoForms]
    arrive_time.short_description = '样品接收时间'


    def get_readonly_fields(self, request, obj=None):
        readonly_fields = self.readonly_fields
        if obj:
            if obj.is_submit:
                readonly_fields = ['contract', 'contract_number', 'contract_name','contacts', 'contacts_phone',
                                'saleman', 'company', 'project_type','income_notes','sampleInfoForm','customer_name',
                                'customer_phone', 'service_types','sample_receiver', 'arrive_time','sub_number',
                                'sub_project', 'sample_count','is_ext', 'is_lib', 'is_seq', 'is_ana','sub_project_note','is_submit']
        else:
            #新增的时候不能点确定
            return ['contract_number', 'contract_name', 'contacts', 'contacts_phone', 'saleman', 'company',
                               'project_type', 'income_notes', 'customer_name', 'customer_phone', 'service_types',
                               'sample_receiver', 'arrive_time','is_submit']
        return readonly_fields

    def get_queryset(self, request):
        qs = super(SubProjectAdmin, self).get_queryset(request)
        # 普通项目管理只能看到自己的管理的子项目,其他的有权限的人可以看到所有的
        groups = Group.objects.filter(user__id = request.user.id)
        if len(groups) >= 1:
            for i in groups:
                if i.name == "项目管理":
                    return qs.filter(project_manager=request.user)
                else:
                    return qs
        else:
            return qs

    def get_list_filter(self, request):
        #一般的项目管理只能有状态的过滤器，其他人员有所有的过滤器
        groups = Group.objects.filter(user__id=request.user.id)
        if len(groups) >= 1:
            for i in groups:
                if i.name == "项目管理":
                    return ['is_status']
                else:
                    return ['is_status', StatusListFilter, SalemanListFilter, ('project_start_time', DateRangeFilter), ('time_ext', DateRangeFilter),('time_lib',  DateRangeFilter),('time_ana', DateRangeFilter), ]
        else:
            return ['is_status', StatusListFilter, SalemanListFilter, ('project_start_time', DateRangeFilter), ('time_ext', DateRangeFilter),('time_lib',  DateRangeFilter),('time_ana', DateRangeFilter), ]

    # 更改修改表单里的按钮
    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        add = object_id is None
        if add:
            pass
        else:
            obj = SubProject.objects.get(pk=object_id)
            if obj:
                if obj.is_submit:
                    extra_context['show_delete'] = False
                    extra_context['show_save_and_add_another'] = False
                    extra_context['show_save'] = False
                    extra_context['show_save_as_new'] = False
                    extra_context['show_save_and_continue'] = False

        return super(SubProjectAdmin,self).change_view(request, object_id, form_url, extra_context=extra_context)

    def save_model(self, request, obj, form, change):
        if not obj.project_start_time:
            obj.project_start_time = date.today()
        states =[obj.is_ext , obj.is_lib ,obj.is_seq, obj.is_ana]
        project_amount = obj.sample_count * obj.contract.price
        contract_income = 0
        mm_invoices = mm_Invoice.objects.filter(contract__id=obj.contract.id)
        for mm_invoice in mm_invoices:
            fm_invoice = fm_Invoice.objects.get(invoice__id=mm_invoice.id)
            contract_income = fm_invoice.income + contract_income
        if project_amount * Decimal(0.7) > (contract_income-obj.contract.use_amount):
            obj.status = True
        else:
            obj.status = False
        obj.project_manager = request.user
        if obj.status:
            if obj.file_to_start:
                if obj.is_submit:
                    contract = Contract.objects.get(id=obj.contract.id)
                    contract.use_amount = contract.use_amount + project_amount
                    contract.save()
                    #新建执行表单
                    create_submit_table(request, obj, states)
                obj.save()
            else:
                if change:
                    self.message_user(request, '子项目编号：%s属于提取启动，必须上传审批文件'%(obj.sub_number),level=messages.ERROR)
                else:
                    obj.status=False
                    obj.is_submit=False
                    obj.sample_count=0
                    self.message_user(request, '子项目编号：%s，属于提取启动，必须上传审批文件'%(obj.sub_number), level=messages.ERROR)
                    obj.save()
        else:
            if obj.is_submit:
                contract = Contract.objects.get(id=obj.contract.id)
                contract.use_amount = contract.use_amount + project_amount
                contract.save()
                # 新建执行表单
                create_submit_table(request, obj, states)
            obj.save()
        super().save_model(request, obj, form, change)

    def make_submit(self, request, queryset):
        n = 0
        un =  0
        sn = 0
        for obj in queryset:
            if not obj.is_submit:
                states = [obj.is_ext, obj.is_lib, obj.is_seq, obj.is_ana]
                project_amount = obj.sample_count * obj.contract.price
                contract_income = 0
                mm_invoices = mm_Invoice.objects.filter(contract__id=obj.contract.id)
                for mm_invoice in mm_invoices:
                    fm_invoice = fm_Invoice.objects.get(invoice__id=mm_invoice.id)
                    contract_income = fm_invoice.income + contract_income
                if project_amount * Decimal(0.7) > (contract_income - obj.contract.use_amount):
                    obj.status = True
                else:
                    obj.status = False
                obj.project_manager = request.user
                if obj.status:
                    if obj.file_to_start:
                        contract = Contract.objects.get(id=obj.contract.id)
                        contract.use_amount = contract.use_amount + project_amount
                        contract.save()
                        # 新建执行表单
                        create_submit_table(request, obj, states)
                        obj.is_submit = True
                        obj.save()
                        n = n +1
                    else:
                        un = un +1
                else:
                    contract = Contract.objects.get(id=obj.contract.id)
                    contract.use_amount = contract.use_amount + project_amount
                    contract.save()
                    # 新建执行表单
                    create_submit_table(request, obj, states)
                    obj.is_submit = True
                    obj.save()
                    n = n + 1
            else:
                sn = sn + 1
        self.message_user(request,"选择项目数量：%s,所选项目立项的子项目数量：%s,   无法立项的子项目数量：%s  ,已经立项过的子项目数量：%s" %(queryset.count(),n,un,sn), level=messages.ERROR)
        # 新增立项的时候，给实验发钉钉通知
        self.send_group_message("编号{0}的立项完成------，立项人员:{1}".format(obj.sub_number, obj.project_manager),
                                "chat62dbddc59ef51ae0f4a47168bdd2a65b")
        print(self.send_dingtalk_result)
    make_submit.short_description = '设置所选项目为确认可启动状态'

    def get_actions(self, request):
        actions = super().get_actions(request)
        for group in request.user.groups.all():
            if group.id == 13:  # 项目管理组之外都不能启动中止项目
                pass
            else:
                if "make_submit" in actions:
                    del actions["make_submit"]
                if "make_subProject_submit" in actions:
                    del actions["make_subProject_submit"]
        return actions


# 提取提交表
class ExtSubmitForm(forms.ModelForm):
    # pass
    class Meta:
        model = ExtSubmit
        fields = "__all__"

    def clean_subProject(self):
        subProject = self.cleaned_data['subProject']
        if subProject.is_status == 13:
            raise forms.ValidationError("该子项目已经完成，请选择其他子项目")
        elif subProject.is_status == 14:
            raise forms.ValidationError("该子项目已经中止，请选择其他子项目")
        return self.cleaned_data['subProject']



# 提取提交管理
class ExtSubmitAdmin(admin.ModelAdmin,NotificationMixin):
    form = ExtSubmitForm
    appkey = DINGTALK_APPKEY
    appsecret = DINGTALK_SECRET
    list_display = ['subProject', 'ext_number', 'sample_count', 'ext_start_date', 'is_submit', 'note', ]
    filter_horizontal = ('sample',)
    fieldsets = (
        ('合同信息',{
            'fields':(('contacts','contract_number','partner_company',),
                      ('subProject','sub_project_name','sample_receiver','arrive_time',),)
        }),
        ('任务信息',{
            'fields':('ext_number', 'sample', 'sample_count',
              'ext_start_date',('note',),)
        })
    )
    readonly_fields = ['sample_receiver', 'contract_number', 'sub_project_name', 'contacts', 'partner_company', 'arrive_time','ext_number','sample_count',]
    search_fields = ['subProject__sub_number', 'ext_number', 'sample_count', 'ext_start_date', 'note', ]
    autocomplete_fields = ('subProject',)
    list_per_page = 50
    def contacts(self, obj):
        return obj.subProject.contract.contacts
    contacts.short_description = '合同联系人姓名'

    def sub_project_name(self, obj):
        return obj.subProject.sub_project
    sub_project_name.short_description = '子项目名称'

    def contract_number(self, obj):
        return obj.subProject.contract.contract_number
    contract_number.short_description = '合同号'

    def partner_company(self, obj):
        return obj.subProject.contract.partner_company
    partner_company.short_description = '合同单位'

    def sample_receiver(self, obj):
        sampleInfoForms = SampleInfoForm.objects.filter(subproject__id=obj.subProject.id)
        return ["%s %s"%(sampleInfoForm.sample_receiver.last_name,sampleInfoForm.sample_receiver.first_name) for sampleInfoForm in sampleInfoForms]
    sample_receiver.short_description = '样品接收人'

    def arrive_time(self, obj):
        sampleInfoForms = SampleInfoForm.objects.filter(subproject__id=obj.subProject.id)
        return [sampleInfoForm.arrive_time for sampleInfoForm in sampleInfoForms]
    arrive_time.short_description = '样品接收时间'

    def get_list_display_links(self, request, list_display):
        return ['ext_number']

    actions = ['make_ExtSubmit_submit', ]

    def get_object(self, request, object_id, from_field=None):

        self.obj = super(ExtSubmitAdmin,self).get_object(request,object_id)

        return self.obj

    def formfield_for_manytomany(self, db_field, request,**kwargs):

        if db_field.name == "sample" and getattr(self,"obj",None):

            sampleinfoform = self.obj.subProject.sampleInfoForm.all()

            for i in sampleinfoform:
                kwargs["queryset"] = SampleInfo.objects.filter(sampleinfoform=i)

        return super(ExtSubmitAdmin, self).formfield_for_manytomany(db_field, request, **kwargs)

    def make_ExtSubmit_submit(self, request, queryset):
        """
        提交提取的表单
        """
        n = 0  #可以确认
        un = 0 #无法确认
        sn = 0 #已经确认
        for obj in queryset:
            if obj.is_submit:
                sn = sn + 1
            elif not obj.ext_start_date:
                un = un + 1
            else:
                n = n + 1
                obj.is_submit = True
                id = obj.subProject.id
                project = SubProject.objects.filter(id=id).first()
                if project.is_status < 2:
                    project.is_status = 2
                    project.save()
                # if obj.subProject.is_status < 2:
                #     SubProject.objects.filter(sub_number = obj.subProject).update(is_status = 2)
                # obj.subProject.save()
                # print(obj.subProject.is_status)
                extExecute = lims_ExtExecute.objects.create(extSubmit=obj)
                sampleInfos = SampleInfo.objects.filter(id__in = [i.id for i in obj.sample.all()])
                for sampleInfo in sampleInfos:
                    if "_" in sampleInfo.color_code:
                        sampleInfo.color_code = "重抽提（已执行）_" + sampleInfo.color_code[-1]
                    sampleInfoExt = lims_SampleInfoExt.objects.create(extExecute=extExecute)
                    sampleInfoExt.unique_code = sampleInfo.unique_code
                    sampleInfoExt.sample_number = sampleInfo.sample_number
                    sampleInfoExt.sample_name = sampleInfo.sample_name
                    sampleInfoExt.species = sampleInfo.sample_species
                    sampleInfoExt.sample_type = sampleInfo.sample_type
                    sampleInfoExt.save()
                obj.save()
        self.message_user(request, '选中数量：%s, 完成确定的数量：%s, 无法完成确定的数量：%s, 已经确定过的数量：%s'%(queryset.count(),n,un,sn), level=messages.ERROR)
        # 新增抽提的时候，给实验发钉钉通知
        self.send_group_message("编号{0}的抽提下单完成------，抽提下单人员:{1}".format(obj.ext_number, obj.project_manager),
                                "chat62dbddc59ef51ae0f4a47168bdd2a65b")
        print(self.send_dingtalk_result)
    make_ExtSubmit_submit.short_description = '提交提取任务'

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = self.readonly_fields
        if obj:
            if obj.is_submit:
                readonly_fields = ['subProject', 'ext_number', 'ext_start_date', 'sample_count',
                                   'note','sample_receiver', 'contract_number', 'sub_project_name', 'contacts', 'partner_company', 'arrive_time']
        return readonly_fields

    def get_queryset(self, request):
        qs = super(ExtSubmitAdmin, self).get_queryset(request)
        # 普通项目管理只能看到自己的下任务,其他的有权限的人可以看到所有的任务
        groups = Group.objects.filter(user__id = request.user.id)
        if len(groups) >= 1:
            for i in groups:
                if i.name == "项目管理":
                    return qs.filter(project_manager=request.user)
                else:
                    return qs
        else:
            return qs

    def get_list_filter(self, request):
        # 过滤器，过滤时间
        groups = Group.objects.filter(user__id=request.user.id)
        # if len(groups) >= 1:
        return [('ext_start_date', DateRangeFilter), ]


        # 更改修改表单里的按钮
    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        add = object_id is None
        if add:
            pass
        else:
            obj = ExtSubmit.objects.get(pk=object_id)
            if obj:
                if obj.is_submit:
                    extra_context['show_delete'] = False
                    extra_context['show_save_and_add_another'] = False
                    extra_context['show_save'] = False
                    extra_context['show_save_as_new'] = False
                    extra_context['show_save_and_continue'] = False

        return super(ExtSubmitAdmin, self).change_view(request, object_id, form_url, extra_context=extra_context)

    def save_model(self, request, obj, form, change):
        if not obj.ext_number:
            ext_number = creat_uniq_number(request, ExtSubmit, 'Ext')
            obj.ext_number = ext_number
        if not obj.project_manager:
            obj.project_manager = request.user
        super(ExtSubmitAdmin, self).save_model(request, obj, form, change)

        if ExtSubmit.objects.all().count() == 0:
            obj.id = "1"
            obj.sample_count = obj.sample.all().count()
            obj.save()
        else:
            obj.id = obj.id
            obj.sample_count = obj.sample.all().count()
            obj.save()

        # if obj.subProject.is_status < 13:
        #     obj.save()
        # elif obj.subProject.is_status == 13:
        #     raise Exception("该子项目已经完成，请选择其他子项目")
        # else:
        #     raise Exception("该子项目已经中止，请选择其他子项目")
        super().save_model(request, obj, form, change)


# 建库提交表
class LibSubmitForm(forms.ModelForm):
    # pass
    class Meta:
        model = LibSubmit
        fields = "__all__"

    def clean_subProject(self):
        subProject = self.cleaned_data['subProject']
        if subProject.is_status == 13:
            raise forms.ValidationError("该子项目已经完成，请选择其他子项目")
        elif subProject.is_status == 14:
            raise forms.ValidationError("该子项目已经中止，请选择其他子项目")
        return self.cleaned_data['subProject']


# 建库提交管理
class LibSubmitAdmin(admin.ModelAdmin,NotificationMixin):
    form = LibSubmitForm
    appkey = DINGTALK_APPKEY
    appsecret = DINGTALK_SECRET
    list_display = ['subProject', 'lib_number', 'customer_sample_count', 'lib_start_date', 'customer_confirmation_time',
                    # 'contract_count', 'project_count',
                    'is_submit', 'note', ]
    filter_horizontal = ('sample',)
    fieldsets = (
        ('合同信息',{
            'fields':(('contacts','contract_number','partner_company',),
                      ('subProject','sub_project_name',),)
        }),
        ('任务信息',{
            'fields':('lib_number', 'sample', 'customer_sample_count', 'lib_start_date',
                      'customer_confirmation_time', ('note', ),)
        })
    )

    readonly_fields =  ['lib_number','contract_number', 'sub_project_name', 'contacts', 'partner_company','customer_sample_count', ]
    search_fields = ['subProject__sub_number', 'lib_number', 'customer_sample_count', 'lib_start_date',
                     'customer_confirmation_time', 'note', ]
    autocomplete_fields = ('subProject',)
    list_per_page = 50
    def contacts(self, obj):
        return obj.subProject.contract.contacts
    contacts.short_description = '合同联系人姓名'

    def contract_number(self, obj):
        return obj.subProject.contract.contract_number
    contract_number.short_description = '合同号'

    def partner_company(self, obj):
        return obj.subProject.contract.partner_company
    partner_company.short_description = '合同单位'

    def sub_project_name(self, obj):
        return obj.subProject.sub_project
    sub_project_name.short_description = '子项目名称'

    def get_list_display_links(self, request, list_display):
        return ['lib_number']

    actions = ['make_LibSubmit_submit', ]

    def get_object(self, request, object_id, from_field=None):

        self.obj = super(LibSubmitAdmin, self).get_object(request, object_id)

        return self.obj

    def formfield_for_manytomany(self, db_field, request, **kwargs):

        if db_field.name == "sample" and getattr(self, "obj", None):

            sampleinfoform = self.obj.subProject.sampleInfoForm.all()

            for i in sampleinfoform:
                kwargs["queryset"] = SampleInfo.objects.filter(sampleinfoform=i)
        return super(LibSubmitAdmin, self).formfield_for_manytomany(db_field, request, **kwargs)

    def make_LibSubmit_submit(self, request, queryset):
        """
        提交建库的表单
        """
        n = 0  #可以确认
        un = 0 #无法确认
        sn = 0 #已经确认
        for obj in queryset:
            if obj.is_submit:
                sn = sn + 1
            elif not obj.lib_start_date:
                un = un + 1
            else:
                n = n + 1
                obj.is_submit = True
                id = obj.subProject.id
                project = SubProject.objects.filter(id=id).first()
                if project.is_status < 5:
                    project.is_status = 5
                    project.save()
                # if obj.subProject.is_status < 5:
                #     SubProject.objects.filter(sub_number=obj.subProject).update(is_status=5)
                # obj.subProject.save()
                libExecute = lims_LibExecute.objects.create(libSubmit=obj)
                sampleInfos = SampleInfo.objects.filter(id__in=[i.id for i in obj.sample.all()])
                for sampleInfo in sampleInfos:
                    if "_" in sampleInfo.color_code:
                        sampleInfo.color_code = "重建库（已执行）_" + sampleInfo.color_code[-1]
                    sampleInfoLib = lims_SampleInfoLib.objects.create(libExecute=libExecute)
                    sampleInfoLib.unique_code = sampleInfo.unique_code
                    sampleInfoLib.sample_number = sampleInfo.sample_number
                    sampleInfoLib.sample_name = sampleInfo.sample_name
                    sampleInfoLib.save()
                obj.save()
        self.message_user(request, '选中数量：%s, 完成确定的数量：%s, 无法完成确定的数量：%s, 已经确定过的数量：%s' % (queryset.count(), n, un, sn),
                          level=messages.ERROR)
        # 新增建库的时候，给实验发钉钉通知
        self.send_group_message("编号{0}的建库下单完成------，建库下单人员:{1}".format(obj.lib_number, obj.project_manager),
                                "chat62dbddc59ef51ae0f4a47168bdd2a65b")
        print(self.send_dingtalk_result)
    make_LibSubmit_submit.short_description = '提交建库任务'

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = self.readonly_fields
        if obj:
            if obj.is_submit:
                readonly_fields = ['lib_number','subProject', 'sample', 'lib_number', 'lib_start_date', 'customer_confirmation_time',
                                   'customer_sample_count', 'note', 'contract_number', 'sub_project_name', 'contacts', 'partner_company']
        return readonly_fields

    def get_queryset(self, request):
        qs = super(LibSubmitAdmin, self).get_queryset(request)
        # 普通项目管理只能看到自己的下任务,其他的有权限的人可以看到所有的任务
        groups = Group.objects.filter(user__id = request.user.id)
        if len(groups) >= 1:
            for i in groups:
                if i.name == "项目管理":
                    return qs.filter(project_manager=request.user)
                else:
                    return qs
        else:
            return qs

    def get_list_filter(self, request):
        # 过滤器，过滤时间
        groups = Group.objects.filter(user__id=request.user.id)
        # if len(groups) >= 1:
        return [('lib_start_date', DateRangeFilter), ('customer_confirmation_time', DateRangeFilter), ]

        # 更改修改表单里的按钮
    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        add = object_id is None
        if add:
            pass
        else:
            obj = LibSubmit.objects.get(pk=object_id)
            if obj:
                if obj.is_submit:
                    extra_context['show_delete'] = False
                    extra_context['show_save_and_add_another'] = False
                    extra_context['show_save'] = False
                    extra_context['show_save_as_new'] = False
                    extra_context['show_save_and_continue'] = False
        return super(LibSubmitAdmin, self).change_view(request, object_id, form_url, extra_context=extra_context)

    def save_model(self, request, obj, form, change):
        if not obj.lib_number:
            lib_number = creat_uniq_number(request, LibSubmit, 'Lib')
            obj.lib_number = lib_number
        if not obj.project_manager:
            obj.project_manager = request.user
        super(LibSubmitAdmin, self).save_model(request, obj, form, change)
        if LibSubmit.objects.all().count() == 0:
            obj.id = "1"
            obj.customer_sample_count = obj.sample.all().count()
        else:
            obj.id = obj.id
            obj.customer_sample_count = obj.sample.all().count()
            obj.save()
        # if obj.subProject.is_status < 13:
        #     obj.save()
        # elif obj.subProject.is_status == 13:
        #     raise Exception("该子项目已经完成，请选择其他子项目")
        # else:
        #     raise Exception("该子项目已经中止，请选择其他子项目")
        super().save_model(request, obj, form, change)


# 测序提交表
class SeqSubmitForm(forms.ModelForm):
    # pass
    class Meta:
        model = SeqSubmit
        fields = "__all__"

    def clean_subProject(self):
        subProject = self.cleaned_data['subProject']
        if subProject.is_status == 13:
            raise forms.ValidationError("该子项目已经完成，请选择其他子项目")
        elif subProject.is_status == 14:
            raise forms.ValidationError("该子项目已经中止，请选择其他子项目")
        return self.cleaned_data['subProject']


# 测序提交管理
class SeqSubmitAdmin(admin.ModelAdmin,NotificationMixin):
    form = SeqSubmitForm
    appkey = DINGTALK_APPKEY
    appsecret = DINGTALK_SECRET
    list_display = ['subProject', 'seq_number', 'customer_sample_count', 'seq_start_date', 'customer_confirmation_time',
                    'pooling_excel',
                    # 'contract_count',  'project_count',
                    # 'sample_count',
                    'is_submit', 'note',
                    ]
    filter_horizontal = ('sample',)

    fieldsets = (
        ('合同信息',{
            'fields':(('contacts','contract_number','partner_company',),
                      ('subProject','sub_project_name',),)
        }),
        ('任务信息',{
            'fields':('seq_number', 'sample', 'customer_sample_count',
                      ('seq_start_date', 'customer_confirmation_time', 'pooling_excel',),
                      ('note', ),)
        })
    )

    readonly_fields = ['contract_number', 'sub_project_name', 'contacts', 'partner_company','seq_number', 'customer_sample_count',]
    search_fields = ['subProject__sub_number', 'seq_number', 'customer_sample_count', 'seq_start_date',
                     'customer_confirmation_time', 'note', ]
    autocomplete_fields = ('subProject',)
    list_per_page = 50
    def contacts(self, obj):
        return obj.subProject.contract.contacts

    contacts.short_description = '合同联系人姓名'

    def contract_number(self, obj):
        return obj.subProject.contract.contract_number

    contract_number.short_description = '合同号'

    def partner_company(self, obj):
        return obj.subProject.contract.partner_company

    partner_company.short_description = '合同单位'

    def sub_project_name(self, obj):
        return obj.subProject.sub_project

    sub_project_name.short_description = '子项目名称'

    def get_list_display_links(self, request, list_display):
        return ['seq_number']

    actions = ['make_SeqSubmit_submit', ]

    def get_object(self, request, object_id, from_field=None):

        self.obj = super(SeqSubmitAdmin, self).get_object(request, object_id)

        return self.obj

    def formfield_for_manytomany(self, db_field, request, **kwargs):

        if db_field.name == "sample" and getattr(self, "obj", None):

            sampleinfoform = self.obj.subProject.sampleInfoForm.all()

            for i in sampleinfoform:
                kwargs["queryset"] = SampleInfo.objects.filter(sampleinfoform=i)
        return super(SeqSubmitAdmin, self).formfield_for_manytomany(db_field, request, **kwargs)

    def make_SeqSubmit_submit(self, request, queryset):
        """
        提交测序的表单
        """
        n = 0  # 可以确认
        un = 0  # 无法确认
        sn = 0  # 已经确认
        for obj in queryset:
            if not obj.pooling_excel:
                # raise forms.ValidationError('请上传pooling表')
                self.message_user(request, '子项目编号：%s。测序号：%s。必须上传pooling表' % (obj.subProject, obj.seq_number), level=messages.ERROR)
            else:
                if obj.is_submit:
                    sn = sn + 1
                elif not obj.seq_start_date:
                    un = un + 1
                else:
                    n = n + 1
                    obj.is_submit = True
                    id = obj.subProject.id
                    project = SubProject.objects.filter(id=id).first()
                    if project.is_status < 8:
                        project.is_status = 8
                        project.save()
                    # if obj.subProject.is_status < 8:
                    #     SubProject.objects.filter(sub_number=obj.subProject).update(is_status=8)
                    # obj.subProject.save()
                    seqExecute = lims_SeqExecute.objects.create(seqSubmit=obj)
                    sampleInfos = SampleInfo.objects.filter(id__in=[i.id for i in obj.sample.all()])
                    for sampleInfo in sampleInfos:
                        if "_" in sampleInfo.color_code:
                            sampleInfo.color_code = "重测序（已执行）_" + sampleInfo.color_code[-1]
                        sampleInfoseq = lims_SampleInfoSeq.objects.create(seqExecute=seqExecute)
                        sampleInfoseq.unique_code = sampleInfo.unique_code
                        sampleInfoseq.sample_number = sampleInfo.sample_number
                        sampleInfoseq.sample_name = sampleInfo.sample_name
                        sampleInfoseq.save()
                    obj.save()
                self.message_user(request, '选中数量：%s, 完成确定的数量：%s, 无法完成确定的数量：%s, 已经确定过的数量：%s' % (queryset.count(), n, un, sn),
                                  level=messages.ERROR)
                # 新增测序的时候，给实验发钉钉通知
                self.send_group_message("编号{0}的测序下单完成------，测序下单人员:{1}".format(obj.seq_number, obj.project_manager),
                                        "chat62dbddc59ef51ae0f4a47168bdd2a65b")
                print(self.send_dingtalk_result)
    make_SeqSubmit_submit.short_description = '提交测序任务'

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = self.readonly_fields
        if obj:
            if obj.is_submit:
                readonly_fields = ['subProject', 'sample', 'seq_number', 'seq_start_date', 'customer_confirmation_time',
                                   'customer_sample_count', 'pooling_excel', 'note','contract_number', 'sub_project_name', 'contacts', 'partner_company' ]
        return readonly_fields

    def get_queryset(self, request):
        qs = super(SeqSubmitAdmin, self).get_queryset(request)
        # 普通项目管理只能看到自己的下任务,其他的有权限的人可以看到所有的任务
        groups = Group.objects.filter(user__id = request.user.id)
        if len(groups) >= 1:
            for i in groups:
                if i.name == "项目管理":
                    return qs.filter(project_manager=request.user)
                else:
                    return qs
        else:
            return qs

    def get_list_filter(self, request):
        # 过滤器过滤时间
        groups = Group.objects.filter(user__id=request.user.id)
        # if len(groups) >= 1:
        return [('seq_start_date', DateRangeFilter), ('customer_confirmation_time', DateRangeFilter), ]

        # 更改修改表单里的按钮
    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        add = object_id is None
        if add:
            pass
        else:
            obj = SeqSubmit.objects.get(pk=object_id)
            if obj:
                if obj.is_submit:
                    extra_context['show_delete'] = False
                    extra_context['show_save_and_add_another'] = False
                    extra_context['show_save'] = False
                    extra_context['show_save_as_new'] = False
                    extra_context['show_save_and_continue'] = False
        return super(SeqSubmitAdmin, self).change_view(request, object_id, form_url, extra_context=extra_context)

    def save_model(self, request, obj, form, change):
        if not obj.seq_number:
            seq_number = creat_uniq_number(request, SeqSubmit, 'Seq')
            obj.seq_number = seq_number
        if not obj.project_manager:
            obj.project_manager = request.user
        super(SeqSubmitAdmin, self).save_model(request, obj, form, change)
        if SeqSubmit.objects.all().count() == 0:
            obj.id = "1"
            obj.customer_sample_count = obj.sample.all().count()
        else:
            obj.id = obj.id
            obj.customer_sample_count = obj.sample.all().count()
            obj.save()
        # if obj.subProject.is_status < 13:
        #     obj.save()
        # elif obj.subProject.is_status == 13:
        #     raise Exception("该子项目已经完成，请选择其他子项目")
        # else:
        #     raise Exception("该子项目已经中止，请选择其他子项目")
        super().save_model(request, obj, form, change)


class AnaSubmitForm(forms.ModelForm):
    pass
    # class Meta:
    #     model = AnaSubmit
    #     fields = "__all__"
    #
    # def clean_subProject(self):
    #     subProject = self.cleaned_data['subProject']
    #     if subProject.is_status == 13:
    #         raise forms.ValidationError("该子项目已经完成，请选择其他子项目")
    #     elif subProject.is_status == 14:
    #         raise forms.ValidationError("该子项目已经中止，请选择其他子项目")
    #     return self.cleaned_data['subProject']


# 分析提交管理
class AnaSubmitAdmin(admin.ModelAdmin,NotificationMixin):
    form = AnaSubmitForm
    appkey = DINGTALK_APPKEY
    appsecret = DINGTALK_SECRET
    list_display = ['ana_number', 'ana_start_date', 'depart_data_path', 'confirmation_sheet',
                    # 'contract_count',
                    # 'project_count',
                    'is_submit', 'note','file_link' ]

    fieldsets = (
        ('合同信息',{
            'fields':(('contacts','contract_number','partner_company',),)
        }),
        ('任务信息',{
            'fields':('ana_number', ('subProject',), 'ana_start_date',
              'depart_data_path', 'confirmation_sheet',('note'),)
        })
    )
    readonly_fields = ['contract_number', 'contacts', 'partner_company', 'ana_number',]
    filter_horizontal = ('subProject',)
    search_fields = ['ana_number', 'ana_start_date', 'note', ]
    list_per_page = 50
    def contacts(self, obj):
        contracts = Contract.objects.filter(pk__in = [i.contract.id for i in obj.subProject.all()])
        return "\t".join([contract.contacts for contract in contracts])
    contacts.short_description = '合同联系人姓名'

    def contract_number(self, obj):
        contracts = Contract.objects.filter(pk__in=[i.contract.id for i in obj.subProject.all()])
        return "\t".join([contract.contract_number for contract in contracts])
    contract_number.short_description = '合同号'

    def partner_company(self, obj):
        contracts = Contract.objects.filter(pk__in=[i.contract.id for i in obj.subProject.all()])
        return "\t".join([contract.partner_company for contract in contracts])
    partner_company.short_description = '合同单位'

    def get_list_display_links(self, request, list_display):
        return ['ana_number']

    actions = ['make_AnaSubmit_submit', ]

    def make_AnaSubmit_submit(self, request, queryset):
        """
        提交分析的表单
        """
        n = 0  # 可以确认
        un = 0  # 无法确认
        sn = 0  # 已经确认
        for obj in queryset:
            if obj.is_submit:
                sn = sn + 1
            elif not obj.ana_start_date:
                un = un + 1
            elif not obj.confirmation_sheet:
                un = un + 1
            elif not obj.depart_data_path:
                un = un + 1
            else:
                n = n + 1
                print("4")
                print(obj.is_submit)
                obj.is_submit = True
                for subProject in obj.subProject.all():
                    subProject_old = SubProject.objects.get(id=subProject.id)
                    if subProject_old.is_status < 11:
                        subProject_old.is_status = 11
                    subProject_old.save()
                anaExecute = am_anaExecute.objects.create(ana_submit=obj)
                obj.save()
        self.message_user(request, '选中数量：%s, 完成确定的数量：%s, 无法完成确定的数量：%s, 已经确定过的数量：%s' % (queryset.count(), n, un, sn),
                          level=messages.ERROR)
        # 新增分析的时候，给实验发钉钉通知
        self.send_group_message("编号{0}的分析下单完成------，分析下单人员:{1}".format(obj.ana_number, obj.project_manager),
                                "chat62dbddc59ef51ae0f4a47168bdd2a65b")
        print(self.send_dingtalk_result)
    make_AnaSubmit_submit.short_description = '提交分析任务'

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = self.readonly_fields
        if obj:
            if obj.is_submit:
                readonly_fields = ['subProject', 'ana_number', 'ana_start_date', 'note', 'sample_count',
                                   'depart_data_path', 'confirmation_sheet','contract_number', 'sub_project_name', 'contacts', 'partner_company' ]
        return readonly_fields

    def get_queryset(self, request):
        qs = super(AnaSubmitAdmin, self).get_queryset(request)
        # 普通项目管理只能看到自己的下任务,其他的有权限的人可以看到所有的任务
        groups = Group.objects.filter(user__id = request.user.id)
        if len(groups) >= 1:
            for i in groups:
                if i.name == "项目管理":
                    return qs.filter(project_manager=request.user)
                else:
                    return qs
        else:
            return qs

    def get_list_filter(self, request):
        # 过滤器过滤时间
        groups = Group.objects.filter(user__id=request.user.id)
        # if len(groups) >= 1:
        return [('ana_start_date', DateRangeFilter), ]

        # 更改修改表单里的按钮
    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        add = object_id is None
        if add:
            pass
        else:
            obj = AnaSubmit.objects.get(pk=object_id)
            if obj:
                if obj.is_submit:
                    extra_context['show_delete'] = False
                    extra_context['show_save_and_add_another'] = False
                    extra_context['show_save'] = False
                    extra_context['show_save_as_new'] = False
                    extra_context['show_save_and_continue'] = False
        return super(AnaSubmitAdmin, self).change_view(request, object_id, form_url, extra_context=extra_context)

    def save_model(self, request, obj, form, change):
        if not obj.ana_number:
            ana_number = creat_uniq_number(request, AnaSubmit, 'Ana')
            obj.ana_number = ana_number
            obj.project_manager = request.user
        super(AnaSubmitAdmin, self).save_model(request, obj, form, change)
        for subProject in obj.subProject.all():
            subProject_status = SubProject.objects.get(id=subProject.id)
            if obj.subProject.is_status < 13:
                obj.save()
            elif obj.subProject.is_status == 13:
                raise Exception("该子项目已经完成，请选择其他子项目")
            elif obj.subProject.is_status == 14:
                raise Exception("该子项目已经中止，请选择其他子项目")
            subProject_status.save()


BMS_admin_site.register(SubProject, SubProjectAdmin)
BMS_admin_site.register(ExtSubmit, ExtSubmitAdmin)
BMS_admin_site.register(LibSubmit, LibSubmitAdmin)
BMS_admin_site.register(SeqSubmit, SeqSubmitAdmin)
BMS_admin_site.register(AnaSubmit, AnaSubmitAdmin)
