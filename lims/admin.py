import datetime
import time

from django.contrib import admin
from django.contrib.auth.models import User, Group
from django import forms
from django.utils.html import format_html
from hashlib import md5
from nm.models import DingtalkChat
from import_export import resources, fields
from import_export.admin import ImportExportActionModelAdmin
from django.db import models
from BMS import settings
from BMS.admin_bms import BMS_admin_site
from BMS.notice_mixin import NotificationMixin
from BMS.settings import DINGTALK_SECRET, DINGTALK_APPKEY
from lims.models import SampleInfoExt, ExtExecute, LibExecute, SampleInfoLib, SampleInfoSeq, SeqExecute, Extmethod, \
    Testmethod
from pm.models import LibSubmit,SeqSubmit,ExtSubmit,AnaSubmit,SubProject

try:
    from django.utils.encoding import force_text
except ImportError:
    from django.utils.encoding import force_unicode as force_text
from sample.models import SampleInfoForm, SampleInfo



class ExtExecuteForm(forms.ModelForm):

    class Meta:
        model = ExtExecute
        fields = "__all__"

    def clean_is_submit(self):
        aa = self.cleaned_data['is_submit']
        file = self.cleaned_data["upload_file"]
        if aa:
            if not file:
                raise forms.ValidationError(
                    "提交时抽提报告不能为空", code='invalid value'
                )
        else:
            return self.cleaned_data['is_submit']
        return aa
class LibExecuteForm(forms.ModelForm):

    class Meta:
        model = LibExecute
        fields = "__all__"

    def clean_is_submit(self):
        aa = self.cleaned_data['is_submit']
        file = self.cleaned_data["upload_file"]
        if aa:
            if not file:
                raise forms.ValidationError(
                    "提交时建库报告不能为空", code='invalid value'
                )
        else:
            return self.cleaned_data['is_submit']
        return aa
class SeqExecuteForm(forms.ModelForm):

    class Meta:
        model = SeqExecute
        fields = "__all__"

    def clean_is_submit(self):
        aa = self.cleaned_data['is_submit']
        file = self.cleaned_data["upload_file"]
        if aa:
            if not file:
                raise forms.ValidationError(
                    "提交时测序结果报告不能为空", code='invalid value'
                )
        else:
            return self.cleaned_data['is_submit']
        return aa
#外键样品
class SampleInfoExtInline(admin.StackedInline):
    model = SampleInfoExt
    fields = (("extExecute","unique_code","sample_number",),("sample_name","species","sample_type",),("sample_used",
               "sample_rest",),("density_checked","volume_checked","D260_280","D260_230","DNA_totel","quality_control_conclusion","is_rebuild"),)
    radio_fields = {
        "quality_control_conclusion": admin.HORIZONTAL,
        "is_rebuild": admin.HORIZONTAL,
        "sample_type": admin.HORIZONTAL,
    }
    def has_change_permission(self, request, obj=None):
        try:
            if obj.is_submit:
                return False
        except:
            pass
        return super().has_change_permission(request, obj=None)

class SampleInfoLibInline(admin.StackedInline):
    model = SampleInfoLib
    fields = (("libExecute", "unique_code", "sample_number", "sample_name", "lib_code", "index", "lib_volume",
               "lib_concentration", "lib_total", "lib_result", "is_rebuild"),)
    radio_fields = {
        "lib_result": admin.HORIZONTAL,
        "is_rebuild": admin.HORIZONTAL,
    }
    def has_change_permission(self, request, obj=None):
        try:
            if obj.is_submit:
                return False
        except:
            pass
        return super().has_change_permission(request, obj=None)

class SampleInfoSeqInline(admin.StackedInline):
    model = SampleInfoSeq
    fields = (("seqExecute", "unique_code", "sample_number", "sample_name", "seq_code", "seq_index", "data_request",
               "seq_data", "seq_result",  "is_rebuild"),)
    radio_fields = {
        "seq_result": admin.HORIZONTAL,
        "is_rebuild": admin.HORIZONTAL,
    }
    def has_change_permission(self, request, obj=None):
        try:
            if obj.is_submit:
                return False
        except:
            pass
        return super().has_change_permission(request, obj=None)

#抽提方法注册
class ExtmothodAdmin(admin.ModelAdmin):
    search_fields = ("mothod",)


class TestmothodAdmin(admin.ModelAdmin):
    search_fields = ("mothod",)

#抽提的导入
class SampleInfoExtResource(resources.ModelResource):
    class Meta:
        model = SampleInfoExt
        skip_unchanged = True
        import_id_fields = ("sample_number",)
        fields = ("id",'sample_number','sample_used',
        'sample_rest', 'density_checked','volume_checked', 'D260_280', 'D260_230', 'DNA_totel','note','quality_control_conclusion','is_rebuild')
        # export_order = ("id",'sample_number','sample_used',
        # 'sample_rest', 'density_checked','volume_checked', 'D260_280', 'D260_230', 'DNA_totel','note','quality_control_conclusion','is_rebuild')

    def get_export_headers(self):
        return ["id","sample_number","样品提取用量","样品剩余用量","浓度ng/uL(公司检测)","体积uL(公司检测)"
            ,"D260/280","D260/230","DNA总量","备注","质检结论","选择是否重抽提(0代表不重抽提,1代表重抽提)"]

    def get_diff_headers(self):
        return ["id","sample_number","样品提取用量","样品剩余用量","浓度ng/uL(公司检测)","体积uL(公司检测)"
            ,"D260/280","D260/230","DNA总量","备注","质检结论","选择是否重抽提(0代表不重抽提,1代表重抽提)"]

    def export(self, queryset=None, *args, **kwargs):
        queryset_result = SampleInfoExt.objects.filter(id=None)
        for i in queryset:
            queryset_result |= SampleInfoExt.objects.filter(extExecute=i)
        return super().export(queryset=queryset_result, *args, **kwargs)

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
            instance.is_rebuild = row['选择是否重抽提(0代表不重抽提,1代表重抽提)']
            instance.save()
            return (instance, False)
        else:
            raise Exception("请核对样品编号")
            # return (self.init_instance(row), True)





class ExtExecuteAdmin(ImportExportActionModelAdmin,NotificationMixin):



    form = ExtExecuteForm

    filter_horizontal = ("ext_experimenter",)

    resource_class = SampleInfoExtResource

    list_per_page = 50

    inlines = [SampleInfoExtInline]

    save_as_continue = False

    save_on_top = False

    appkey = DINGTALK_APPKEY

    appsecret = DINGTALK_SECRET

    fields = ("extSubmit","ext_experimenter",("extract_method","test_method"),"note","upload_file","is_submit")

    search_fields = ("extract_method","test_method")

    autocomplete_fields = ("extract_method","test_method")

    list_display = ('extSubmit',  'ext_end_date', 'note',"is_submit")

    exclude = ("ext_end_date","query_code")

    list_display_links = ('extSubmit',)

    ordering = ('-id',)
    # actions = ["submit_result",]

    # def export_action(self, request, *args, **kwargs):

    # def change_view(self, request, object_id, form_url='', extra_context=None):


    def get_object(self, request, object_id, from_field=None):

        self.obj = super(ExtExecuteAdmin,self).get_object(request,object_id)

        return self.obj


    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "ext_experimenter":
            kwargs["queryset"] = User.objects.filter(groups__name="实验部")
        return super().formfield_for_manytomany( db_field, request, **kwargs)

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
        Dinggroupid = DingtalkChat.objects.filter(chat_name="实验钉钉群-BMS").first().chat_id

        sub_number = obj.extSubmit.subProject.sub_number


        project = SubProject.objects.filter(sub_number=sub_number).first()

        if project.is_status < 3:
            project.is_status = 3
            project.save()
            man = []
            for i in form.cleaned_data["ext_experimenter"]:
                man.append((i.last_name+i.first_name))
            self.send_group_message("编号{0}的抽提任务执行中------，执行人:{1}".format(obj.extSubmit,
                                                                   man),Dinggroupid)
            self.message_user(request,"编号{0}的抽提任务执行中------，执行人:{1}".format(obj.extSubmit,
                                                                   man))
            if not self.send_dingtalk_result:
                self.message_user(request,"钉钉发送失败")
        if obj.is_submit:
            # if not obj.upload_file:
            #     self.message_user(request,"抽提结果不能为空")
            #     return None
            if project.is_status < 4:
                project.is_status = 4
                project.save()
            if not obj.ext_end_date:
                obj.ext_end_date = datetime.datetime.now()
                obj.save()
                qs = obj.sampleinfoext_set.all()
                if qs.count()==0:
                    self.message_user(request,"未选择样品！")
                    return None
                msg_dingding = "项目{0}的抽提执行{1}结果已上传".format(project.sub_project,obj.extSubmit)
                # msg_email = ["<h2>{0}</h2><br><table><tr><th>抽提样品编号</th><th>样品名称</th><th>物种</th><th>样品类型</th><th>样品提取用量"
                #              "</th><th>样品剩余用量</th><th>浓度ng/uL(公司检测)</th><th>体积uL(公司检测)</th><th>D260_280</th><th>D260_230</th>"
                #              "<th>DNA总量</th><th>选择是否重抽提</th><th>质检结论</th><th>备注</th></tr>".format(msg_dingding),]
                md = md5()
                md.update(("ext" + str(time.time())).encode())
                key = md.hexdigest()
                obj.query_code = key
                data_url = "http://" + request.META.get("HTTP_HOST") + "/lims/getdata/?index=" + key
                print(data_url)
                msg_email = "编号：{0} 的抽提实验完成，请点击<a href='{1}'>实验结果</a>查看<hr>".format(sub_number,data_url)
                for i in qs.filter(is_rebuild=0):
                    # msg_email.append(("<tr><td>{0}</td><td>{1}</td><td>{2}</td><td>{3}</td><td>{4}</td><td>{5}</td><td>{6}</td><td>{7}</td>"
                    #                   "<td>{8}</td><td>{9}</td><td>{10}</td><td>{11}</td><td>{12}</td></tr>".format(i.sample_number,i.sample_name,i.species,i.Type_of_Sample[i.sample_type-1][1],i.sample_used,
                    #            i.sample_rest,str(i.density_checked),str(i.volume_checked),str(i.D260_280),str(i.D260_230),
                    #            str(i.DNA_totel),str(i.Rebulid[i.is_rebuild][1]),str(i.Quality_control_conclusion[i.quality_control_conclusion-1][1]),
                    #            i.note)))
                    SampleInfo.objects.filter(unique_code=i.unique_code).update(color_code = "__{}__已抽提".format(sub_number) )
                #建立重抽提任务单
                ext = ExtSubmit()
                ext.project_manager_id = obj.extSubmit.project_manager_id
                ext.id = str(int(ExtSubmit.objects.latest('id').id) + 1)
                ext.subProject = obj.extSubmit.subProject
                for i in qs.filter(is_rebuild=1):
                    # msg_email.append(("<tr><td>{0}</td><td>{1}</td><td>{2}</td><td>{3}</td><td>{4}</td><td>{5}</td><td>{6}</td><td>{7}</td>"
                    #                      "<td>{8}</td><td>{9}</td><td>{10}</td><td>{11}</td><td>{12}</td></tr>".format(
                    #                          i.sample_number, i.sample_name, i.species,
                    #                          i.Type_of_Sample[i.sample_type - 1][1], i.sample_used,
                    #                          i.sample_rest, str(i.density_checked), str(i.volume_checked),
                    #                          str(i.D260_280), str(i.D260_230),
                    #                          str(i.DNA_totel), str(i.Rebulid[i.is_rebuild][1]),
                    #                          str(i.Quality_control_conclusion[i.quality_control_conclusion - 1][1]),
                    #                          i.note)))
                    try:
                        if SampleInfo.objects.filter(unique_code=i.unique_code).first().color_code:
                            if ord(SampleInfo.objects.filter(unique_code=i.unique_code).first().color_code[-1:]) in range(48,58):
                                if ord(SampleInfo.objects.filter(unique_code=i.unique_code).first().color_code[-2:-1]) in range(48,58):
                                    new_status = SampleInfo.objects.filter(unique_code=i.unique_code).first().color_code[0:-2] +\
                                                 str(int(SampleInfo.objects.filter(unique_code=i.unique_code).first().color_code[-2:])+1)
                                else:
                                    new_status = SampleInfo.objects.filter(unique_code=i.unique_code).first().color_code[0:-1] + \
                                                 str(int(SampleInfo.objects.filter(unique_code=i.unique_code).first().color_code[-1:])+1)
                                SampleInfo.objects.filter(unique_code=i.unique_code).update(color_code=new_status)
                            else:
                                SampleInfo.objects.filter(unique_code=i.unique_code).update(
                                    color_code=" __{}__重抽提（未执行）1".format(sub_number))
                        else:
                            SampleInfo.objects.filter(unique_code=i.unique_code).update(color_code=" __{}__重抽提（未执行）1".format(sub_number))

                        ext.sample.add(SampleInfo.objects.filter(unique_code=i.unique_code).first())
                    except:
                        pass
                old = obj.extSubmit.ext_number
                if "_" in old:
                    new = old[0:-1] + str(int(old[-1])+1)
                else:
                    new = old + "_" + "1"
                ext.ext_number = new
                ext.save()
                del ext
                del md
                project.time_ext = datetime.datetime.now()
                project.save()
                # content = ""
                # for x in msg_email:
                #     content += x
                # content += "</table>"
                self.send_email(content="内容",html_message = msg_email,
                        sender=settings.EMAIL_FROM,
                        recipient_list=["love949872618@qq.com",],
                        fail_silently=False)
                self.send_group_message(msg_dingding,"chat62dbddc59ef51ae0f4a47168bdd2a65b")
                self.message_user(request,"抽提实验结果导入成功")
            else:
                pass
        else:
            pass

        super().save_model(request, obj, form, change)


    # def get_actions(self, request):
    #     actions = super().get_actions(request)
    #     del actions['export_admin_action']
    #     return actions

#建库操作
class SampleInfoLibResource(resources.ModelResource,):
    class Meta:
        model = SampleInfoLib
        skip_unchanged = True
        import_id_fields = ("sample_number",)
        fields = ("id",'sample_number','lib_code',
        'index', 'lib_volume','lib_concentration', 'lib_total', 'lib_result', 'lib_note','is_rebuild')
        # export_order = ('sample_number','lib_code',
        # 'index', 'lib_volume','lib_concentration', 'lib_total', 'lib_result', 'lib_note','is_rebuild')

    def get_export_headers(self):
        return ["id","sample_number","文库号","Index","体积uL(文库)","浓度ng/uL(文库)"
            ,"总量ng(文库)","结论(文库)","备注(文库)","选择是否重建库(0代表不重建库,1代表重建库)"]

    def get_diff_headers(self):
        return ["id","sample_number","文库号","Index","体积uL(文库)","浓度ng/uL(文库)"
                ,"总量ng(文库)","结论(文库)","备注(文库)","选择是否重建库(0代表不重建库,1代表重建库)"]

    def export(self, queryset=None, *args, **kwargs):
        queryset_result = SampleInfoLib.objects.filter(id=None)
        print(queryset)
        for i in queryset:
            print(i)
            queryset_result |= SampleInfoLib.objects.filter(libExecute=i)
        print(queryset_result)
        return super().export(queryset=queryset_result, *args, **kwargs)

    def get_or_init_instance(self, instance_loader, row):
        """
        Either fetches an already existing instance or initializes a new one.
        """
        instance = self.get_instance(instance_loader, row)
        if instance:
            try:
                a = str(int(row["文库号"]))
                b = str(int(row["Index"]))
                instance.lib_code = a
                instance.index = b
            except:
                instance.lib_code = row['文库号']
                instance.index = row['Index']
            instance.lib_volume = row['体积uL(文库)']
            instance.lib_concentration = row['浓度ng/uL(文库)']
            instance.lib_total = row['总量ng(文库)']
            instance.lib_result = row['结论(文库)']
            instance.lib_note = row['备注(文库)']
            instance.is_rebuild = row['选择是否重建库(0代表不重建库,1代表重建库)']
            instance.save()
            return (instance, False)
        else:
            raise Exception("请核对样品编号")
            # return (self.init_instance(row), True)

#
class LibExecuteAdmin(ImportExportActionModelAdmin,NotificationMixin):

    resource_class = SampleInfoLibResource

    list_per_page = 50

    save_as_continue = False

    inlines = [SampleInfoLibInline]

    save_on_top = False

    fields = ("libSubmit","lib_experimenter",("reaction_times","pcr_system","dna_polymerase"),("model_initiation_mass","enzyme_number",
             ),("pcr_process","loop_number","gel_recovery_kit"),"annealing_temperature","note","upload_file","is_submit")

    form = LibExecuteForm

    appkey = DINGTALK_APPKEY

    appsecret = DINGTALK_SECRET

    list_display = ('libSubmit', 'lib_end_date', 'note',"is_submit")

    exclude = ("lib_end_date","query_code")

    list_display_links = ('libSubmit',)

    filter_horizontal = ("lib_experimenter",)

    ordering = ('-id',)

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

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "lib_experimenter":
            kwargs["queryset"] = User.objects.filter(groups__name="实验部")
        return super().formfield_for_manytomany( db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):

        Dinggroupid = DingtalkChat.objects.filter(chat_name="实验钉钉群-BMS").first().chat_id

        sub_number = obj.libSubmit.subProject.sub_number

        project = SubProject.objects.filter(sub_number=sub_number)

        #钉钉
        if project.first().is_status < 6:
            project.update(is_status=6)
            man = []
            for i in form.cleaned_data["lib_experimenter"]:
                man.append((i.last_name + i.first_name))
            self.send_group_message("编号{0}的建库任务执行中------，执行人:{1}".format(obj.libSubmit,
                                                                         man), Dinggroupid)
            self.message_user(request,"编号{0}的建库任务执行中------，执行人:{1}".format(obj.libSubmit,
                                                                         man))
            if not self.send_dingtalk_result:
                self.message_user(request,"钉钉发送失败")
        if obj.is_submit:
            # if not obj.upload_file:
            #     self.message_user(request,"提交时建库报告不能为空")
            #     return None
            if project.first().is_status < 7:
                project.update(is_status=7)
            if not obj.lib_end_date:
                # 钉钉
                obj.lib_end_date = datetime.datetime.now()
                qs = obj.sampleinfolib_set.all()
                if qs.count()==0:
                    self.message_user(request,"未选择样品！")
                    return None
                msg_dingding = "项目{0}的建库执行{1}结果已上传".format(project.first().sub_project, obj.libSubmit)
                # # msg_email = ["<h2>{0}</h2><br><table><tr><th>建库样品编号</th><th>样品名称</th><th>文库号</th><th>Index</th><th>体积uL(文库)"
                #              "</th><th>浓度ng/uL(文库)</th><th>总量ng(文库)</th><th>结论(文库)</th><th>备注(文库)</th><th>选择是否重建库</th>"
                #              "</tr>".format(msg_dingding), ]
                md = md5()
                md.update(("lib" + str(time.time())).encode())
                key = md.hexdigest()
                obj.query_code = key
                data_url = "http://" + request.META.get("HTTP_HOST") + "/lims/getdata/?index=" + key
                msg_email = "编号：{0} 的建库实验完成，请点击<a href='{1}'>实验结果</a>查看<hr>".format(sub_number, data_url)

                for i in qs.filter(is_rebuild=0):
                    # msg_email.append(("<tr><td>{0}</td><td>{1}</td><td>{2}</td><td>{3}</td><td>{4}</td><td>{5}</td><td>{6}</td><td>{7}</td><td>{8}</td><td>{9}</td>"
                    #                   .format(i.sample_number,i.sample_name,i.lib_code,i.index,i.lib_volume,i.lib_concentration,
                    #                           i.lib_total,i.Lib_result[i.lib_result-1][1],i.lib_note,i.Rebulid[i.is_rebuild][1])))
                    SampleInfo.objects.filter(unique_code=i.unique_code).update(color_code="__{}__已建库".format(sub_number))
                # 建立重建库任务单
                lib = LibSubmit()
                lib.project_manager_id = obj.libSubmit.project_manager_id
                lib.id = str(int(LibSubmit.objects.latest('id').id) + 1)
                lib.subProject = obj.libSubmit.subProject
                for j in qs.filter(is_rebuild=1):
                    # msg_email.append((
                    #                      "<tr><td>{0}</td><td>{1}</td><td>{2}</td><td>{3}</td><td>{4}</td><td>{5}</td><td>{6}</td><td>{7}</td><td>{8}</td><td>{9}</td>"
                    #                      .format(j.sample_number, j.sample_name, j.lib_code, j.index, j.lib_volume,
                    #                              j.lib_concentration,
                    #                              j.lib_total, j.Lib_result[j.lib_result - 1][1], j.lib_note,
                    #                              j.Rebulid[j.is_rebuild][1])))
                    try:
                        if SampleInfo.objects.filter(unique_code=j.unique_code).first().color_code:
                            if ord(SampleInfo.objects.filter(unique_code=j.unique_code).first().color_code[-1:]) in range(48, 58):
                                if ord(SampleInfo.objects.filter(unique_code=j.unique_code).first().color_code[-1:]) in range(
                                        48, 58):
                                    if ord(SampleInfo.objects.filter(unique_code=j.unique_code).first().color_code[
                                           -2:-1]) in range(48, 58):
                                        new_status = SampleInfo.objects.filter(unique_code=j.unique_code).first().color_code[
                                                     0:-2] + \
                                                     str(int(SampleInfo.objects.filter(
                                                         unique_code=j.unique_code).first().color_code[-2:]) + 1)
                                    else:
                                        new_status = SampleInfo.objects.filter(unique_code=j.unique_code).first().color_code[
                                                     0:-1] + \
                                                     str(int(SampleInfo.objects.filter(
                                                         unique_code=j.unique_code).first().color_code[-1:]) + 1)
                                    SampleInfo.objects.filter(unique_code=j.unique_code).update(color_code=new_status)
                                else:
                                    SampleInfo.objects.filter(unique_code=j.unique_code).update(
                                        color_code=" __{}__重建库（未执行）1".format(sub_number))
                        else:
                            SampleInfo.objects.filter(unique_code=j.unique_code).update(
                                color_code=" __{}__重建库（未执行）1".format(sub_number))
                        lib.sample.add(SampleInfo.objects.filter(unique_code=j.unique_code).first())
                    except:
                        pass
                old = obj.libSubmit.lib_number
                if "_" in old:
                    new = old[0:-1] + str(int(old[-1]) + 1)
                else:
                    new = old + "_" + "1"
                lib.lib_number = new
                lib.save()
                del lib
                del md
                project.update(time_lib=datetime.datetime.now())
                # content = ""
                # for x in msg_email:
                #     content += x
                # content += "</table>"
                self.send_email(content="内容", html_message=msg_email,
                                sender=settings.EMAIL_FROM,
                                recipient_list=["love949872618@qq.com", ],
                                fail_silently=False)
                self.send_group_message(msg_dingding, "chat62dbddc59ef51ae0f4a47168bdd2a65b")
                self.message_user(request,"建库实验结果导入成功")
            else:
                pass
        super().save_model(request, obj, form, change)


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
        fields = ("id",'sample_number','seq_code',
        'seq_index', 'data_request','seq_data', 'seq_result', 'seq_note','is_rebuild')
        # export_order = ('sample_number','seq_code',
        # 'seq_index', 'data_request','seq_data', 'seq_result', 'seq_note','is_rebuild')

    def get_export_headers(self):
        return ["id","sample_number","文库号","Index","数据量要求","测序数据量"
            ,"结论(测序)","备注(测序)","选择是否重测序(0代表不重测序,1代表重测序)"]

    def get_diff_headers(self):
        return ["id","sample_number","文库号","Index","数据量要求","测序数据量"
            ,"结论(测序)","备注(测序)","选择是否重测序(0代表不重测序,1代表重测序)"]

    def export(self, queryset=None, *args, **kwargs):
        queryset_result = SampleInfoSeq.objects.filter(id=None)
        for i in queryset:
            queryset_result |= SampleInfoSeq.objects.filter(seqExecute=i)
        return super().export(queryset=queryset_result, *args, **kwargs)

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
            instance.is_rebuild = row['选择是否重测序(0代表不重测序,1代表重测序)']
            instance.save()
            return (instance, False)
        else:
            raise Exception("请核对样品编号")
            # return (self.init_instance(row), True)



class SeqExecuteAdmin(ImportExportActionModelAdmin,NotificationMixin):

    resource_class = SampleInfoSeqResource

    list_per_page = 50

    save_as_continue = False

    inlines = [SampleInfoSeqInline]

    save_on_top = False

    fields = ("seqSubmit", "seq_experimenter", "note", "upload_file",
              "is_submit")


    form = SeqExecuteForm

    appkey = DINGTALK_APPKEY

    appsecret = DINGTALK_SECRET

    filter_horizontal = ("seq_experimenter",)
    # list_display = ('seqSubmit', 'seq_experimenter', 'seq_end_date', 'note')
    list_display = ('seqSubmit', 'seq_end_date', 'note',"pooling","is_submit")

    exclude = ("seq_end_date","query_code")

    list_display_links = ('seqSubmit',)

    ordering = ('-id',)
    actions = ["processing_experiment", ]

    def processing_experiment(self,request,queryset):
        i = 0
        for obj in queryset:
            if obj.seq_experimenter.count()==0:
                i += 1
                for j in User.objects.filter(groups__id=13).all():
                    obj.seq_experimenter.add(j)
                obj.save()
        self.message_user(request,"{}个测序执行成功分配实验员".format(i))

    processing_experiment.short_description = "为所选中执行任务分配实验员" \
                                              ""
    def pooling(self,obj):
        if obj.seqSubmit.pooling_excel:
            return format_html(
            "<a href='{0}'>下载</a>" .format(obj.seqSubmit.pooling_excel.url))

        else:
            return "未上传"
    pooling.short_description = "Pooling表下载"

    def get_readonly_fields(self, request, obj=None):
        self.readonly_fields = []
        try:
            if obj.is_submit:
                self.readonly_fields = ('seqSubmit','seq_experimenter','upload_file','seq_end_date', 'note',"is_submit",)
                return self.readonly_fields
        except:
            return self.readonly_fields
        return self.readonly_fields

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "seq_experimenter":
            kwargs["queryset"] = User.objects.filter(groups__name="测序组")
        return super().formfield_for_manytomany( db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):

        Dinggroupid = DingtalkChat.objects.filter(chat_name="实验钉钉群-BMS").first().chat_id

        sub_number = obj.seqSubmit.subProject.sub_number

        project = SubProject.objects.filter(sub_number=sub_number)

        # 钉钉
        if project.first().is_status < 9:
            project.update(is_status=9)
            man = []
            for i in form.cleaned_data["seq_experimenter"]:
                man.append((i.last_name + i.first_name))
            self.send_group_message("编号{0}的测序任务执行中------，执行人:{1}".format(obj.seqSubmit,
                                                                         man), Dinggroupid)
            self.message_user(request,"编号{0}的测序任务执行中------，执行人:{1}".format(obj.seqSubmit,
                                                                         man))
            if not self.send_dingtalk_result:
                self.message_user(request,"钉钉发送失败")
        if obj.is_submit:
            # if not obj.upload_file:
            #     self.message_user(request,"测序结果报告")
            #     return None
            if project.first().is_status < 10:
                project.update(is_status=10)
            if not obj.seq_end_date:
                # 钉钉
                obj.seq_end_date = datetime.datetime.now()
                qs = obj.sampleinfoseq_set.all()
                if qs.count()==0:
                    self.message_user(request,"未选择样品！")
                    return None
                msg_dingding = "项目{0}的测序执行{1}结果已上传".format(project.first().sub_project, obj.seqSubmit)
                # msg_email = [
                #     "<h2>{0}</h2><br><table><tr><th>测序样品编号</th><th>样品名称</th><th>文库号</th><th>Index</th><th>数据量要求"
                #     "</th><th>测序数据量</th><th>结论(测序)</th><th>备注(测序)</th><th>选择是否重测序</th>"
                #     "</tr>".format(msg_dingding), ]
                md = md5()
                md.update(("lib" + str(time.time())).encode())
                key = md.hexdigest()
                obj.query_code = key
                data_url = "http://" + request.META.get("HTTP_HOST") + "/lims/getdata/?index=" + key
                msg_email = "编号：{0} 的建库实验完成，请点击<a href='{1}'>实验结果</a>查看<hr>".format(sub_number, data_url)

                for i in qs.filter(is_rebuild=0):
                    # msg_email.append(("<tr><td>{0}</td><td>{1}</td><td>{2}</td><td>{3}</td><td>{4}</td><td>{5}</td><td>{6}</td><td>{7}</td><td>{8}</td>"
                    #                      .format(i.sample_number, i.sample_name, i.seq_code, i.seq_index, i.data_request,
                    #                              i.seq_data,
                    #                              i.Seq_result[i.seq_result-1][1], i.seq_note,
                    #                              i.Rebulid[i.is_rebuild][1])))

                    SampleInfo.objects.filter(unique_code=i.unique_code).update(color_code="__{}__已测序".format(sub_number))
                # 建立重测序任务单
                seq = SeqSubmit()
                seq.project_manager_id = obj.seqSubmit.project_manager_id
                seq.id = str(int(SeqSubmit.objects.latest('id').id) + 1)
                seq.subProject = obj.seqSubmit.subProject
                for j in qs.filter(is_rebuild=1):
                    # msg_email.append((
                    #                      "<tr><td>{0}</td><td>{1}</td><td>{2}</td><td>{3}</td><td>{4}</td><td>{5}</td><td>{6}</td><td>{7}</td><td>{8}</td>"
                    #                      .format(j.sample_number, j.sample_name, j.seq_code, j.seq_index,
                    #                              j.data_request,
                    #                              j.seq_data,
                    #                              j.Seq_result[j.seq_result - 1][1], j.seq_note,
                    #                              j.Rebulid[j.is_rebuild][1])))
                    try:
                        if SampleInfo.objects.filter(unique_code=j.unique_code).first().color_code:
                            if ord(SampleInfo.objects.filter(unique_code=j.unique_code).first().color_code[-1:]) in range(48, 58):
                                if ord(SampleInfo.objects.filter(unique_code=j.unique_code).first().color_code[-1:]) in range(
                                        48, 58):
                                    if ord(SampleInfo.objects.filter(unique_code=j.unique_code).first().color_code[
                                           -2:-1]) in range(48, 58):
                                        new_status = SampleInfo.objects.filter(unique_code=j.unique_code).first().color_code[
                                                     0:-2] + \
                                                     str(int(SampleInfo.objects.filter(
                                                         unique_code=j.unique_code).first().color_code[-2:]) + 1)
                                    else:
                                        new_status = SampleInfo.objects.filter(unique_code=j.unique_code).first().color_code[
                                                     0:-1] + \
                                                     str(int(SampleInfo.objects.filter(
                                                         unique_code=j.unique_code).first().color_code[-1:]) + 1)
                                    SampleInfo.objects.filter(unique_code=j.unique_code).update(color_code=new_status)
                                else:
                                    SampleInfo.objects.filter(unique_code=j.unique_code).update(
                                        color_code=" __{}__重测序（未执行）1".format(sub_number))
                        else:
                            SampleInfo.objects.filter(unique_code=j.unique_code).update(
                                color_code=" __{}__重测序（未执行）1".format(sub_number))
                        seq.sample.add(SampleInfo.objects.filter(unique_code=j.unique_code).first())
                    except:
                        pass
                old = obj.seqSubmit.seq_number
                if "_" in old:
                    new = old[0:-1] + str(int(old[-1]) + 1)
                else:
                    new = old + "_" + "1"
                seq.seq_number = new
                seq.save()
                del seq
                del md
                # content = ""
                # for x in msg_email:
                #     content += x
                # content += "</table>"
                self.send_email(content="内容", html_message=msg_email,
                                sender=settings.EMAIL_FROM,
                                recipient_list=["love949872618@qq.com", ],
                                fail_silently=False)
                self.send_group_message(msg_dingding, "chat62dbddc59ef51ae0f4a47168bdd2a65b")
                self.message_user(request,"测序实验结果已导入")
            else:
                pass
        super().save_model(request, obj, form, change)

#样品池管理
class Extsampleadmin(admin.ModelAdmin):
    list_display = ["sample_number","sample_name","unique_code","extExecute","quality_control_conclusion","is_rebuild"]
    list_display_links = ["sample_number"]
    search_fields = ["is_rebuild","quality_control_conclusion"]
class Libsampleadmin(admin.ModelAdmin):
    list_display = ["sample_number", "sample_name", "unique_code", "libExecute", "lib_code",
                    "lib_note","is_rebuild"]
    list_display_links = ["sample_number"]
    search_fields = ["is_rebuild",]
class Seqsampleadmin(admin.ModelAdmin):
    list_display = ["sample_number", "sample_name", "unique_code", "seqExecute",
                 "seq_note","is_rebuild"]
    list_display_links = ["sample_number"]
    search_fields = ["is_rebuild",]

BMS_admin_site.register(Extmethod,ExtmothodAdmin)
BMS_admin_site.register(Testmethod,TestmothodAdmin)
BMS_admin_site.register(ExtExecute,ExtExecuteAdmin)
BMS_admin_site.register(LibExecute,LibExecuteAdmin)
BMS_admin_site.register(SeqExecute,SeqExecuteAdmin)
BMS_admin_site.register(SampleInfoExt,Extsampleadmin)
BMS_admin_site.register(SampleInfoLib,Libsampleadmin)
BMS_admin_site.register(SampleInfoSeq,Seqsampleadmin)