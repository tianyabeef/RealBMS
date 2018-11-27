from django.contrib.auth.models import User
from django.db import models
from pm.models import ExtSubmit, LibSubmit, SeqSubmit



#提取方法
class Extmethod(models.Model):
    mothod = models.CharField(verbose_name="提取方法",max_length=100)

    def __str__(self):
        return self.mothod
    class Meta:
        ordering = ['id']
        verbose_name = '提取方法'
        verbose_name_plural = '提取方法'
#质检方法
class Testmethod(models.Model):
    mothod = models.CharField(verbose_name="质检方法", max_length=100)

    def __str__(self):
        return self.mothod
    class Meta:
        ordering = ['id']
        verbose_name = '质检方法'
        verbose_name_plural = '质检方法'

#抽提执行


class ExtExecute(models.Model):
    extSubmit = models.OneToOneField(
        ExtSubmit,
        verbose_name='子项目编号(抽提)',
        on_delete=models.CASCADE,blank= True,null=True
    )
    ext_experimenter = models.ManyToManyField(
        User,
        verbose_name='抽提实验员',
        # on_delete= models.DO_NOTHING,
    )
    extract_method = models.ForeignKey(Extmethod,verbose_name="提取方法",on_delete=models.CASCADE,null=True)
    test_method = models.ForeignKey(Testmethod,verbose_name="质检方法",on_delete=models.CASCADE,null=True)
    ext_end_date = models.DateField('提取完成日期',blank=True,null=True)
    note = models.TextField('实验结果备注',blank=True,null=True)
    upload_file = models.FileField('抽提结果报告', upload_to='uploads/ext/%Y/%m/%d/', blank=True, null=True)
    is_submit = models.BooleanField('提交',default=False)
    query_code = models.CharField("查询码",max_length=50,blank=True,null=True)
    # def save(self, *args, **kwargs):
    #     super(ExtSubmit, self).save(*args, **kwargs)
    #     if not self.slug:
    #         self.slug = "提取任务 #" + str(self.id)
    #         self.save()
    class Meta:
        verbose_name = '1提取任务执行'
        verbose_name_plural = verbose_name

    def __str__(self):
        return '%s' % self.extSubmit


#建库执行
class LibExecute(models.Model):

    libSubmit = models.OneToOneField(
        LibSubmit,
        verbose_name='子项目编号(建库)',
        on_delete=models.CASCADE,blank= True,null=True
    )
    lib_experimenter = models.ManyToManyField(
        User,
        # on_delete= models.DO_NOTHING,
        verbose_name='建库实验员',

    )
    lib_end_date = models.DateField('建库完成日期',blank=True,null=True)
    note = models.TextField('实验结果备注',blank=True,null=True)
    query_code = models.CharField("查询码", max_length=50, blank=True, null=True)
    #非必填
    reaction_times = models.IntegerField(verbose_name="反应次数（选填）",blank=True,null=True)
    pcr_system = models.CharField(verbose_name="PCR体系（选填）",max_length=200,blank=True,null=True)
    dna_polymerase = models.CharField(verbose_name="DNA聚合酶（选填）",max_length=50,blank=True,null=True)
    model_initiation_mass = models.CharField(verbose_name="模板起始量（选填）",max_length=50,blank=True,null=True)
    enzyme_number = models.CharField(verbose_name="酶批号（选填）",max_length=50,blank=True,null=True)
    pcr_process = models.IntegerField(choices=((0,"KAPA酶程序"),(1,"唯赞酶程序"),(2,"降落PCR程序"),(3,"其它程序（见备注）")),blank=True,null=True)
    annealing_temperature = models.CharField(verbose_name="退货问题（选填）",max_length=50,blank=True,null=True)
    loop_number = models.IntegerField(verbose_name="循环数",blank=True,null=True)
    gel_recovery_kit = models.CharField(verbose_name="胶回收试剂盒（选填）",max_length=200,blank=True,null=True)
    upload_file = models.FileField('建库结果报告', upload_to='uploads/lib/%Y/%m/%d/', blank=True, null=True)
    is_submit = models.BooleanField('提交', default=False)
    # def save(self, *args, **kwargs):
    #     super(LibSubmit, self).save(*args, **kwargs)
    #     if not self.slug:
    #         self.slug = "建库任务 #" + str(self.id)
    #         self.save()

    class Meta:
        verbose_name = '2建库任务执行'
        verbose_name_plural = verbose_name

    def __str__(self):
        return '%s' % self.libSubmit


#测序执行
class SeqExecute(models.Model):
    seqSubmit = models.OneToOneField(
        SeqSubmit,
        verbose_name='子项目编号(测序)',
        on_delete=models.CASCADE,blank=True,null=True
    )
    # subproject = models.ForeignKey()
    seq_experimenter = models.ManyToManyField(
        User,
        verbose_name='测序实验员',
        # on_delete= models.DO_NOTHING,
    )
    query_code = models.CharField("查询码", max_length=50, blank=True, null=True)
    seq_end_date = models.DateField('测序下机日期',blank=True,null=True)
    upload_file = models.FileField('测序结果报告上传', upload_to='uploads/seq/%Y/%m/%d/',blank=True,null=True)
    note = models.TextField('实验结果备注',blank=True,null=True)
    is_submit = models.BooleanField('提交',default=False)

    # def save(self, *args, **kwargs):
    #     super(SeqSubmit, self).save(*args, **kwargs)
    #     if not self.slug:
    #         self.slug = "测序任务 #" + str(self.id)
    #         self.save()

    class Meta:
        verbose_name = '3测序任务执行'
        verbose_name_plural = verbose_name

    def __str__(self):
        return '%s' % self.seqSubmit




# # 分析提交
# class AnaExecute(models.Model):
#     contract = models.ForeignKey(
#         'mm.Contract',
#         verbose_name='合同号',
#         on_delete=models.CASCADE,
#     )#里面包含合同编号，合同名称
#     ana_experimenter =  models.ForeignKey(
#         User,
#         verbose_name='分析员',blank= True,null=True
#     )
#     ana_end_date = models.DateField('分析完成日期')
#     upload_file = models.FileField('分析结果报告', upload_to='uploads/%Y/%m/%d/')
#     note = models.TextField('实验结果备注')
#     is_submit = models.BooleanField('提交')

    # def save(self, *args, **kwargs):
    #     super(AnaSubmit, self).save(*args, **kwargs)
    #     if not self.slug:
    #         self.slug = "分析任务 #" + str(self.id)
    # #         self.save()
    #
    # class Meta:
    #     verbose_name = '4分析任务执行'
    #     verbose_name_plural = verbose_name
    #
    # def __str__(self):
    #     return '%s' % self.contract


#样品
class SampleInfoExt(models.Model):

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

    Quality_control_conclusion = (
        (1, 'A'),
        (2, 'B'),
        (3, 'C'),
        (4, 'D'),
    )

    Type_of_Sample = (
        (1, 'g DNA'),
        (2, '组织'),
        (3, '细胞'),
        (4, '土壤'),
        (5, '粪便其他未提取（请描述）'),
    )

    Rebulid = (
        (0, '不重抽提'),
        (1, '重抽提'),
    )
    #外键
    extExecute = models.ForeignKey(
        "lims.ExtExecute",
        verbose_name="子项目(抽提)",
        on_delete=models.CASCADE,
        blank = True, null = True
    )
    #以下5个字段从SampleInfo表中获得
    # samples =
    unique_code = models.CharField(max_length=60,verbose_name="对应样品池唯一编号")
    sample_number = models.CharField(max_length=50,verbose_name="样品编号")
    sample_name = models.CharField(max_length=50,verbose_name="样品名称")##就是样品编号
    # preservation_medium = models.IntegerField(choices=Preservation_medium,verbose_name="样品保存介质",default=1)
    # is_RNase_processing = models.IntegerField(choices=Is_RNase_processing,verbose_name="是否经过RNase处理",default=1)
    species = models.CharField(max_length=200,verbose_name="物种")
    sample_type = models.IntegerField(choices=Type_of_Sample,verbose_name="样品类型",default=1)
    ##以下字段为抽提的的结果
    sample_used = models.CharField(max_length=200,verbose_name="样品提取用量",blank=True,null=True)
    sample_rest = models.CharField(max_length=200,verbose_name="样品剩余用量",blank=True,null=True)
    density_checked = models.DecimalField('浓度ng/uL(公司检测)', max_digits=5, decimal_places=3,blank=True,null=True)
    volume_checked = models.DecimalField('体积uL(公司检测)', max_digits=5, decimal_places=3,blank=True,null=True)
    D260_280 = models.DecimalField(max_digits=8,decimal_places=1,verbose_name="D260/280",blank=True,null=True)
    D260_230 = models.DecimalField(max_digits=8,decimal_places=1,verbose_name="D260/230",blank=True,null=True)
    DNA_totel = models.CharField(max_length=200,verbose_name="DNA总量",blank=True,null=True)
    note = models.TextField('备注', blank=True, null=True)
    quality_control_conclusion = models.IntegerField(choices=Quality_control_conclusion,verbose_name="质检结论",default=1)##ABC
    is_rebuild = models.IntegerField(choices=Rebulid,verbose_name="选择是否重抽提",default=0)
    def __str__(self):
        return str(self.sample_number)

    def type_sample(self):
        return self.Type_of_Sample[self.sample_type - 1][1]

    def rebuild(self):
        return self.Rebulid[self.is_rebuild][1]

    def quality(self):
        return self.Quality_control_conclusion[self.quality_control_conclusion - 1][1]

    class Meta:
        verbose_name = "样品池---抽提"
        verbose_name_plural = "样品池---抽提"


class SampleInfoLib(models.Model):
    Lib_result = (
        (1, '合格'),
        (2, '不合格'),
    )
    # 外键
    libExecute = models.ForeignKey(
        "lims.LibExecute",
        verbose_name="子项目(建库)",
        on_delete=models.CASCADE,
        blank = True, null = True
    )
    Rebulid = (
        (0, '不重建库'),
        (1, '重建库'),
    )
    ##以下两个字段重SampleInfo表中获得
    unique_code = models.CharField(max_length=60, verbose_name="对应样品池唯一编号")
    sample_number = models.CharField(max_length=50,verbose_name="样品编号")
    sample_name = models.CharField(max_length=50,verbose_name="样品名称")##就是样品编号
    ##以下质控结果
    lib_code = models.CharField('文库号', max_length=20,blank=True,null=True)##需要项目管理填写
    index = models.CharField('Index', max_length=20,blank=True,null=True)##需要项目管理填写
    lib_volume = models.DecimalField('体积uL(文库)', max_digits=5, decimal_places=3,blank=True,null=True)
    lib_concentration = models.DecimalField('浓度ng/uL(文库)', max_digits=5, decimal_places=3,blank=True,null=True)
    lib_total = models.DecimalField('总量ng(文库)', max_digits=5, decimal_places=3,blank=True,null=True)
    lib_result = models.IntegerField(choices=Lib_result,verbose_name='结论(文库)',default=1)
    lib_note = models.TextField('备注(文库)', blank=True, null=True)
    is_rebuild = models.IntegerField(choices=Rebulid, verbose_name="选择是否重建库", default=0)
    def __str__(self):
        return str(self.sample_number)

    class Meta:
        verbose_name = "样品池---建库"
        verbose_name_plural = "样品池---建库"

    def result(self):
        return self.Lib_result[self.lib_result - 1][1]
    def rebuild(self):
        return self.Rebulid[self.is_rebuild][1]

class SampleInfoSeq(models.Model):
    Seq_result = (
        (1, '合格'),
        (2, '不合格'),
    )
    #外键
    seqExecute = models.ForeignKey(
        "lims.SeqExecute",
        verbose_name="子项目(测序)",
        on_delete=models.CASCADE,
        blank=True, null=True
    )
    Rebulid = (
        (0, '不重测序'),
        (1, '重测序'),
    )

    ##以下两个字段重SampleInfo表中获得
    unique_code = models.CharField(max_length=60, verbose_name="对应样品池唯一编号")
    sample_number = models.CharField(max_length=50,verbose_name="样品编号")
    sample_name = models.CharField(max_length=50,verbose_name="样品名称")##就是样品编号
    ##以下质控结果
    seq_code = models.CharField('文库号', max_length=20,blank=True,null=True)##需要项目管理填写
    seq_index = models.CharField('Index', max_length=20,blank=True,null=True)##需要项目管理填写
    data_request = models.CharField(max_length=200,verbose_name="数据量要求",blank=True,null=True)
    seq_data = models.CharField(max_length=200,verbose_name="测序数据量",blank=True,null=True)
    seq_result = models.IntegerField(choices=Seq_result,verbose_name='结论(测序)',default=1)
    seq_note = models.TextField('备注(测序)', blank=True, null=True)
    is_rebuild = models.IntegerField(choices=Rebulid, verbose_name="选择是否重测序", default=0)
    def __str__(self):
        return str(self.sample_number)

    class Meta:
        verbose_name = "样品池---测序"
        verbose_name_plural = "样品池---测序"

    def result(self):
        return self.Seq_result[self.seq_result-1][1]

    def rebuild(self):
        return self.Rebulid[self.is_rebuild][1]
