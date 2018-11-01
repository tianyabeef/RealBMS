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

def creat_uniq_number(request,instance,name):
    if instance.objects.all().count() == 0:
        uniq_number = request.user.username + \
                               '-' + str(datetime.datetime.now().year) + \
                               str(datetime.datetime.now().month) + '-'+name+'-' + \
                               "1"
    else:
        uniq_number = request.user.username + \
                               '-' + str(datetime.datetime.now().year) + \
                               str(datetime.datetime.now().month) + '-'+name+'-' + \
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
                extSubmit = ExtSubmit.objects.create(subProject=obj, sample_count=obj.sample_count, ext_number=ext_number)
                for sampleInfoForm in sampleInfoForms:
                    sampleInfos = SampleInfo.objects.filter(sampleinfoform__id=sampleInfoForm.id)
                    for sampleInfo in sampleInfos:
                        extSubmit.sample.add(sampleInfo)
            elif i == 1:
                sampleInfoForms = SampleInfoForm.objects.filter(subproject__id=obj.id)
                libSubmit = LibSubmit.objects.create(subProject=obj, customer_sample_count=obj.sample_count, lib_number=lib_number)
                for sampleInfoForm in sampleInfoForms:
                    sampleInfos = SampleInfo.objects.filter(sampleinfoform__id=sampleInfoForm.id)
                    for sampleInfo in sampleInfos:
                        libSubmit.sample.add(sampleInfo)
            elif i == 2:
                sampleInfoForms = SampleInfoForm.objects.filter(subproject__id=obj.id)
                seqSubmit = SeqSubmit.objects.create(subProject=obj, customer_sample_count=obj.sample_count, seq_number=seq_number)
                for sampleInfoForm in sampleInfoForms:
                    sampleInfos = SampleInfo.objects.filter(sampleinfoform__id=sampleInfoForm.id)
                    for sampleInfo in sampleInfos:
                        seqSubmit.sample.add(sampleInfo)
            elif i == 3:
                sampleInfoForms = SampleInfoForm.objects.filter(subproject__id=obj.id)
                anaSubmit = AnaSubmit.objects.create(subProject=obj, sample_count=obj.sample_count, ana_number=ana_number)
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
                    extra_context['show_save_and_add_another'] = False
                    extra_context['show_save'] = False
                    extra_context['show_save_as_new'] = False
                    extra_context['show_save_and_continue'] = False

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


# 提取提交表
class ExtSubmitForm(forms.ModelForm):
    pass


# 提取提交管理
class ExtSubmitAdmin(admin.ModelAdmin):
    # form = ExtSubmitForm
    list_display = ['subProject', 'ext_number', 'sample_count', 'ext_start_date', 'is_submit', 'note', ]
    filter_horizontal = ('sample',)
    fields = ('subProject', 'ext_number', 'sample', 'sample_count',
              'ext_start_date',
              # 'is_submit',
              'note')

    # raw_id_fields = ['subProject', ]

    def get_list_display_links(self, request, list_display):
        return ['ext_number']

    actions = ['make_ExtSubmit_submit', ]

    def make_ExtSubmit_submit(self, request, queryset):
        """
        提交提取的表单
        """
        n = 0
        for obj in queryset:
            if (obj.is_submit == False) and obj.ext_start_date:
                obj.is_submit = True
                obj.save()
            else:
                n += 1

    make_ExtSubmit_submit.short_description = '提交提取的表单'

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = self.readonly_fields
        if obj:
            if obj.is_submit:
                readonly_fields = ['subProject', 'sample', 'ext_number', 'ext_start_date', 'sample_count',
                                   'note', ]
        return readonly_fields

    def save_model(self, request, obj, form, change):
        if obj.is_submit:
            obj.subProject.is_status = 2
            obj.subProject.save()
        else:
            pass
        super(ExtSubmitAdmin, self).save_model(request, obj, form, change)


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
    fields = ('subProject', 'lib_number', 'sample', 'lib_start_date',
              'customer_confirmation_time', 'customer_sample_count',
              # 'is_submit',
              'note',)

    # raw_id_fields = ['subProject', ]

    def get_list_display_links(self, request, list_display):
        return ['lib_number']

    def sample_count(self, obj):
        pass
        # return obj.sample.all().count()

    sample_count.short_description = '样品数'

    actions = ['make_LibSubmit_submit', ]

    def make_LibSubmit_submit(self, request, queryset):
        """
        提交建库的表单
        """
        n = 0
        for obj in queryset:
            if (obj.is_submit == False) and obj.lib_start_date:
                obj.is_submit = True
                obj.save()
            else:
                n += 1

    make_LibSubmit_submit.short_description = '建库提取的表单'

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = self.readonly_fields
        if obj:
            if obj.is_submit:
                readonly_fields = ['subProject', 'sample', 'lib_number', 'lib_start_date', 'customer_confirmation_time',
                                   'customer_sample_count', 'note', ]
        return readonly_fields

    def save_model(self, request, obj, form, change):
        if obj.is_submit:
            obj.subProject.is_status = 5
            obj.subProject.save()
        else:
            pass
        super(LibSubmitAdmin, self).save_model(request, obj, form, change)


# 测序提交表
class SeqSubmitForm(forms.ModelForm):
    pass


# 测序提交管理
class SeqSubmitAdmin(admin.ModelAdmin):
    # form = SeqSubmitForm
    list_display = ['subProject', 'seq_number', 'customer_sample_count', 'seq_start_date', 'customer_confirmation_time',
                    'pooling_excel',
                    # 'contract_count',  'project_count',
                    # 'sample_count',
                    'customer_sample_count', 'is_submit', 'note',
                    ]
    filter_horizontal = ('sample',)
    fields = ('subProject', 'seq_number', 'sample', 'seq_start_date', 'customer_confirmation_time',
              'customer_sample_count', 'pooling_excel',
              # 'is_submit',
              'note',)

    # raw_id_fields = ['subProject', ]

    def get_list_display_links(self, request, list_display):
        return ['seq_number']

    actions = ['make_SeqSubmit_submit', ]

    def make_SeqSubmit_submit(self, request, queryset):
        """
        提交测序的表单
        """
        n = 0
        for obj in queryset:
            if (obj.is_submit == False) and obj.seq_start_date:
                obj.is_submit = True
                obj.save()
            else:
                n += 1

    make_SeqSubmit_submit.short_description = '测序提取的表单'

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = self.readonly_fields
        if obj:
            if obj.is_submit:
                readonly_fields = ['subProject', 'sample', 'seq_number', 'seq_start_date', 'customer_confirmation_time',
                                   'customer_sample_count', 'pooling_excel', 'note', ]
        return readonly_fields

    def save_model(self, request, obj, form, change):
        if obj.is_submit:
            obj.subProject.is_status = 8
            obj.subProject.save()
        else:
            pass
        super(SeqSubmitAdmin, self).save_model(request, obj, form, change)


# 分析提交表
class AnaSubmitForm(forms.ModelForm):
    # pass

    subProject = forms.ModelChoiceField(queryset=SubProject.objects.all())

    class Meta():
        fields = ('subProject',)
        model = SubProject
        labels = {'username': 'Email',
                  'subProject': 'subProject'}

    # def save(self, commit=True):
    #     if not commit:
    #         raise NotImplementedError("Can't create User and Userextended without database save")
    #     user = super(UserCreateForm, self).save(commit=True)
    #     user_profile = Userextended(user=user, cristin=self.cleaned_data['cristin'],
    #                                 rolle=self.cleaned_data['rolle'])
    #     user_profile.save()
    #     return user

    # def save(self, commit=True):
    #     if not commit:
    #         raise NotImplementedError("Can't create User and Userextended without database save")
    #     SubProject = super(AnaSubmitForm, self).save(is_submit=True)
    #     SubProject = AnaSubmit(user=user, cristin=self.cleaned_data['cristin'])
    #     SubProject_is_status.save()
    #     SubProject_is_status.subProject.add(self.cleaned_data['subProject'])
    #     SubProject_is_status.save()
    #     return SubProject

# 分析提交管理
class AnaSubmitAdmin(admin.ModelAdmin):
    # form = AnaSubmitForm
    list_display = ['ana_number', 'sample_count', 'ana_start_date', 'depart_data_path', 'data_analysis',
                    # 'contract_count',
                    # 'project_count',
                    'is_submit', 'note', ]
    fields = ('ana_number', 'subProject', 'note', 'sample_count', 'ana_start_date',
              'is_submit',
              'depart_data_path', 'data_analysis')
    # raw_id_fields = ['subProject', ]
    filter_horizontal = ('subProject',)

    def get_list_display_links(self, request, list_display):
        return ['ana_number']

    actions = ['make_AnaSubmit_submit', ]

    def make_AnaSubmit_submit(self, request, queryset):
        """
        提交分析的表单
        """
        n = 0
        for obj in queryset:
            if (obj.is_submit == False) and obj.ana_start_date:
                obj.is_submit = True
                obj.save()
            else:
                n += 1

    make_AnaSubmit_submit.short_description = '分析提取的表单'

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = self.readonly_fields
        if obj:
            if obj.is_submit:
                readonly_fields = ['subProject', 'ana_number', 'ana_start_date', 'note', 'sample_count',
                                   'depart_data_path', 'data_analysis', ]
        return readonly_fields

    def save_model(self, request, obj, form, change):
        if obj.is_submit:
            # is_submits = obj.save(is_submit=False)
            obj.subProject.is_status = 11
            obj.subProject.save()
            obj.save_m2m()
        else:
            pass
        super(AnaSubmitAdmin, self).save_model(request, obj, form, change)

    # print(SubProject.objects.get(pk=1))
    # entry = SubProject.objects.get(pk=1)
    # joe = SubProject.objects.create(is_status=11)
    # entry.SubProject.add(joe)
    # super(AnaSubmitAdmin, self).save_model(request, obj, form, change)


BMS_admin_site.register(SubProject, SubProjectAdmin)
BMS_admin_site.register(ExtSubmit, ExtSubmitAdmin)
BMS_admin_site.register(LibSubmit, LibSubmitAdmin)
BMS_admin_site.register(SeqSubmit, SeqSubmitAdmin)
BMS_admin_site.register(AnaSubmit, AnaSubmitAdmin)
