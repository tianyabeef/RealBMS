from BMS.admin_bms import BMS_admin_site
from .models import SubProject, ExtSubmit, LibSubmit, AnaSubmit
from django.contrib import admin
from sample.models import SampleInfoForm
from mm.models import Contract
from mm.models import Invoice as mm_Invoice
from fm.models import Invoice as fm_Invoice
from decimal import Decimal
from django.contrib import messages

class SubProjectAdmin(admin.ModelAdmin):
    # resource_class = ProjectResource
    # form = ProjectForm
    list_display = ('contract_number', 'contract_name', 'sub_number', 'sub_project', 'contacts', 'saleman',
                    'project_manager', 'is_submit', 'status','file_to_start',)
    list_display_links = ['sub_number', ]
    # list_editable = ['is_confirm']
    # list_filter = [StatusListFilter]
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
    # search_fields = ['contract__contract_number','id']
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

    # 更改修改表单里的按钮
    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        add = object_id is None
        if add:
            return super(SubProjectAdmin, self).change_view(request, object_id, form_url, extra_context=extra_context)
        else:
            obj = SubProject.objects.get(pk=object_id)
            if obj:
                if obj.is_submit:
                    extra_context['show_delete'] = False
                    extra_context['show_save'] = False
                    extra_context['show_save_as_new'] = False
                    extra_context['show_save_and_continue'] = False
                    extra_context['show_save_and_add_another'] = False
        return super(SubProjectAdmin,self).change_view(request, object_id, form_url, extra_context=extra_context)

    def save_model(self, request, obj, form, change):
        dict = {'a': 1, 'b': 2, 'b': '3'};
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
                    ##
                obj.save()
            else:
                self.message_user(request, '提取启动，必须上传审批文件',level=messages.ERROR)
        else:
            if obj.is_submit:
                contract = Contract.objects.get(id=obj.contract.id)
                contract.use_amount = contract.use_amount + project_amount
                contract.save()
            obj.save()








BMS_admin_site.register(SubProject, SubProjectAdmin)
# BMS_admin_site.register(AnaSubmit, AnaSubmitAdmin)
# BMS_admin_site.register(ExtSubmit, ExtSubmitAdmin)
# BMS_admin_site.register(LibSubmit, LibSubmitAdmin)
