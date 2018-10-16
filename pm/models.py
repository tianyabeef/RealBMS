from django.db import models
from django.contrib.auth.models import User


# 项目


class SubProject(models.Model):
    STATUS_CHOICES = (
        (0, '不能启动'),  # CNS(Could not started)
        (1, '正常启动'),  # NS(normal start)
        (2, '提前启动'),  # ES(Early start)
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
        on_delete=models.CASCADE,
    )
    customer = models.CharField('客户', max_length=20, blank=True)
    customer_phone = models.CharField('电话', max_length=30, blank=True)
    saleman = models.ForeignKey(User,related_name="销售代表",verbose_name="销售代表",blank=True,null=True,on_delete=models.SET_NULL)
    income_notes = models.CharField('到款记录', max_length=20,blank=True,default='')
    sample_customer = models.ForeignKey(User,related_name="样品联系人姓名",verbose_name="销售代表",blank=True,null=True,on_delete=models.SET_NULL)
    sample_customer_phone = models.CharField('样品联系人电话', max_length=11,blank=True,default='')

    company = models.CharField('地址', max_length=100, blank=True,default='')
    sub_number = models.CharField('子项目编号', max_length=100,blank=True,default='')
    sub_project = models.CharField('子项目的名称', max_length=40,blank=True,default='')
    project_start_time = models.DateField('立项时间', max_length=20,blank=True,default=None)
    receive_date = models.DateField('收到样品日期',blank=True,default=None)
    sample_type = models.CharField('样本类型', max_length=50,blank=True,default='')
    sample_count = models.IntegerField('样品数量',blank=True,default=0)
    name = models.TextField('项目注解', max_length=100, blank=True)
    is_ext = models.BooleanField('需提取',blank=True,default=False)
    # is_qc = models.BooleanField('需质检')
    is_lib = models.BooleanField('需建库',blank=True,default=False)
    is_seq = models.BooleanField("需测序",blank=True,default=False)
    is_ana = models.BooleanField("需分析",blank=True,default=False)
    project_personnel = models.CharField('项目管理人员', max_length=40,blank=True,default='')
    service_type = models.CharField('服务类型', max_length=50,blank=True,default='')
    data_amount = models.CharField('数据要求', max_length=10,blank=True,default='')

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
    status = models.IntegerField('状态', choices=STATUS_CHOICES, default=1)

    class Meta:
        unique_together = ('contract', 'name')
        verbose_name = '0项目管理'
        verbose_name_plural = '0项目管理'

    def __str__(self):
        return '%s' % self.name


# 提取
class ExtSubmit(models.Model):
    ext_cycle = models.PositiveIntegerField('项目提取周期',blank=True, null=True)
    ext_date = models.DateField('提取完成日', blank=True, null=True)
    slug = models.SlugField('提取任务号', blank=True, null=True,allow_unicode=True)

    sample = models.ManyToManyField(
        'teacher.SampleInfo',
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
    lib_cycle = models.PositiveIntegerField('项目建库周期', blank=True, null=True)
    lib_date = models.DateField('建库完成日', blank=True, null=True)
    slug = models.SlugField('任务号', allow_unicode=True, blank=True, null=True)
    sample = models.ManyToManyField(
        'teacher.SampleInfo',
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
    seq_cycle = models.PositiveIntegerField('项目测序周期', blank=True, null=True)
    seq_start_date = models.DateField('测序开始日', blank=True, null=True)
    seq_end_date = models.DateField('测序完成日', blank=True, null=True)
    slug = models.SlugField('任务号', allow_unicode=True, blank=True, null=True)
    sample = models.ManyToManyField(
        'teacher.SampleInfo',
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
    slug = models.SlugField('任务号', allow_unicode=True)
    sample = models.ManyToManyField(
        'teacher.SampleInfo',
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
