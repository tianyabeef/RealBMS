from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal
from django.contrib import admin
from django.utils.html import format_html


# 项目
class SubProject(models.Model):
    STATUS_CHOICES = (
        (0, '不能启动'),  # CNS(Could not started)
        (2, '正常启动'),  # NS(normal start)
        (1, '提前启动'),  # ES(Early start)
        (3, '立项处理'),  # PA(Project approval)
        (4, '待首款'),  # 'FIS'
        # (5, '待处理'),  # 'ENS'
        (5, '提取中'),  # 'EXT'
        # (7, '质检中'),  # 'QC'
        (6, '建库中'),  # 'LIB'
        (7, '测序中'),  # 'SEQ'
        (8, '分析中'),  # 'ANA'
        (9, '待尾款'),  # 'FIN'
        (10, '尾款已到'),  # 'FINE'
        (11, '完成'),  # 'END'
    )
    contract = models.ForeignKey(
        'mm.Contract',
        verbose_name='合同号',
        null=True,
        on_delete=models.SET_NULL,
    )
    # customer = models.ForeignKey(
    #     'crm.Customer',
    #     verbose_name='客户姓名',
    #     null=True,
    #     on_delete=models.SET_NULL,
    # )
    # project_personnel = models.ForeignKey(
    #     User,
    #     verbose_name='项目人员',
    #     null=True,
    #     on_delete=models.SET_NULL,
    # )
    project_personnel = models.CharField('项目管理人员', max_length=40)

    sample_types = models.ForeignKey(
        'sample.SampleInfoForm',
        verbose_name='样品类型',
        null=True,
        on_delete=models.SET_NULL,
    )
    # sample_types = models.ManyToManyField(
    #     'sample.SampleInfoForm',
    #     verbose_name='样品类型',
    #
    # )
    # # sample_type = models.CharField('样本类型', max_length=50)
    # sample_count = models.ForeignKey(
    #     'sample.SampleInfoForm',
    #     verbose_name='样品数量',
    #     null=True,
    #     on_delete=models.SET_NULL,
    # )
    # sample_count = models.IntegerField('样品数量', )
    # customer = models.CharField('客户', max_length=20, blank=True)
    # customer_phone = models.CharField('电话', max_length=30, blank=True)
    # saleman = models.CharField('销售人员', max_length=40)
    # income_notes = models.CharField('到款记录', max_length=20)
    # sample_customer = models.CharField('样品联系人姓名', max_length=40)
    # sample_customer_phone = models.CharField('样品联系人电话', max_length=11)
    # company = models.CharField('地址', max_length=100)
    sub_number = models.CharField('子项目编号', max_length=100)
    sub_project = models.CharField('子项目的名称', max_length=40)
    project_start_time = models.DateField('立项时间', max_length=20)
    receive_date = models.DateField('收到样品日期')
    name = models.TextField('项目注解', max_length=100, blank=True)
    # IS_CHOICE =(
    #     (1, "需提取"),
    #     (2,"需建库"),
    #     (3, "需测序"),
    #     (4, "需分析"),
    #
    # )
    is_ext = models.BooleanField('需提取')
    # is_qc = models.BooleanField('需质检')
    is_lib = models.BooleanField('需建库')
    is_seq = models.BooleanField("需测序")
    is_ana = models.BooleanField("需分析")
    # service_type = models.IntegerField(verbose_name='服务类型',
    #                                    choices=(('is_ext', '需测序'), ('is_lib', '需建库'), ('is_seq', '需测序'),
    #                                             ('is_ana', '需分析'),), default='is_ext')
    # service_type = models.CharField('服务类型', max_length=50)
    data_amount = models.CharField('数据要求', max_length=10)
    pic = models.ImageField('提前启动图片', upload_to='pm/', null=True, blank=True)

    # ext_cycle = models.PositiveIntegerField('提取周期')
    # ext_task_cycle = models.PositiveIntegerField('提取周期')
    # ext_date = models.DateField('提取完成日', blank=True, null=True)
    # qc_cycle = models.PositiveIntegerField('质检周期')
    # qc_task_cycle = models.PositiveIntegerField('质检周期')
    # qc_date = models.DateField('质检完成日', blank=True, null=True)
    # lib_cycle = models.PositiveIntegerField('建库周期')
    # lib_task_cycle = models.PositiveIntegerField('建库周期')
    # lib_date = models.DateField('建库完成日', blank=True, null=True)
    # seq_cycle = models.PositiveIntegerField('测序周期')
    # seq_start_date = models.DateField('测序开始日', blank=True, null=True)
    # seq_end_date = models.DateField('测序完成日', blank=True, null=True)
    # ana_cycle = models.PositiveIntegerField('分析周期')
    # ana_start_date = models.DateField('分析开始日', blank=True, null=True)
    # ana_end_date = models.DateField('分析完成日', blank=True, null=True)
    report_date = models.DateField('释放报告日', blank=True, null=True)
    result_date = models.DateField('释放结果日', blank=True, null=True)
    data_date = models.DateField('释放数据日', blank=True, null=True)
    due_date = models.DateField('合同节点', blank=True, null=True)
    is_confirm = models.BooleanField('确认', default=False)
    # status = models.IntegerField('状态', max_length=3, choices=STATUS_CHOICES, default=1)
    status = models.IntegerField('状态', choices=STATUS_CHOICES, default=0)
    # save_statuss = models.CharField(max_length=6)
    #
    # def colored_name(self):
    #     return format_html(
    #         '<span style="color: #{};">{} {}</span>',
    #         self.save_statuss,
    #     )
    # save_status = models.CharField(choices=((0,u'不能'),(1,u'提前'),(2,u'正常')),default=1,max_length=3,verbose_name=u'启动状态')

    # def save_status(self,):
    #     if self.contract.fin_amount_in >= (self.contract.all_amount*Decimal(0.7)):
    #         self.status = '2'
    #     elif (self.contract.fis_amount_in > 0) and self.contract.fis_amount_in < (self.contract.all_amount*Decimal(0.7)):
    #
    #         self.status = '1'
    #     else:
    #         self.status = '0'
    #     self.save()
    # save_status.short_description = '启动状态2'

    class Meta:
        unique_together = ('contract', 'name')
        verbose_name = '0项目管理'
        verbose_name_plural = '0项目管理'

    def __str__(self):
        return '%s' % self.sub_number


# class ProjectAdmin(admin.ModelAdmin):
#     list_display = ('colored_name',)


# 提取
class ExtSubmit(models.Model):
    # is_exts = models.ForeignKey('Project', verbose_name="提取的信息集", null=True,on_delete=models.SET_NULL,)
    ext_cycle = models.PositiveIntegerField('项目提取周期')
    ext_date = models.DateField('提取完成日', blank=True, null=True)
    ext_man = models.ForeignKey(
        User,
        verbose_name='提取实验员',
        null=True,
        on_delete=models.SET_NULL,
    )
    ext_slug = models.ForeignKey(
        'SubProject',
        verbose_name='提取子项目编号',
        null=True,
        on_delete=models.SET_NULL,
    )
    slug = models.SlugField('提取任务号', allow_unicode=True)

    sample = models.ManyToManyField(
        'sample.SampleInfo',
        verbose_name='样品',
    )
    date = models.DateField('提交时间', blank=True, null=True)
    is_submit = models.BooleanField('提交')

    def save(self, *args, **kwargs):
        super(ExtSubmit, self).save(*args, **kwargs)
        if not self.slug:
            self.slug = "提取任务 #" + str(self.id)
            self.save()

    class Meta:
        verbose_name = '1提取任务下单'
        verbose_name_plural = '1提取任务下单'

    def __str__(self):
        return '%s' % self.slug


# class QcSubmit(models.Model):
#     slug = models.SlugField('任务号', allow_unicode=True)
#     sample = models.ManyToManyField(
#         'lims.SampleInfo',
#         verbose_name='样品',
#     )
#     date = models.DateField('提交时间', blank=True, null=True)
#     is_submit = models.BooleanField('提交')
#
#     def save(self, *args, **kwargs):
#         super(QcSubmit, self).save(*args, **kwargs)
#         if not self.slug:
#             self.slug = "质检任务 #" + str(self.id)
#             self.save()
#
#     class Meta:
#         verbose_name = '2质检任务下单'
#         verbose_name_plural = '2质检任务下单'
#
#     def __str__(self):
#         return '%s' % self.slug


# 建库
class LibSubmit(models.Model):
    lib_cycle = models.PositiveIntegerField('项目建库周期')
    lib_date = models.DateField('建库完成日', blank=True, null=True)
    lib_man = models.ForeignKey(
        User,
        verbose_name='建库实验员',
        null=True,
        on_delete=models.SET_NULL,
    )
    lib_slug = models.ForeignKey(
        'SubProject',
        verbose_name='建库子项目编号',
        null=True,
        on_delete=models.SET_NULL,
    )
    slug = models.SlugField('任务号', allow_unicode=True)
    sample = models.ManyToManyField(
        'sample.SampleInfo',
        verbose_name='样品'
    )
    date = models.DateField('提交时间', blank=True, null=True)
    is_submit = models.BooleanField('提交')

    def save(self, *args, **kwargs):
        super(LibSubmit, self).save(*args, **kwargs)
        if not self.slug:
            self.slug = "建库任务 #" + str(self.id)
            self.save()

    class Meta:
        verbose_name = '3建库任务下单'
        verbose_name_plural = '3建库任务下单'

    def __str__(self):
        return '%s' % self.slug


# 测序
class SeqSubmit(models.Model):
    seq_cycle = models.PositiveIntegerField('项目测序周期')
    seq_start_date = models.DateField('测序开始日', blank=True, null=True)
    seq_end_date = models.DateField('测序完成日', blank=True, null=True)
    seq_man = models.ForeignKey(
        User,
        verbose_name='测序实验员',
        null=True,
        on_delete=models.SET_NULL,
    )
    seq_slug = models.ForeignKey(
        'SubProject',
        verbose_name='测序子项目编号',
        null=True,
        on_delete=models.SET_NULL,
    )
    slug = models.SlugField('任务号', allow_unicode=True)
    sample = models.ManyToManyField(
        'sample.SampleInfo',
        verbose_name='样品'
    )
    date = models.DateField('提交时间', blank=True, null=True)
    is_submit = models.BooleanField('提交')

    def save(self, *args, **kwargs):
        super(SeqSubmit, self).save(*args, **kwargs)
        if not self.slug:
            self.slug = "测序任务 #" + str(self.id)
            self.save()

    class Meta:
        verbose_name = '4测序任务下单'
        verbose_name_plural = '4测序任务下单'

    def __str__(self):
        return '%s' % self.slug


# 分析
class AnaSubmit(models.Model):
    ana_cycle = models.PositiveIntegerField('项目分析周期')
    ana_start_date = models.DateField('分析开始日', blank=True, null=True)
    ana_end_date = models.DateField('分析完成日', blank=True, null=True)
    ana_man = models.ForeignKey(
        User,
        verbose_name='分析实验员',
        null=True,
        on_delete=models.SET_NULL,
    )
    ana_slug = models.ForeignKey(
        'mm.Contract',
        verbose_name='分析子项目编号',
        null=True,
        on_delete=models.SET_NULL,
    )
    slug = models.SlugField('任务号', allow_unicode=True)
    sample = models.ManyToManyField(
        'sample.SampleInfo',
        verbose_name='样品'
    )
    date = models.DateField('提交时间', blank=True, null=True)
    is_submit = models.BooleanField('提交')

    def save(self, *args, **kwargs):
        super(AnaSubmit, self).save(*args, **kwargs)
        if not self.slug:
            self.slug = "分析任务 #" + str(self.id)
            self.save()

    class Meta:
        verbose_name = '5分析任务下单'
        verbose_name_plural = '5分析任务下单'

    def __str__(self):
        return '%s' % self.slug
