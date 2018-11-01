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

class SubProjectForm(forms.ModelForm):
    def clean_sample_count(self):
        sample_count = self.cleaned_data['sample_count']
        if sample_count == 0:
            raise forms.ValidationError('样品数量不能为0，请留空')
        return self.cleaned_data['sample_count']

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


def create_submit_table(obj, states):
    ##新建执行表
    for i, v in enumerate(states):
        if v == True:
            if i == 0:
                sampleInfoForms = SampleInfoForm.objects.filter(subproject__id=obj.id)
                extSubmit = ExtSubmit.objects.create(subProject=obj, sample_count=obj.sample_count)
                for sampleInfoForm in sampleInfoForms:
                    sampleInfos = SampleInfo.objects.filter(sampleinfoform__id=sampleInfoForm.id)
                    for sampleInfo in sampleInfos:
                        extSubmit.sample.add(sampleInfo)
            elif i == 1:
                sampleInfoForms = SampleInfoForm.objects.filter(subproject__id=obj.id)
                libSubmit = LibSubmit.objects.create(subProject=obj, customer_sample_count=obj.sample_count)
                for sampleInfoForm in sampleInfoForms:
                    sampleInfos = SampleInfo.objects.filter(sampleinfoform__id=sampleInfoForm.id)
                    for sampleInfo in sampleInfos:
                        libSubmit.sample.add(sampleInfo)
            elif i == 2:
                sampleInfoForms = SampleInfoForm.objects.filter(subproject__id=obj.id)
                seqSubmit = SeqSubmit.objects.create(subProject=obj, customer_sample_count=obj.sample_count)
                for sampleInfoForm in sampleInfoForms:
                    sampleInfos = SampleInfo.objects.filter(sampleinfoform__id=sampleInfoForm.id)
                    for sampleInfo in sampleInfos:
                        seqSubmit.sample.add(sampleInfo)
            elif i == 3:
                sampleInfoForms = SampleInfoForm.objects.filter(subproject__id=obj.id)
                anaSubmit = AnaSubmit.objects.create(subProject=obj, sample_count=obj.sample_count)
                for sampleInfoForm in sampleInfoForms:
                    sampleInfos = SampleInfo.objects.filter(sampleinfoform__id=sampleInfoForm.id)
                    for sampleInfo in sampleInfos:
                        anaSubmit.sample.add(sampleInfo)
            else:
                pass
            break
class SubProjectAdmin(admin.ModelAdmin):
    # resource_class = ProjectResource
    form = SubProjectForm
    list_display = ('contract_number', 'contract_name', 'sub_number', 'sub_project', 'contacts', 'saleman',
                    'project_manager', 'is_submit', 'status','file_link','is_status')
    list_display_links = ['sub_number', ]
    # list_editable = ['is_confirm']
    # list_filter = ['is_status',StatusListFilter]
    fieldsets = (
        ('合同信息', {
           'fields': (('contract','contract_number', 'contract_name',),
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
        ('关键信息  (注：请审核好以上的所有的信息，再选中确定栏。)', {
            'fields': (('is_submit',),)
        }),
    )
    readonly_fields = ['contract_number', 'contract_name', 'contacts','contacts_phone', 'saleman','company',
                       'project_type','income_notes','customer_name', 'customer_phone', 'service_types',
                       'sample_receiver','arrive_time']
    raw_id_fields = ['contract', ]
    filter_horizontal = ['sampleInfoForm', ]
    # actions = ['make_confirm']
    search_fields = ['contract__contract_number','sub_number']
    # change_list_template = "pm/chang_list_custom.html"

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
        return_content = "款期\t到账日期\t到账金额\n"
        mm_invoices = mm_Invoice.objects.filter(contract__id=obj.contract.id)
        for mm_invoice in mm_invoices:
            fm_invoice = fm_Invoice.objects.get(invoice__id=mm_invoice.id)
            return_content = "%s%s\t%s\t%s\n" % (
            return_content, mm_invoice.get_period_display(), fm_invoice.income_date, fm_invoice.income)
        return return_content
    income_notes.short_description = '到款的记录'

    # 样品表相关信息（样品寄样人，样品寄样人电话，项目类型）
    def customer_name(self, obj):
        sampleInfoForms = SampleInfoForm.objects.filter(subproject__id=obj.id)
        return "\t".join([sampleInfoForm.transform_contact for sampleInfoForm in sampleInfoForms])
    customer_name.short_description = '寄样人姓名'

    def customer_phone(self, obj):
        sampleInfoForms = SampleInfoForm.objects.filter(subproject__id=obj.id)
        return [sampleInfoForm.transform_phone for sampleInfoForm in sampleInfoForms]
    customer_phone.short_description = '寄样联系人电话'

    def service_types(self, obj):
        sampleInfoForms = SampleInfoForm.objects.filter(subproject__id=obj.id)
        return "\t".join([sampleInfoForm.get_project_type_display() for sampleInfoForm in sampleInfoForms])
    service_types.short_description = '项目类型'

    def sample_receiver(self, obj):
        sampleInfoForms = SampleInfoForm.objects.filter(subproject__id=obj.id)
        return ["%s %s"%(sampleInfoForm.sample_receiver.last_name,sampleInfoForm.sample_receiver.first_name) for sampleInfoForm in sampleInfoForms]
    sample_receiver.short_description = '样品接收人'

    def arrive_time(self, obj):
        sampleInfoForms = SampleInfoForm.objects.filter(subproject__id=obj.id)
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
                    return ['is_status', StatusListFilter]
        else:
            return ['is_status', StatusListFilter]

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
                    extra_context['show_save'] = False
                    extra_context['show_save_as_new'] = False
                    extra_context['show_save_and_continue'] = False
                    extra_context['_addanother'] = False
        return super(SubProjectAdmin,self).change_view(request, object_id, form_url, extra_context=extra_context)

    def save_model(self, request, obj, form, change):
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
            print(obj.file_to_start)
            if obj.file_to_start:
                if obj.is_submit:
                    contract = Contract.objects.get(id=obj.contract.id)
                    contract.use_amount = contract.use_amount + project_amount
                    contract.save()
                    #新建执行表单
                    create_submit_table(obj, states)
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
                create_submit_table(obj, states)
            obj.save()









BMS_admin_site.register(SubProject, SubProjectAdmin)
# BMS_admin_site.register(AnaSubmit, AnaSubmitAdmin)
# BMS_admin_site.register(ExtSubmit, ExtSubmitAdmin)
# BMS_admin_site.register(LibSubmit, LibSubmitAdmin)
