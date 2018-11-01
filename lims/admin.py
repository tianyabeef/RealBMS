import datetime
import gc
from django.contrib import admin
from django.contrib.auth.models import Group
from import_export import resources
from import_export.admin import ImportExportActionModelAdmin
from BMS.admin_bms import BMS_admin_site
from lims.models import SampleInfoExt, ExtExecute, LibExecute,  SampleInfoLib, SampleInfoSeq, SeqExecute
from pm.models import LibSubmit,SeqSubmit,ExtSubmit,AnaSubmit

try:
    from django.utils.encoding import force_text
except ImportError:
    from django.utils.encoding import force_unicode as force_text
from sample.models import SampleInfoForm, SampleInfo

#外键样品
class SampleInfoExtInline(admin.StackedInline):
    model = SampleInfoExt
class SampleInfoLibInline(admin.StackedInline):
    model = SampleInfoLib
class SampleInfoSeqInline(admin.StackedInline):
    model = SampleInfoSeq


#抽提的导入
class SampleInfoExtResource(resources.ModelResource):
    class Meta:
        model = SampleInfoExt
        skip_unchanged = True
        import_id_fields = ("sample_number",)
        fields = ("id",'sample_number','sample_used',
        'sample_rest', 'density_checked','volume_checked', 'D260_280', 'D260_230', 'DNA_totel','note','quality_control_conclusion','is_rebuild')
        export_order = ("id",'sample_number','sample_used',
        'sample_rest', 'density_checked','volume_checked', 'D260_280', 'D260_230', 'DNA_totel','note','quality_control_conclusion','is_rebuild')

    def get_export_headers(self):
        return ["id","样品编号","样品提取用量","样品剩余用量","浓度ng/uL(公司检测)","体积uL(公司检测)"
            ,"D260/280","D260/230","DNA总量","备注","质检结论","选择是否重抽提(0代表不重抽提,1代表重抽提)"]

    def get_or_init_instance(self, instance_loader, row):
        """
        Either fetches an already existing instance or initializes a new one.
        """
        instance = self.get_instance(instance_loader, row)
        if instance:
            instance.sample_used = row['样品提取用量']
            instance.sample_rest = row['样品剩余用量']
            instance.density_checked = row['浓度ng/uL(公司检测)']
            instance.volume_checked = row['体积uL(公司检测)']
            instance.D260_280 = row['D260/280']
            instance.D260_230 = row['D260/230']
            instance.DNA_totel = row['DNA总量']
            instance.note = row['备注']
            instance.quality_control_conclusion = row['质检结论']
            instance.save()
            return (instance, False)
        else:
            raise Exception("请核对样品编号")
            # return (self.init_instance(row), True)

    def get_diff_headers(self):
        return ["id","样品编号","样品提取用量","样品剩余用量","浓度ng/uL(公司检测)","体积uL(公司检测)"
            ,"D260/280","D260/230","DNA总量","备注","质检结论","选择是否重抽提(0代表不重抽提,1代表重抽提)"]

class ExtExecuteAdmin(ImportExportActionModelAdmin):

    filter_horizontal = ("ext_experimenter",)

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
                self.readonly_fields = ('extSubmit','ext_experimenter',"extract_method","test_method",'upload_file','ext_end_date', 'note',"is_submit",)
                return self.readonly_fields
        except:
            return self.readonly_fields
        return self.readonly_fields

    def save_model(self, request, obj, form, change):

        super().save_model(request, obj, form, change)

        if obj.ext_experimenter.all():
            #钉钉
            if obj.extSubmit.subProject.is_status < 3:
                obj.extSubmit.subProject.is_status = 3
                obj.extSubmit.subProject.save()
            else:
                pass
        if obj.is_submit:
            if obj.extSubmit.subProject.is_status < 4:
                obj.extSubmit.subProject.is_status = 4
                obj.extSubmit.subProject.save()
            if not obj.ext_end_date:
                #钉钉
                obj.ext_end_date = datetime.datetime.now()
                qs = obj.sampleinfoext_set.all()
                #建立建库任务单
                # lib = LibSubmit()
                # if LibSubmit.objects.all().count() == 0:
                #     lib.id = "1"
                # else:
                #     lib.id = str(int(LibSubmit.objects.latest('id').id) + 1)
                # lib.subProject = obj.extSubmit.subProject
                for i in qs.filter(is_rebuild=0):
                    SampleInfo.objects.filter(unique_code=i.unique_code).first().color_code = "black"
                    SampleInfo.objects.filter(unique_code=i.unique_code).first().save()
                # lib.lib_number ="test00001"
                # lib.save()
                # del lib
                #建立重抽提任务单
                ext = ExtSubmit()
                ext.subProject = obj.extSubmit.subProject
                for j in qs.filter(is_rebuild=1):
                    SampleInfo.objects.filter(unique_code=j.unique_code).first().color_code = "red"
                    ext.sample.add(SampleInfo.objects.filter(unique_code=j.unique_code).first())
                    SampleInfo.objects.filter(unique_code=j.unique_code).first().save()
                ext.ext_number = "重抽提编号测试一号"
                ext.save()
                del ext
            else:
                pass




    # def get_actions(self, request):
    #     actions = super().get_actions(request)
    #     del actions['export_admin_action']
    #     return actions

#建库操作
class SampleInfoLibResource(resources.ModelResource):
    class Meta:
        model = SampleInfoLib
        skip_unchanged = True
        import_id_fields = ("sample_number",)
        fields = ('sample_number','lib_code',
        'index', 'lib_volume','lib_concentration', 'lib_total', 'lib_result', 'lib_note','is_rebuild')
        export_order = ('sample_number','lib_code',
        'index', 'lib_volume','lib_concentration', 'lib_total', 'lib_result', 'lib_note','is_rebuild')

    def get_export_headers(self):
        return ["样品编号","文库号","Index","体积uL(文库)","浓度ng/uL(文库)"
            ,"总量ng(文库)","结论(文库)","备注(文库)","选择是否重建库(0代表不重建库,1代表重建库)"]

    def get_or_init_instance(self, instance_loader, row):
        """
        Either fetches an already existing instance or initializes a new one.
        """
        instance = self.get_instance(instance_loader, row)
        if instance:
            instance.lib_code = row['文库号']
            instance.index = row['Index']
            instance.lib_volume = row['体积uL(文库)']
            instance.lib_concentration = row['浓度ng/uL(文库)']
            instance.lib_total = row['总量ng(文库)']
            instance.lib_result = row['结论(文库)']
            instance.lib_note = row['备注(文库)']
            instance.save()
            return (instance, False)
        else:
            raise Exception("请核对样品编号")
            # return (self.init_instance(row), True)


    def get_diff_headers(self):
        return ["样品编号","文库号","Index","体积uL(文库)","浓度ng/uL(文库)"
                ,"总量ng(文库)","结论(文库)","备注(文库)","选择是否重建库(0代表不重建库,1代表重建库)"]



#
class LibExecuteAdmin(ImportExportActionModelAdmin):

    resource_class = SampleInfoLibResource

    list_per_page = 30

    save_as_continue = False

    inlines = [SampleInfoLibInline]

    save_on_top = False

    # list_display = ('libSubmit', 'lib_experimenter', 'lib_end_date', 'note')
    list_display = ('libSubmit', 'lib_end_date', 'note',"is_submit")

    exclude = ("lib_end_date",)

    list_display_links = ('libSubmit',)

    filter_horizontal = ("lib_experimenter",)
    # actions = ["submit_result", ]

    def get_readonly_fields(self, request, obj=None):
        self.readonly_fields = []
        try:
            if obj.is_submit:
                self.readonly_fields = ('libSubmit','lib_experimenter','upload_file','lib_end_date', 'note',"is_submit",
                                        "reaction_times","pcr_system","dna_polymerase","model_initiation_mass","enzyme_number",
                                        "pcr_process","annealing_temperature","loop_number","gel_recovery_kit")
                return self.readonly_fields
        except:
            return self.readonly_fields
        return self.readonly_fields

    def save_model(self, request, obj, form, change):

        super().save_model(request, obj, form, change)

        if obj.lib_experimenter.all():
            #钉钉
            if obj.libSubmit.subProject.is_status < 6:
                obj.libSubmit.subProject.is_status = 6
                obj.libSubmit.subProject.save()
            else:
                pass
        if obj.is_submit:
            if obj.libSubmit.subProject.is_status < 7:
                obj.libSubmit.subProject.is_status = 7
                obj.libSubmit.subProject.save()
            if not obj.lib_end_date:
                #钉钉
                obj.lib_end_date = datetime.datetime.now()
                qs = obj.sampleinfolib_set.all()
                #建立测序任务单
                # seq = SeqSubmit()
                # if SeqSubmit.objects.all().count() == 0:
                #     seq.id = "1"
                # else:
                #     seq.id = str(int(SeqSubmit.objects.latest('id').id) + 1)
                # seq.subProject = obj.libSubmit.subProject
                for i in qs.filter(is_rebuild=0):
                    SampleInfo.objects.filter(unique_code=i.unique_code).first().color_code = "black"
                    SampleInfo.objects.filter(unique_code=i.unique_code).first().save()
                # seq.lib_number ="测序编号00001"
                # seq.save()
                # del seq
                #建立重建库任务单
                lib = LibSubmit()
                lib.subProject = obj.libSubmit.subProject
                for j in qs.filter(is_rebuild=1):
                    SampleInfo.objects.filter(unique_code=j.unique_code).first().color_code = "blue"
                    SampleInfo.objects.filter(unique_code=j.unique_code).first().save()
                    lib.sample.add(SampleInfo.objects.filter(unique_code=j.unique_code).first())
                lib.lib_number = "重建库编号测试一号"
                lib.save()
                del lib
            else:
                pass



    # def get_actions(self, request):
    #     actions = super().get_actions(request)
    #     del actions['export_admin_action']
    #     return actions


#测序操作
class SampleInfoSeqResource(resources.ModelResource):
    class Meta:
        model = SampleInfoSeq
        skip_unchanged = True
        import_id_fields = ("sample_number",)
        fields = ('sample_number','seq_code',
        'seq_index', 'data_request','seq_data', 'seq_result', 'seq_note','is_rebuild')
        export_order = ('sample_number','seq_code',
        'seq_index', 'data_request','seq_data', 'seq_result', 'seq_note','is_rebuild')

    def get_export_headers(self):
        return ["样品编号","文库号","Index","数据量要求","测序数据量"
            ,"结论(测序)","备注(测序)","选择是否重测序(0代表不重测序,1代表重测序)"]

    def get_or_init_instance(self, instance_loader, row):
        """
        Either fetches an already existing instance or initializes a new one.
        """
        instance = self.get_instance(instance_loader, row)
        if instance:
            instance.seq_code = row['文库号']
            instance.seq_index = row['Index']
            instance.data_request = row['数据量要求']
            instance.seq_data = row['测序数据量']
            instance.seq_result = row['结论(测序)']
            instance.seq_note = row['备注(测序)']
            instance.save()
            return (instance, False)
        else:
            raise Exception("请核对样品编号")
            # return (self.init_instance(row), True)

    def get_diff_headers(self):
        return ["样品编号","文库号","Index","数据量要求","测序数据量"
            ,"结论(测序)","备注(测序)","选择是否重测序(0代表不重测序,1代表重测序)"]

class SeqExecuteAdmin(ImportExportActionModelAdmin):

    resource_class = SampleInfoSeqResource

    list_per_page = 30

    save_as_continue = False

    inlines = [SampleInfoSeqInline]

    save_on_top = False

    filter_horizontal = ("seq_experimenter",)
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

        super().save_model(request, obj, form, change)

        if obj.seq_experimenter.all():
            #钉钉
            if obj.seqSubmit.subProject.is_status < 9:
                obj.seqSubmit.subProject.is_status = 9
                obj.seqSubmit.subProject.save()
            else:
                pass

        if obj.is_submit:
            if obj.seqSubmit.subProject.is_status < 10:
                obj.seqSubmit.subProject.is_status = 10
                obj.seqSubmit.subProject.save()
            if not obj.seq_end_date:
                #钉钉
                obj.seq_end_date = datetime.datetime.now()
                qs = obj.sampleinfoseq_set.all()
                #建立分析任务单
                # ana = AnaSubmit()
                # if AnaSubmit.objects.all().count() == 0:
                #     ana.id = "1"
                # else:
                #     ana.id = str(int(SeqSubmit.objects.latest('id').id) + 1)
                # ana.subProject = obj.SeqSubmit.subProject
                for i in qs.filter(is_rebuild=0):
                    SampleInfo.objects.filter(unique_code=i.unique_code).first().color_code = "black"
                    SampleInfo.objects.filter(unique_code=i.unique_code).first().save()
                # ana.ana_number ="分析下单编号00001"
                # ana.save()
                # del ana
                #建立重测序任务单
                seq = SeqSubmit()
                seq.subProject = obj.seqSubmit.subProject
                for j in qs.filter(is_rebuild=1):
                    SampleInfo.objects.filter(unique_code=j.unique_code).first().color_code = "yellow"
                    SampleInfo.objects.filter(unique_code=j.unique_code).first().save()
                    seq.sample.add(SampleInfo.objects.filter(unique_code=j.unique_code).first())
                seq.seq_number = "重建库编号测试一号"
                seq.save()
                del seq
            else:
                pass



    # def get_actions(self, request):
    #     actions = super().get_actions(request)
    #     del actions['export_admin_action']
    #     return actions

BMS_admin_site.register(ExtExecute,ExtExecuteAdmin)
BMS_admin_site.register(LibExecute,LibExecuteAdmin)
BMS_admin_site.register(SeqExecute,SeqExecuteAdmin)