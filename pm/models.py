from django.db import models
from django.contrib.auth.models import User


class SubProject(models.Model):
    # 项目选项
    STATUS_CHOICES = (
        (1, '已立项'),  # QC(Quality Control)
        (2, '待抽提'),  # SE(Stay extraction)#项目管理在抽提任务下单表中把每一个子项目的样品都添加好，并提交。
        (3, '抽提中'),  # EXT(Extraction)    #实验管理添加了实验员之后，并通过钉钉通知了实验员
        (4, '抽提完成：待客户反馈建库'),  # WFCFTD(Wait for customer feedback to build the database) #实验管理导入了样品的抽提结果，并提交
        (5, '待建库'),  # TBL(To build libraries)#项目管理在建库任务下单表中把每一个子项目的样品都添加好，并提交。
        (6, '建库中'),  # LIB(libraries) #实验管理添加了建库实验员之后，并通过钉钉通知了实验员
        (7, '建库完成：待客户反馈测序'),  # WFCFS(Waiting for customer feedback sequencing)#实验管理导入了样品的建库结果，并提交
        (8, '待测序'),  # TBS(To build sequencing)#项目管理在测序任务下单表中把每一个子项目的样品都添加好，并提交。
        (9, '测序中'),  # SEQ(sequencing)#实验管理添加了实验员之后，并通过钉钉通知了实验员
        (10, '测序完成：待客户反馈分析'),  # WFCFA(Waiting for Customer feedback analysis)#项目管理把测序的结果导入到样品表中
        (11, '待分析'),  # TBA(To build analysis)#项目管理新建一个分析项目
        (12, '分析中'),  # ANA(analysis)#生信管理添加了分析员
        (13, "完成"),
        (14, "中止"),
    )
    contract = models.ForeignKey('mm.Contract', verbose_name='合同号', on_delete=models.SET_NULL, null=True)
    sampleInfoForm = models.ForeignKey('sample.SampleInfoForm', verbose_name='样品概要表',
                                       on_delete=models.SET_NULL, null=True)
    project_manager = models.OneToOneField(User, verbose_name="项目管理员", on_delete=models.SET_NULL, null=True)
    # 里面包含合同编号，合同名称
    # contract_name = models.CharField('合同名称', max_length=40)
    # customer = models.CharField('合同联系人姓名', max_length=40)
    # customer_phone = models.CharField('合同联系人电话', max_length=11)
    # saleman = models.CharField('销售人员', max_length=40)
    # company = models.CharField('合作伙伴单位', max_length=100)
    # project_type = models.IntegerField(choices=Project_choices, verbose_name="项目类型", default=1)
    # 发票里有
    # income_notes = models.CharField('到款记录', max_length=20)
    # invoice = models.OneToOneField(
    #     'fm.Invoice',
    #     verbose_name='发票',on_delete=models.SET_NULL,null=True
    # )##里面包含了全部的发票到账情况
    # 概要表里有里
    # sample_receiver = models.CharField('样品接收人姓名', max_length=40)
    # receive_date = models.DateField('样品接收时间')
    # 项目信息
    sub_number = models.CharField('子项目编号', max_length=100)
    sub_project = models.CharField('子项目的名称', max_length=40)
    project_start_time = models.DateField('立项时间', auto_now=True)
    is_ext = models.BooleanField('需抽提')
    is_lib = models.BooleanField('需建库')
    is_seq = models.BooleanField("需测序")
    is_ana = models.BooleanField("需分析")
    sub_project_note = models.TextField('备注', blank=True)
    is_submit = models.BooleanField('确认', default=False)
    status = models.BooleanField('项目是否提前启动', default=False)
    sample_count = models.IntegerField('样品数量')
    # data_amount = models.CharField('数据量要求', max_length=10)
    file_to_start = models.FileField('提前启动文件', upload_to='pm/', null=True, blank=True)
    is_status = models.IntegerField('状态', choices=STATUS_CHOICES, default=1)
    # 流程时间节点
    time_ext = models.DateField("抽提完成时间", null=True,)
    time_lib = models.DateField("建库完成时间", null=True,)
    time_ana = models.DateField("分析完成时间", null=True,)

    class Meta:
        unique_together = ('sub_number',)
        verbose_name = '0立项管理'
        verbose_name_plural = verbose_name

    def __str__(self):
            return '%s' % self.sub_number


# 抽提提交
class ExtSubmit(models.Model):
    subProject = models.ForeignKey('SubProject', verbose_name='子项目(抽提)', on_delete=models.SET_NULL, null=True)
    sample = models.ManyToManyField("sample.SampleInfo", verbose_name="选择抽提样品", blank=True,)
    ext_number = models.CharField('抽提号', max_length=100)
    ext_start_date = models.DateField("提取开始日期", auto_now=True)
    sample_count = models.IntegerField('样品数量', blank=True, null=True)
    # ext_result = models.FileField('抽提结果')外键一张抽提样品表
    note = models.TextField('实验任务备注', blank=True, null=True)
    is_submit = models.BooleanField('提交', default=False)
    # def save(self, *args, **kwargs):
    #     super(ExtSubmit, self).save(*args, **kwargs)
    #     if not self.slug:
    #         self.slug = "提取任务 #" + str(self.id)
    #         self.save()

    class Meta:
        verbose_name = '1提取任务下单'
        verbose_name_plural = verbose_name

    def __str__(self):
        return '%s' % self.ext_number


# 建库提交
class LibSubmit(models.Model):
    subProject = models.ForeignKey('SubProject', verbose_name='子项目(建库)', on_delete=models.SET_NULL, null=True)
    sample = models.ManyToManyField("sample.SampleInfo", verbose_name="选择建库样品", blank=True,)
    lib_number = models.CharField('建库号', max_length=100)
    lib_start_date = models.DateField("建库开始日期", auto_now=True)
    customer_confirmation_time = models.DateField('客户确认时间', blank=True, null=True)
    customer_sample_count = models.IntegerField('客户确认样品数量', blank=True, null=True)
    # 加文库类型、测序类型、建库类型

    # lib_info = models.FileField('建库样品明细')外键一张建库样品表
    note = models.TextField('备注', blank=True, null=True)
    is_submit = models.BooleanField('提交', default=False)
    # def save(self, *args, **kwargs):
    #     super(LibSubmit, self).save(*args, **kwargs)
    #     if not self.slug:
    #         self.slug = "建库任务 #" + str(self.id)
    #         self.save()

    class Meta:
        verbose_name = '2建库任务下单'
        verbose_name_plural = verbose_name

    def __str__(self):
        return '%s' % self.lib_number


# 测序提交
class SeqSubmit(models.Model):
    subProject = models.ForeignKey('SubProject', verbose_name='子项目编号', on_delete=models.SET_NULL, null=True)
    sample = models.ManyToManyField("sample.SampleInfo", verbose_name="选择测序样品", blank=True,)
    seq_number = models.CharField('测序号', max_length=100)
    seq_start_date = models.DateField('测序上机日期', auto_now=True)
    customer_confirmation_time = models.DateField('客户确认上机时间', blank=True, null=True)
    customer_sample_count = models.IntegerField('客户确认上机样品数量', blank=True, null=True)
    # customer_sample_info = models.FileField('客上机样本明细')
    pooling_excel = models.FileField(verbose_name="Pooling表格", upload_to="uploads/pooling/%Y/%m/%d/", blank=True)
    # 外键一张测序样品表
    note = models.TextField('备注', blank=True, null=True)
    is_submit = models.BooleanField('提交', default=False)

    # def save(self, *args, **kwargs):
    #     super(SeqSubmit, self).save(*args, **kwargs)
    #     if not self.sub_number:
    #         self.sub_number = "测序任务 #" + str(self.id)
    #         self.save()

    class Meta:
        verbose_name = '3测序任务下单'
        verbose_name_plural = verbose_name

    def __str__(self):
        return '%s' % self.seq_number


# 分析提交
class AnaSubmit(models.Model):
    # contract = models.ForeignKey(
    #     'mm.Contract',
    #     verbose_name='合同号',
    #     on_delete=models.SET_NULL, null=True
    # )
    subProject = models.ManyToManyField('SubProject', verbose_name='子项目编号', blank=True,)
    # 里面包含合同编号，合同名称
    ana_number = models.CharField('分析号', max_length=100)
    # invoice_code = models.CharField('发票号码', max_length=12, unique=True)
    ana_start_date = models.DateField('分析开始日期', auto_now=True)
    note = models.TextField('备注')
    sample_count = models.IntegerField('样品数量')
    is_submit = models.BooleanField('提交')
    depart_data_path = models.CharField(verbose_name="数据拆分路径", max_length=50)
    data_analysis = models.FileField(verbose_name="数据分析单", upload_to="uploads/ana/%Y/%m/%d/", blank=True)

    # def save(self, *args, **kwargs):
    #     super(AnaSubmit, self).save(*args, **kwargs)
    #     if not self.slug:
    #         self.slug = "分析任务 #" + str(self.id)
    #         self.save()

    class Meta:
        verbose_name = '4分析任务下单'
        verbose_name_plural = verbose_name

    def __str__(self):
        return '%s' % self.ana_number
