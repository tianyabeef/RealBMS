import datetime
from django.contrib import admin
from django.contrib.auth.models import Group
from import_export import resources
from import_export import fields
from import_export.admin import ImportExportActionModelAdmin
from BMS.admin_bms import BMS_admin_site
from lims.models import SampleInfoExt, ExtExecute, LibExecute,  SampleInfoLib, SampleInfoSeq, SeqExecute

try:
    from django.utils.encoding import force_text
except ImportError:
    from django.utils.encoding import force_unicode as force_text
from sample.models import SampleInfoForm, SampleInfo

#外键样品
class SampleInfoExtInline(admin.StackedInline):
    model = SampleInfoExt
    fieldsets = (
        ['抽提样品信息', {
            'fields': (( 'sample_number',
                        'sample_name','species',
                        ),("is_RNase_processing",'preservation_medium', 'sample_type','sample_used' ),
                       ('sample_rest','density_checked',"volume_checked"),("D260_280","D260_230","DNA_totel","quality_control_conclusion"),"note","is_rebuild"
                       ),
        }]
        ,)
    # fieldsets = [("unique_code","sample_number","sample_name"),"preservation_medium","is_RNase_processing"]

#抽提的导入
class SampleInfoExtResource(resources.ModelResource):
    class Meta:
        model = SampleInfoExt
        skip_unchanged = True
        fields = ('sample_number','sample_used',
        'sample_rest', 'density_checked','volume_checked', 'D260_280', 'D260_230', 'DNA_totel','note','quality_control_conclusion','is_rebuild')
        export_order = ('sample_number','sample_used',
        'sample_rest', 'density_checked','volume_checked', 'D260_280', 'D260_230', 'DNA_totel','note','quality_control_conclusion','is_rebuild')

    def get_export_headers(self):
        return ["样品编号","样品提取用量","样品剩余用量","浓度ng/uL(公司检测)","体积uL(公司检测)"
            ,"D260/280","D260/230","DNA总量","备注","质检结论","选择是否重抽提(0代表不重抽提,1代表重抽提)"]

    def init_instance(self, row=None):
        if not row:
            row = {}
        instance = SampleInfoExt.objects.get(sample_number = row['样品编号'])
        if instance:
            # instance = SampleInfo()
            for attr, value in row.items():
                setattr(instance, attr, value)
            # instance.id = str(int(SampleInfo.objects.latest('id').id)+1)
            instance.sample_used = row['样品提取用量']
            instance.sample_rest = row['样品剩余用量']
            instance.density_checked = row['浓度ng/uL(公司检测)']
            instance.volume_checked = row['体积uL(公司检测)']
            instance.D260_280 = row['D260/280']
            instance.D260_230 = row['D260/230']
            instance.DNA_totel = row['DNA总量']
            instance.note = row['备注']
            instance.quality_control_conclusion = row['质检结论']
            return instance
        else:
            raise Exception("你上传的样品编号有误")

    def get_diff_headers(self):
        return ["样品编号","样品提取用量","样品剩余用量","浓度ng/uL(公司检测)","体积uL(公司检测)"
            ,"D260/280","D260/230","DNA总量","备注","质检结论","选择是否重抽提(0代表不重抽提,1代表重抽提)"]

class ExtExecuteAdmin(ImportExportActionModelAdmin):

    resource_class = SampleInfoExtResource

    list_per_page = 30

    inlines = [SampleInfoExtInline]

    save_as_continue = False

    save_on_top = False

    #多对多不能显示在列表页面
    # list_display = ('extSubmit', 'ext_experimenter', 'ext_end_date', 'note')
    list_display = ('extSubmit',  'ext_end_date', 'note',"is_submit")

    exclude = ("ext_end_date",)

    list_display_links = ('extSubmit',)

    # actions = ["submit_result",]

    # def save_model(self, request, obj, form, change):
    #     if obj.is_submit:

    def get_readonly_fields(self, request, obj=None):
        self.readonly_fields = []
        try:
            if obj.is_submit:
                self.readonly_fields = ('extSubmit','ext_experimenter','upload_file','ext_end_date', 'note',"is_submit",)
                return self.readonly_fields
        except:
            return self.readonly_fields
        return self.readonly_fields
    def save_model(self, request, obj, form, change):
        if obj.is_submit:
            #钉钉
            obj.ext_end_date = datetime.datetime.now()
            pass
        super().save_model(request, obj, form, change)
    #设置实验员不能增加执行任务
    def has_add_permission(self, request):
        try:
            current_group_set = Group.objects.get(user=request.user)
        except:
            return True
        if current_group_set.name == "实验员":
            return False
        else:
            return True

    def get_actions(self, request):
        actions = super().get_actions(request)
        del actions['delete_selected']
        del actions['export_admin_action']
        return actions

#建库操作
class SampleInfoLibResource(resources.ModelResource):
    class Meta:
        model = SampleInfoLib
        skip_unchanged = True
        fields = ('sample_number','lib_code',
        'index', 'lib_volume','lib_concentration', 'lib_total', 'lib_result', 'lib_note','is_rebuild')
        export_order = ('sample_number','lib_code',
        'index', 'lib_volume','lib_concentration', 'lib_total', 'lib_result', 'lib_note','is_rebuild')

    def get_export_headers(self):
        return ["样品编号","文库号","Index","体积uL(文库)","浓度ng/uL(文库)"
            ,"总量ng(文库)","结论(文库)","备注(文库)","选择是否重建库(0代表不重建库,1代表重建库)"]

    def init_instance(self, row=None):
        if not row:
            row = {}
        instance = SampleInfoExt.objects.get(sample_number = row['样品编号'])
        if instance:
            # instance = SampleInfo()
            for attr, value in row.items():
                setattr(instance, attr, value)
            # instance.id = str(int(SampleInfo.objects.latest('id').id)+1)
            instance.lib_code = row['文库号']
            instance.index = row['Index']
            instance.lib_volume = row['体积uL(文库)']
            instance.lib_concentration = row['浓度ng/uL(文库)']
            instance.lib_total = row['总量ng(文库)']
            instance.lib_result = row['结论(文库)']
            instance.lib_note = row['备注(文库)']
            return instance
        else:
            raise Exception("你上传的样品编号有误")

    def get_diff_headers(self):
        return ["样品编号","文库号","Index","体积uL(文库)","浓度ng/uL(文库)"
                ,"总量ng(文库)","结论(文库)","备注(文库)","选择是否重建库(0代表不重建库,1代表重建库)"]



#
class LibExecuteAdmin(ImportExportActionModelAdmin):

    resource_class = SampleInfoLibResource

    list_per_page = 30

    save_as_continue = False

    save_on_top = False

    # list_display = ('libSubmit', 'lib_experimenter', 'lib_end_date', 'note')
    list_display = ('libSubmit', 'lib_end_date', 'note',"is_submit")

    exclude = ("lib_end_date",)

    list_display_links = ('libSubmit',)

    # actions = ["submit_result", ]

    def get_readonly_fields(self, request, obj=None):
        self.readonly_fields = []
        try:
            if obj.is_submit:
                self.readonly_fields = ('libSubmit','lib_experimenter','upload_file','lib_end_date', 'note',"is_submit",)
                return self.readonly_fields
        except:
            return self.readonly_fields
        return self.readonly_fields

    def save_model(self, request, obj, form, change):
        if obj.is_submit:
            #钉钉
            obj.lib_end_date = datetime.datetime.now()
            pass
        super().save_model(request, obj, form, change)

    # 设置实验员不能增加执行任务
    def has_add_permission(self, request):
        try:
            current_group_set = Group.objects.get(user=request.user)
        except:
            return True
        if current_group_set.name == "实验员":
            return False
        else:
            return True

    def get_actions(self, request):
        actions = super().get_actions(request)
        del actions['delete_selected']
        del actions['export_admin_action']
        return actions


#测序操作
class SampleInfoSeqResource(resources.ModelResource):
    class Meta:
        model = SampleInfoSeq
        skip_unchanged = True
        fields = ('sample_number','seq_code',
        'seq_index', 'data_request','seq_data', 'seq_result', 'seq_note','is_rebuild')
        export_order = ('sample_number','seq_code',
        'seq_index', 'data_request','seq_data', 'seq_result', 'seq_note','is_rebuild')

    def get_export_headers(self):
        return ["样品编号","文库号","Index","数据量要求","测序数据量"
            ,"结论(测序)","备注(测序)","选择是否重测序(0代表不重测序,1代表重测序)"]

    def init_instance(self, row=None):
        if not row:
            row = {}
        instance = SampleInfoExt.objects.get(sample_number = row['样品编号'])
        if instance:
            # instance = SampleInfo()
            for attr, value in row.items():
                setattr(instance, attr, value)
            # instance.id = str(int(SampleInfo.objects.latest('id').id)+1)
            instance.seq_code = row['文库号']
            instance.seq_index = row['Index']
            instance.data_request = row['数据量要求']
            instance.seq_data = row['测序数据量']
            instance.seq_result = row['结论(测序)']
            instance.seq_note = row['备注(测序)']
            return instance
        else:
            raise Exception("你上传的样品编号有误")

    def get_diff_headers(self):
        return ["样品编号","文库号","Index","数据量要求","测序数据量"
            ,"结论(测序)","备注(测序)","选择是否重测序(0代表不重测序,1代表重测序)"]

class SeqExecuteAdmin(ImportExportActionModelAdmin):

    resource_class = SampleInfoSeqResource

    list_per_page = 30

    save_as_continue = False

    save_on_top = False

    # list_display = ('seqSubmit', 'seq_experimenter', 'seq_end_date', 'note')
    list_display = ('seqSubmit', 'seq_end_date', 'note',"is_submit")

    exclude = ("seq_end_date",)

    list_display_links = ('seqSubmit',)

    # actions = ["submit_result", ]

    def get_readonly_fields(self, request, obj=None):
        self.readonly_fields = []
        try:
            if obj.is_submit:
                self.readonly_fields = ('seqSubmit','seq_experimenter','upload_file','seq_end_date', 'note',"is_submit",)
                return self.readonly_fields
        except:
            return self.readonly_fields
        return self.readonly_fields

    def save_model(self, request, obj, form, change):
        if obj.is_submit:
            #钉钉
            obj.seq_end_date = datetime.datetime.now()
            pass
        super().save_model(request, obj, form, change)

    # 设置实验员不能增加执行任务
    def has_add_permission(self, request):
        try:
            current_group_set = Group.objects.get(user=request.user)
        except:
            return True
        if current_group_set.name == "实验员":
            return False
        else:
            return True

    def get_actions(self, request):
        actions = super().get_actions(request)
        del actions['delete_selected']
        del actions['export_admin_action']
        return actions

BMS_admin_site.register(ExtExecute,ExtExecuteAdmin)
BMS_admin_site.register(LibExecute,LibExecuteAdmin)
BMS_admin_site.register(SeqExecute,SeqExecuteAdmin)