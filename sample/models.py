from django.db import models
from django.contrib.auth import admin
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser

# class Realbio_User(AbstractUser):
#     is_teacher = models.NullBooleanField(blank=True,null=True,verbose_name="是否是老师")
#     is_projectcharge = models.NullBooleanField(blank=True,null=True,verbose_name="是否是项目主管")
#     is_tester =  models.NullBooleanField(blank=True,null=True,verbose_name="是否是实验员")
#     is_saler = models.NullBooleanField(blank=True, null=True, verbose_name="是否是销售代表")
#
#     class Meta:
#         verbose_name = "用户信息"
#         verbose_name_plural = verbose_name
#
#     def __str__(self):
#         return self.username
from django.utils.html import format_html

from BMS.settings import MEDIA_ROOT
import datetime

def upload_to(instance, filename):
    return '/'.join(['teachers',str(datetime.datetime.now().year)+'-'+str(datetime.datetime.now().month),instance.partner,filename])
def upload_to1(instance, filename):
    return '/'.join(['testers',str(datetime.datetime.now().year)+'-'+str(datetime.datetime.now().month),instance.man_to_upload,filename])

# class Employee(models.Model):
#     name = models.CharField(max_length=200,verbose_name="姓名")
#     department = models.CharField(max_length=200,verbose_name="部门")
#
#     def __str__(self):
#         return self.department +"----------"+ self.name


class SampleInfoForm(models.Model):

    # sampleinfoformid = models.

    #项目选项
    Project_choices = (
        (1, '微生物宏基因组测序'),
        (2, '微生物扩增子测序------16S'),
        (3, '微生物扩增子测序------ITS'),
        (4, '微生物扩增子测序------古菌；其他'),
        (5, '细菌基因组测序------小片段文库'),
        (6, '细菌基因组测序------PCR-free文库'),
        (7, '细菌基因组测序------2K大片段文库'),
        (8, '细菌基因组测序------5K大片段文库'),
        (9, '细菌基因组测序------SMRT cell DNA 文库'),
        (10, '真菌基因组测序------小片段文库'),
        (11, '真菌基因组测序------PCR-free文库'),
        (12, '真菌基因组测序------2K大片段文库'),
        (13, '真菌基因组测序------5K大片段文库'),
        (14, '真菌基因组测序------SMRT cell DNA 文库'),
        (15, '动植物denovo------180bp'),
        (16, '动植物denovo------300bp'),
        (17, '动植物denovo------500bp'),
        (18, '动植物denovo------2K'),
        (19, '动植物denovo------5K'),
        (20, '动植物denovo------10K'),
        (21, '动植物denovo------20K'),
        (22, '动植物重测序'),
        (23, '人重测序'),
        (24, '外显子测序'),
        (25, '其他'),
    )

    #样品处理选项
    Management_to_the_rest = (
        (1, '项目结束后剩余样品立即返还给客户'),
        (2, '项目结束后剩余样品暂时由锐翌基因保管'),
    )

    #样品状态选项
    Sample_status = (
        (0, '未提交'),
        (1, '已提交，未审核'),
        (2, '已审核')
        )
    #进度
    Sample_jindu = (
        (0, '项目待启动'),
        (1, '项目已完结'),
        )

    #运输状态
    TransForm_Status  = (
        (0, '干冰'),
        (1, '冰袋'),
        (2, '无'),
        (3, '其他'),
        )
    #低温介质到达时状态
    Arrive_Status = (
        (0, '不合格'),
        (1, '合格'),
        )


    #物流信息
    transform_company = models.CharField(max_length=200,verbose_name="运输公司",default="顺丰")
    transform_number = models.CharField(max_length=200,verbose_name="快递单号")
    transform_contact = models.CharField(max_length=200,verbose_name="寄样人姓名",default="")
    transform_phone = models.BigIntegerField(verbose_name="寄样联系人电话")
    transform_status = models.IntegerField(choices=TransForm_Status,verbose_name="运输状态",default=0)
    sender_address = models.CharField(max_length=200, verbose_name="寄件人联系地址", default='')


    #客户信息
    partner = models.CharField(max_length=200,verbose_name="客户姓名",default="")
    information_email = models.EmailField(verbose_name="消息接收邮箱",default='')
    partner_company = models.CharField(max_length=200, verbose_name="合作伙伴单位")
    partner_phone = models.BigIntegerField(verbose_name="合作人联系电话")
    partner_email = models.EmailField(verbose_name="合作邮箱",default='')

    saler = models.ForeignKey(User,related_name="销售联系人",verbose_name="销售代表",blank=True,null=True,on_delete=models.SET_NULL)

    #服务类型
    project_type = models.IntegerField(choices=Project_choices,verbose_name="项目类型",default=2)

    #样品信息
    sample_num = models.IntegerField(verbose_name="样品数量")
    extract_to_pollute_DNA = models.NullBooleanField("DNA提取是否可能有大量非目标DNA污染",default=False)
    management_to_rest = models.IntegerField(choices=Management_to_the_rest,
                                             verbose_name="剩余样品处理方式",default=2)

    sample_diwenjiezhi = models.IntegerField(choices=TransForm_Status,verbose_name="低温保存介质",default=0)

    #上传信息
    # download_model = models.CharField(max_length=200,verbose_name="点击下载表格",default="www.")
    file_teacher = models.FileField(upload_to=upload_to,verbose_name='客户上传文件',default='')
    # file_tester = models.FileField(upload_to=upload_to1,verbose_name='实验室上传文件',blank=True,null=True,default='')
    man_to_upload = models.ForeignKey(User,related_name="上传文件人", verbose_name="公司上传者",blank=True,null=True,
                                                        on_delete=models.SET_NULL)
    time_to_upload = models.DateField(verbose_name="上传时间",blank=True,null=True)
    sampleinfoformid = models.CharField(max_length=200, verbose_name="客户上传表格编号")

    #样品接收信息
    arrive_time = models.DateField(verbose_name="样品接收时间",null=True,blank=True)
    sample_receiver = models.ForeignKey(User,related_name="样品接收人",verbose_name="样品接收人",null=True,blank=True,on_delete=models.SET_NULL)
    sample_checker = models.ForeignKey(User,related_name="物流接收人",verbose_name="样品核对人",blank=True,null=True,on_delete=models.SET_NULL)
    sample_status = models.IntegerField(choices=Sample_status,verbose_name="样品状态",default=0)
    sample_jindu = models.IntegerField(choices=Sample_jindu,verbose_name="样品进度",default=0)
    sample_diwenzhuangtai = models.IntegerField(choices=Arrive_Status,verbose_name="低温介质到达时状态",default=1)
    note_receive = models.TextField(verbose_name="样品接收备注",blank=True,null=True)
    #颜色显示
    color_code = models.CharField(max_length=6,default='')
    color_code1 = models.CharField(max_length=6, default='')

    def __str__(self):
        return self.sampleinfoformid

    class Meta:
        verbose_name = "样品概要"
        verbose_name_plural = "样品概要"


    def file_link(self):
        if self.file_teacher:
            return format_html(
            "<a href='{0}'>下载</a>" .format(self.file_teacher.url))

        else:
            return "未上传"

    file_link.allow_tags = True
    file_link.short_description = "已上传信息"

    #状态颜色
    def color_status(self):
        if self.sample_status == 0:
            self.color_code = "red"
        elif self.sample_status == 1:
            self.color_code = "green"
        return format_html(
            '<span style="color: {};">{}</span>',
            self.color_code,
            self.Sample_status[self.sample_status][1],)

    color_status.short_description = "状态"

    #进度颜色
    def jindu_status(self):
        if self.sample_jindu == 1:
            self.color_code1 = "red"
        elif self.sample_jindu == 0:
            self.color_code1 = "blue"
        return format_html(
            '<span style="color: {};">{}</span>',
            self.color_code1,
            self.Sample_jindu[self.sample_jindu][1],)

    jindu_status.short_description = "进度"

Monthchoose = {1:"A",2:"B",3:"C",4:"D",5:"E",6:"F",7:"G",8:"H",9:"I",10:"G",11:"K",12:"L",}

class SampleInfo(models.Model):
    #样品种类
    Type_of_Sample = (
        (1, 'g DNA'),
        (2, '组织'),
        (3, '细胞'),
        (4, '土壤'),
        (5, '粪便其他未提取（请描述）'),
    )
    # #样品状态
    # Status_of_Sample = (
    #     (1, '已入库'),
    #     (2, '已立项'),
    # )
    #样品保存介质
    Preservation_medium = (
        (1, '纯水'),
        (2, 'TE buffer'),
        (3, '无水乙醇'),
        (4, 'Trizol其他'),
    )

    #是否经过RNase处理
    Is_RNase_processing = (
        (1, '是'),
        (2, '否'),
    )

    #状态
    Sample_status = (
        (0,"已核对"),
        (1, "抽提失败"),
        (2, "建库失败"),
        (3, "测序失败"),
    )

    #概要
    unique_code = models.CharField(max_length=60, verbose_name="对应样品池唯一编号",default='')
    sampleinfoform = models.ForeignKey(SampleInfoForm,verbose_name="对应样品概要编号",blank=True,null=True,on_delete=models.CASCADE)
    sample_number = models.CharField(max_length=50,verbose_name="样品编号", blank=True,null=True)
    sample_name = models.CharField(max_length=50,verbose_name="样品名称")
    sample_receiver_name = models.CharField(max_length=50,verbose_name="实际接收样品名称(与客户所给名称不同时标红)") #*
    density = models.DecimalField('浓度ng/uL', max_digits=5, decimal_places=3, blank=True,null=True)
    volume = models.DecimalField('体积uL', max_digits=5, decimal_places=3,blank=True, null=True)
    purity = models.CharField(max_length=200,verbose_name="纯度",blank=True,null=True)
    tube_number = models.IntegerField(verbose_name="管数量") #*
    is_extract = models.NullBooleanField(verbose_name="是否需要提取",default=False)
    remarks = models.CharField(max_length=200,verbose_name="备注",blank=True,null=True)
    status = models.IntegerField(choices=Sample_status,verbose_name="样品可用状态",blank=True,default=0)
    sample_species = models.CharField(max_length=200, verbose_name="物种", default='')
    #数据量要求
    data_request = models.CharField(max_length=200,verbose_name="数据量要求",blank=True,null=True)
    color_code = models.CharField(max_length=16,blank=True,null=True,default="")
    sample_type = models.IntegerField(choices=Type_of_Sample,verbose_name="样品类型",default=1)
    color_code2 = models.CharField(max_length=16,blank=True,null=True,default="")

    @property
    def color_diff(self):
        return self.sample_name == self.sample_receiver_name

    def sample_receiver_name_color(self):
        return format_html(
            '<h5 >{}_{}</h5>',
            self.sample_receiver_name,
            self.color_code2)

    def __str__(self):
        return format_html(
            '<h5 >{}{}</h5>',
            self.sample_number,
            self.color_code)

    class Meta:
        verbose_name = "样品池管理"
        verbose_name_plural = "样品池管理"
