from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.core.exceptions import PermissionDenied
from django.template.response import TemplateResponse
from django.contrib.auth.models import Group, User
from django.utils.html import format_html
from import_export import resources
from import_export.admin import ImportExportActionModelAdmin,ExportActionModelAdmin
from import_export.forms import ConfirmImportForm, ImportForm
from django.utils.translation import ugettext_lazy as _

from BMS.admin_bms import BMS_admin_site
from BMS.notice_mixin import NotificationMixin
from pm.models import SubProject

try:
    from django.utils.encoding import force_text
except ImportError:
    from django.utils.encoding import force_unicode as force_text
from sample.models import SampleInfoForm, SampleInfo
import datetime
from django.conf import settings
from django.core.mail import send_mail
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
...

# def send(request,):
#     msg=''
#     send_mail('标题','内容',settings.EMAIL_FROM,
#               '目标邮箱',
#               html_message=msg)
#     return HttpResponse('ok')



#选择可编辑字段
def get_editable(obj):
    if obj.sample_status == 2:
        return (obj.sampleinfoformid,)
    else:
        return (obj.sampleinfoformid,)
get_editable.short_description = "点击查看详情"
#编辑可看字段
# def get_display(obj):
#     if obj.sample_status:
#         return (obj.sampleinfoformid,)
#     else:
#         return (obj.sampleinfoformid,obj.time_to_upload,obj.color_status,obj.file_link,obj.jindu_status)

#选择样品编号对应月份字母

Monthchoose = {1:"A",2:"B",3:"C",4:"D",5:"E",6:"F",7:"G",8:"H",9:"I",10:"G",11:"K",12:"L",}

class Sampleadmin(ExportActionModelAdmin):
    search_fields = ["sample_type",]
    list_display = ["sampleinfoform","sample_name","unique_code"]
    list_display_links = ["unique_code"]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        try:
            current_group_set = Group.objects.filter(user=request.user)
            if len(current_group_set) == 1:
                if current_group_set[0].name == "实验部":
                    return qs
                elif current_group_set[0].name == "合作伙伴":
                    return qs.filter(sampleinfoform__partner_email=request.user)
                else:
                    return qs
            else:
                names = [i.name for i in current_group_set]
                # if "实验部" in names:
                #     return qs
                # elif "项目管理" in names:
                #     return qs
                return qs
        except:
            return qs




class SampleInline(admin.TabularInline):
    model = SampleInfo
    fields = ['sampleinfoform','sample_name','sample_receiver_name','tube_number','sample_type','is_extract','data_request'
        ,'remarks'
              ]
    # readonly_fields = ['sampleinfoform','sample_name','sample_receiver_name','tube_number','is_extract','remarks','data_request','sample_type']


    def get_readonly_fields(self, request, obj=None):
        readonly_fields = ["",]
        try:
            current_group_set = Group.objects.get(user=request.user)
            if current_group_set.name == "合作伙伴":
                readonly_fields = ['sampleinfoform', 'sample_name', 'sample_receiver_name', 'tube_number', 'is_extract',
                                   'remarks', 'data_request', 'sample_type']
                return readonly_fields
            else:
                return readonly_fields
        except:
            return readonly_fields

    #设置不能修改确认后的样品详情列表
    def has_change_permission(self, request, obj=None):
        try:
            if obj.sample_status == 2 :
                return False
        except:
            pass
        return super().has_change_permission(request, obj=None)

    def has_add_permission(self, request, obj):
        try:
            if obj.sample_status == 2:
                return False
        except:
            pass
        return super().has_change_permission(request, obj=None)


#上传管理器
class SampleInfoResource(resources.ModelResource):
    class Meta:
        model = SampleInfo
        skip_unchanged = True
        fields = ('id','sampleinfoform',
        'sample_name', 'sample_receiver_name','sample_type', 'tube_number', 'is_extract', 'remarks','data_request',"sample_species")
        export_order = ('id','sampleinfoform',
        'sample_name', 'sample_receiver_name','sample_type', 'tube_number', 'is_extract', 'remarks','data_request',"sample_species")

    def get_export_headers(self):
        return ["id","概要信息编号","样品名","实际收到样品名"
            ,"样品类型(1-g DNA,2-组织,3-细胞,4-土壤,5-粪便其他未提取（请描述))","管数","是否需要提取(0-不需要，1-需要)","备注","数据量要求","物种"]
    def get_diff_headers(self):
        return ["id","概要信息编号","样品名","实际收到样品名","样品类型(1-g DNA,2-组织,3-细胞,4-土壤,5-粪便其他未提取（请描述))",
                "管数","是否需要提取(0-不需要，1-需要)","备注","数据量要求","物种"]

    def get_or_init_instance(self, instance_loader, row):
        """
        Either fetches an already existing instance or initializes a new one.
        """
        instance = self.get_instance(instance_loader, row)
        if instance:
            instance.sampleinfoform = SampleInfoForm.objects.get(sampleinfoformid=row['概要信息编号'])
            instance.sample_name = row['样品名']
            instance.sample_receiver_name = row['实际收到样品名']
            instance.sample_type = row['样品类型(1-g DNA,2-组织,3-细胞,4-土壤,5-粪便其他未提取（请描述))']
            instance.tube_number = row['管数']
            instance.is_extract = row['是否需要提取(0-不需要，1-需要)']
            instance.remarks = row['备注']
            instance.data_request = row['数据量要求']
            instance.sample_species = row["物种"]
            instance.save()
            return (instance, False)
        else:
            return (self.init_instance(row), True)


    def init_instance(self, row=None):
        if not row:
            row = {}
        instance = self._meta.model()
        for attr, value in row.items():
            setattr(instance, attr, value)
        if SampleInfo.objects.all().count() == 0:
            instance.id = "1"
        else:
            instance.id = str(int(SampleInfo.objects.latest('id').id)+1)
        instance.sampleinfoform = SampleInfoForm.objects.get(sampleinfoformid=row['概要信息编号'])
        instance.sample_name = row['样品名']
        instance.sample_receiver_name = row['实际收到样品名']
        instance.sample_type = row['样品类型(1-g DNA,2-组织,3-细胞,4-土壤,5-粪便其他未提取（请描述))']
        instance.tube_number = row['管数']
        instance.is_extract = row['是否需要提取(0-不需要，1-需要)']
        instance.remarks = row['备注']
        instance.data_request = row['数据量要求']
        instance.sample_species = row["物种"]
        if SampleInfo.objects.all().count() == 0:
            instance.sample_number = str(datetime.datetime.now().year) + \
                                     Monthchoose[datetime.datetime.now().month] + "0001"
            instance.unique_code = 'RY_Sample_1'
        else:
            instance.sample_number = str(datetime.datetime.now().year) + \
                                 Monthchoose[datetime.datetime.now().month] + "000" + str(SampleInfo.objects.latest('id').id + 1)
            instance.unique_code = 'RY_Sample_' + str(SampleInfo.objects.latest('id').id + 1)
        return instance


    def export(self, queryset=None, *args, **kwargs):
        queryset_result = SampleInfo.objects.filter(id=None)
        for i in queryset:
            queryset_result |= SampleInfo.objects.filter(sampleinfoform=i)
        return super().export(queryset=queryset_result,*args, **kwargs)


#样品概要管理
class SampleInfoFormAdmin(ImportExportActionModelAdmin,NotificationMixin):

    resource_class = SampleInfoResource


    inlines = [SampleInline]

    list_per_page = 50

    search_fields = ("sample_status","partner")

    save_as_continue = False

    save_on_top = False

    autocomplete_fields = ("saler",)

    raw_id_fields = ("saler",)

    ordering = ('-id',)

    radio_fields = {
        "transform_status": admin.HORIZONTAL,
        "sample_diwenjiezhi": admin.HORIZONTAL,
        "management_to_rest": admin.HORIZONTAL,
        "sample_status":admin.HORIZONTAL,
        "sample_diwenzhuangtai":admin.HORIZONTAL,
    }

    list_display = ('sampleinfoformid', "partner", 'time_to_upload', 'color_status', 'file_link', 'jindu_status')

    list_display_links = ('sampleinfoformid',)

    def process_result(self, result, request):
        sample = SampleInfo.objects.latest("id").sampleinfoform
        try:
            send_mail('样品核对通知', '<h3>编号{0}的样品核对信息已上传，请查看核对</h3>'.format(sample.sampleinfoformid),
                      settings.EMAIL_FROM,
                      [sample.partner_email, ],
                          fail_silently=False)
        except:
            self.message_user(request,"邮件发送失败")
        return super(SampleInfoFormAdmin, self).process_result(result, request)

    actions = ['make_sampleinfoform_submit','insure_sampleinfoform']


    def get_queryset(self, request):
        qs = super(SampleInfoFormAdmin, self).get_queryset(request)
        try:
            current_group_set = Group.objects.filter(user=request.user)
            if len(current_group_set) == 1:
                if current_group_set[0].name == "实验部":
                    return qs
                elif current_group_set[0].name == "合作伙伴":
                    return qs.filter(partner_email=request.user)
                elif current_group_set[0].name == "业务员（销售）":
                    return qs.filter(saler=request.user)
                elif current_group_set.name == "项目管理":
                    subproject = SubProject.objects.filter(project_manager=request.user)
                    result = qs.filter(id=None)
                    for i in subproject:
                        result |= (qs & i.sampleInfoForm.all())
                    return result
            else:
                names = [i.name for i in current_group_set]
                if "业务员（销售）" in names:
                    return qs.filter(saler=request.user)
                elif "项目管理" in names:
                    subproject = SubProject.objects.filter(project_manager=request.user)
                    result = qs.filter(id=None)
                    for i in subproject:
                        result |= (qs & i.sampleInfoForm.all())
                    return result
                elif "实验部" in names:
                    return qs
                else:
                    return qs
        except:
            return qs

    #可以改变增加表单里的内容
    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_delete'] = True
        # if not Invoice.objects.get(id=object_id).invoice_code and not request.user.has_perm('fm.add_invoice'):
        extra_context['show_save'] = True
        extra_context['show_save_as_new'] = True
        # extra_context['show_save_and_continue'] = False
        return super().change_view(request, object_id, form_url, extra_context=extra_context)

    def has_change_permission(self, request, obj=None):
        try:
            if obj.sample_status == 2:
                return False
        except:
            return True
        return super().has_change_permission(request, obj=None)

    def import_action(self, request, *args, **kwargs):

        resource = self.get_import_resource_class()(**self.get_import_resource_kwargs(request, *args, **kwargs))

        context = self.get_import_context_data()

        import_formats = self.get_import_formats()
        form_type = self.get_import_form()
        form = form_type(import_formats,
                         request.POST or None,
                         request.FILES or None)

        if request.POST and form.is_valid():
            input_format = import_formats[
                int(form.cleaned_data['input_format'])
            ]()
            import_file = form.cleaned_data['import_file']
            # first always write the uploaded file to disk as it may be a
            # memory file or else based on settings upload handlers
            tmp_storage = self.write_to_tmp_storage(import_file, input_format)

            # then read the file, using the proper format-specific mode
            # warning, big files may exceed memory
            try:
                data = tmp_storage.read(input_format.get_read_mode())
                if not input_format.is_binary() and self.from_encoding:
                    data = force_text(data, self.from_encoding)
                dataset = input_format.create_dataset(data)
            except UnicodeDecodeError as e:
                return HttpResponse(_(u"<h1>Imported file has a wrong encoding: %s</h1>" % e))
            except Exception as e:
                return HttpResponse(
                    _(u"<h1>%s encountered while trying to read file: %s</h1>" % (type(e).__name__, import_file.name)))
            result = resource.import_data(dataset, dry_run=True,
                                          raise_errors=False,
                                          file_name=import_file.name,
                                          user=request.user)

            context['result'] = result

            if not result.has_errors():
                context['confirm_form'] = ConfirmImportForm(initial={
                    'import_file_name': tmp_storage.name,
                    'original_file_name': import_file.name,
                    'input_format': form.cleaned_data['input_format'],
                })

        context.update(self.admin_site.each_context(request))

        context['title'] = _("Import")
        context['form'] = form
        context['opts'] = self.model._meta
        context['fields'] = [f.column_name for f in resource.get_user_visible_fields()]

        request.current_app = self.admin_site.name
        return TemplateResponse(request, [self.import_template_name],
                                context)

    def write_to_tmp_storage(self, import_file, input_format):
        tmp_storage = self.get_tmp_storage_class()()
        data = bytes()
        for chunk in import_file.chunks():
            data += chunk

        tmp_storage.save(data, input_format.get_read_mode())
        return tmp_storage

    def get_context_data(self, **kwargs):
        return {}
    def get_import_context_data(self, **kwargs):
        return self.get_context_data(**kwargs)

    def get_import_form(self):
        '''
        Get the form type used to read the import format and file.
        '''
        return ImportForm

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "saler":
            kwargs["queryset"] = User.objects.filter(groups__name="业务员（销售）")
        if db_field.name == "transform_contact":
            kwargs["queryset"] = User.objects.filter(groups__name="实验部")
        if db_field.name == "sample_receiver":
            kwargs["queryset"] = User.objects.filter(groups__name="实验部")
        if db_field.name == "sample_checker":
            kwargs["queryset"] = User.objects.filter(groups__name="实验部")
        return super(SampleInfoFormAdmin,self).formfield_for_foreignkey(db_field, request, **kwargs)

    # def save_related(self, request, form, formsets, change):

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for obj in formset.deleted_objects:
            obj.delete()
        if instances:
            for instance in instances:
                if not (instance.unique_code and instance.sample_number):
                    instance.unique_code = 'RY_Sample_' + str(SampleInfo.objects.latest('id').id + 1)
                    instance.sample_number = str(datetime.datetime.now().year) + \
                                      Monthchoose[datetime.datetime.now().month] + "000" + str(
                        SampleInfo.objects.latest('id').id + 1)
                instance.save()
                formset.save_m2m()


    def save_model(self, request, obj, form, change):
        if not obj.time_to_upload:
            obj.time_to_upload = datetime.datetime.now()
        try:
            current_group_set = Group.objects.get(user=request.user)
            if not obj.sampleinfoformid:
                if SampleInfoForm.objects.all().count() == 0:
                    obj.sampleinfoformid = request.user.username + "-" + obj.partner +\
                                                   '-' + str(datetime.datetime.now().year) + "-"+ \
                                                   str(datetime.datetime.now().month) + '-' + \
                                                    str(datetime.datetime.now().day)                  + "_" + \
                                                     "1"
                else:
                    obj.sampleinfoformid = request.user.username + "-" + obj.partner +\
                                               '-' +str(datetime.datetime.now().year)+ "-"+ \
                                               str(datetime.datetime.now().month) + '-'+ str(datetime.datetime.now().day) +\
                                                 "_" + \
                                               str(int(SampleInfoForm.objects.latest("id").id)+1)
                obj.partner_email = request.user.username
                obj.save()
            if current_group_set.name == "合作伙伴":
                if obj.sample_status == 1 and obj.arrive_time:
                    obj.sample_status = 2
                    obj.save()
                    msg = "<h3>{0}客户的样品概要（{1}）信息已确认</h3>".format(obj.partner, obj.sampleinfoformid)
                    try:
                        self.send_email("<h3>{0}客户的样品概要（{1}）信息已确认</h3>".format(obj.partner, obj.sampleinfoformid),
                                        settings.EMAIL_FROM,
                                        ["love949872618@qq.com", ],
                                        fail_silently=False)
                        self.send_group_message(msg,"chat62dbddc59ef51ae0f4a47168bdd2a65b")
                    except:
                        self.message_user(request,"邮箱发送失败")
                    if not self.send_dingtalk_result:
                        self.message_user(request,"钉钉发送失败")
                    self.message_user(request,"审核成功！")
            else:
                obj.save()
        except:
            obj.save()
         #根据身份获取动作

    def get_actions(self, request):
        actions = super().get_actions(request)
        try:
            current_group_set = Group.objects.filter(user=request.user)
            names = [i.name for i in current_group_set]
        except:
            # print(actions)
            return None
        if current_group_set.name == "合作伙伴":
            # del actions['export_admin_action']
            return actions
        else:
            # del actions['export_admin_action']
            # del actions['make_sampleinfoform_submit']
            del actions['insure_sampleinfoform']
            # del actions['test1']
            return actions
    #提交并发送邮件
    def insure_sampleinfoform(self,request,queryset):
        """
        确认信息
        :param request:
        :param queryset:
        :return:
        """
        i = ''
        n = 0
        for obj in queryset:
            if obj.sample_status == 0:
                obj.sample_status = 1
                msg = "<h3>{0}客户的样品概要信息已上传，请核对</h3>".format(obj.partner)
                try:
                    send_mail('样品收到通知', '{0}客户的样本已经上传，请查看核对'.format(obj.partner), settings.EMAIL_FROM,
                              ["love949872618@qq.com", ],
                              fail_silently=False)
                except:
                    self.message_user(request,"邮箱发送失败")
                self.send_work_notice(msg, settings.DINGTALK_AGENT_ID, "00000")
                if not self.send_dingtalk_result:
                    self.message_user(request,"钉钉发送失败")
                obj.time_to_upload = datetime.datetime.now()
                obj.save()
                n += 1
            elif obj.sample_status == 1:
                self.message_user(request,"该概要表已经提交，请勿重复提交")
            else:
                self.message_user(request,"不可提交已审核内容")


    insure_sampleinfoform.short_description = '样品信息表单提交（并发送邮件）'

    # #确认
    # def make_sampleinfoform_submit(self, request, queryset):
    #     """
    #     提交样品信息表单
    #     """
    #     i = ''
    #     n = 0
    #     for obj in queryset:
    #         if obj.sample_status == 1 and obj.arrive_time:
    #             obj.sample_status = 2
    #             obj.save()
    #             msg = "<h3>{0}客户的样品概要（{1}）信息已确认</h3>".format(obj.partner,obj.sampleinfoformid)
    #             self.send_email("<h3>{0}客户的样品概要（{1}）信息已确认</h3>".format(obj.partner,obj.sampleinfoformid), settings.EMAIL_FROM,
    #                       ["love949872618@qq.com",],
    #                       fail_silently=False)
    #             self.send_work_notice(msg, settings.DINGTALK_AGENT_ID, "00000")
    #         else:
    #             n += 1
    #
    # #提示邮件
    # make_sampleinfoform_submit.short_description = '样品信息表单确认'

    def get_readonly_fields(self, request, obj=None):
        """  重新定义此函数，限制普通用户所能修改的字段  """
        # if request.user.is_superuser:
        #     self.readonly_fields = []
        #     return self.readonly_fields
        try:
            current_group_set = Group.objects.get(user=request.user)
            # print(current_group_set.name)
            if current_group_set.name == "实验部":
                if obj.sample_status==2:
                    self.readonly_fields = ('transform_company',"partner", 'transform_number',
                                        'transform_contact', 'transform_phone',
                                        'transform_status', 'sender_address', 'partner', 'partner_company',
                                        'partner_phone', 'partner_email', 'saler',
                                        'project_type',
                                        'sample_num', 'extract_to_pollute_DNA',
                                        'management_to_rest', 'file_teacher',"download_teacher","download_tester",
                                        "sampleinfoformid", "time_to_upload","information_email","arrive_time",'sample_receiver','sample_checker','sample_diwenjiezhi',
                            'sample_diwenzhuangtai',"note_receive")

                else:
                    self.readonly_fields = ('transform_company', "partner", 'transform_number',
                                        'transform_contact', 'transform_phone',
                                        'transform_status', 'sender_address', 'partner', 'partner_company',
                                        'partner_phone', 'partner_email', 'saler',
                                        'project_type',
                                        'sample_num', 'extract_to_pollute_DNA',
                                        'management_to_rest', 'file_teacher', "download_teacher", "download_tester",
                                        "sampleinfoformid", "time_to_upload", "information_email",)
                return self.readonly_fields

            if obj.sample_status:
                self.readonly_fields = ('transform_company','transform_number',"partner",
                           'transform_contact','transform_phone',
                           'transform_status','sender_address','partner', 'partner_company', 'partner_phone','partner_email', 'saler',
                                        'sample_receiver', 'sample_checker', 'sample_diwenzhuangtai','project_type','arrive_time','sample_diwenjiezhi',
                           'sample_num','extract_to_pollute_DNA',"download_teacher","download_tester",
                            'management_to_rest','file_teacher',
                            "sampleinfoformid","time_to_upload","information_email")
                return self.readonly_fields
        except:
            self.readonly_fields = ["",]
            return self.readonly_fields
        else:
            self.readonly_fields = ["",]
            return self.readonly_fields


    # def change_view(self, request, object_id, form_url='', extra_context=None):
    #     change_obj = DataPaperStore.objects.filter(pk=object_id)
    #     self.get_readonly_fields(request, obj=change_obj)
    #     return super(DataPaperStoreAdmin, self).change_view(request, object_id, form_url, extra_context=extra_context)

    def get_fieldsets(self, request, obj=None):
        fieldsets = (
            ['物流信息', {
                'fields': (('transform_company', 'transform_number',
                            'transform_contact', 'transform_phone'),
                           'transform_status', 'sender_address'),
            }]
            , ['客户信息', {
                'fields': (
                ('partner', 'partner_company'), ('partner_phone', "information_email", 'partner_email'), 'saler'),
            }], ['收货信息', {
                'fields': (('man_to_upload', 'sample_receiver', 'sample_checker', 'sample_diwenzhuangtai'),),
            }], ['项目信息', {
                'fields': ('project_type', 'arrive_time', 'sample_diwenzhuangtai',
                           'sample_num', 'extract_to_pollute_DNA',
                           'management_to_rest', 'file_teacher',
                           "sampleinfoformid", "time_to_upload"),
            }])
        try:
            current_group_set = Group.objects.filter(user=request.user)
            names = [s.name for s in current_group_set]
            if current_group_set[0].name == "实验部" or "实验部" in names:
                fieldsets = (
            ['物流信息', {
                'fields': ('transform_company','transform_number',
                           'transform_contact','transform_phone',
                           'transform_status','sender_address'),
            }],['客户信息',{
                'fields': ('partner', 'partner_company', 'partner_phone',"information_email",'partner_email', 'saler'),
            }],['项目信息',{
                'fields': ( 'project_type',
                           'sample_num','extract_to_pollute_DNA',
                            'management_to_rest','file_teacher',
                            "sampleinfoformid",
                            "time_to_upload"),
                            }],['收货信息',{
                'fields': ( "arrive_time",'sample_receiver','sample_checker','sample_diwenjiezhi',
                            'sample_diwenzhuangtai',"note_receive"),
            }])

            elif current_group_set[0].name == "合作伙伴":
                fieldsets = (
                ['物流信息', {
                    'fields': (('transform_company', 'transform_number'),(
                               'transform_contact', 'transform_phone',
                               'sender_address',),('transform_status',)),
                }], ['客户信息', {
                    'fields': ( ("partner","information_email"),('partner_company', 'partner_phone'),('saler'),),
                }], ['项目信息', {
                    'fields': ('project_type',
                               'sample_num', 'extract_to_pollute_DNA',
                               'management_to_rest', 'file_teacher',
                               # "sampleinfoformid",
                               ),
                }])
        except:
            fieldsets = (
                ['物流信息', {
                    'fields': (('transform_company','transform_number',
                               'transform_contact','transform_phone'),
                               'transform_status','sender_address'),
                }]
                ,['客户信息',{
                'fields': (('partner', 'partner_company'), ('partner_phone',"information_email",'partner_email'), 'saler'),
            }],['收货信息',{
                'fields': ( ('man_to_upload','sample_receiver','sample_checker', 'sample_diwenzhuangtai'),),
            }],['项目信息',{
                'fields': ( 'project_type','arrive_time','sample_diwenzhuangtai',
                           'sample_num','extract_to_pollute_DNA',
                            'management_to_rest','file_teacher',
                            "sampleinfoformid","time_to_upload"),
                            }])
        return fieldsets


    list_filter = ("sample_status",'time_to_upload')
BMS_admin_site.register(SampleInfoForm,SampleInfoFormAdmin)
BMS_admin_site.register(SampleInfo,Sampleadmin)
# admin.site.register(Realbio_User, UserAdmin)
#全站范围内禁用删权限
# admin.site.disable_action('delete_selected')
# admin.site.register(SampleInfo)
# admin.site.register(Product,ProAdmin)
# admin.site.site_header = '杭州锐翌BMS系统'
# admin.site.site_title = '杭州锐翌'




# class SampleInfoAdmin(ImportExportActionModelAdmin):
#     resource_class = SampleInfoResource
#
#
#
# admin.site.register(SampleInfo,SampleInfoAdmin)