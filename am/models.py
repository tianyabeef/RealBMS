from django.contrib.auth.models import User
from django.db import models

from mm.models import Contract
from pm.models import AnaSubmit


class AnaExecute(models.Model):
    """执行生信分析步骤"""
    ana_submit = models.OneToOneField(
        AnaSubmit, verbose_name="子项目编号（分析）", on_delete=models.CASCADE
    )
    analyst = models.ForeignKey(
        User, verbose_name="生信分析员", on_delete=models.SET_NULL, null=True
    )
    submit_date = models.DateField(
        verbose_name="分析提交日期", auto_now_add=True
    )
    end_date = models.DateField(
        verbose_name="实际结束日期", blank=True, null=True
    )
    baidu_link = models.CharField(
        verbose_name="结果百度链接", max_length=512, blank=True, null=True
    )
    notes = models.TextField(
        verbose_name="备注", null=True, blank=True
    )
    is_submit = models.BooleanField(
        verbose_name="是否提交", default=False,
    )

    class Meta:
        verbose_name_plural = verbose_name = '4分析任务执行'

    def __str__(self):
        return '%s' % self.ana_submit.ana_number


class WeeklyReport(models.Model):
    """
    科技服务生信部门的周报管理
    """
    reporter = models.ForeignKey(
        User, verbose_name="汇报人", on_delete=models.CASCADE
    )
    submit_date = models.DateField(
        verbose_name="提交日期", auto_now_add=True
    )
    start_date = models.DateField(
        verbose_name="起始日期", null=True
    )
    end_date = models.DateField(
        verbose_name="截止日期", null=True
    )
    attachment = models.FileField(
        verbose_name="附件", null=True, blank=True,
        upload_to="uploads/weekly_report_attachment/%Y/%m/%d/"
    )
    content = models.TextField(
        verbose_name="汇报内容", null=True, blank=True
    )
    is_submit = models.BooleanField(
        verbose_name="提交状态", default=False
    )

    class Meta:
        verbose_name_plural = verbose_name = "周报"

    def __str__(self):
        return "%s的周报" % self.reporter.username


class ProjectTask(models.Model):
    """
    科技服务生信部门的项目任务管理
    """
    contract = models.CharField(
        verbose_name="合同号", unique=True, blank=True, null=True, max_length=50
    )
    product_name = models.CharField(
        verbose_name="产品名称", choices=(("扩增子", "扩增子"), ("基因组", "基因组"),
                                      ("转录组", "转录组"), ("代谢组", "代谢组"),
                                      ("单菌", "单菌"),
                                      ("扩增子+代谢组", "扩增子+代谢组"),
                                      ("宏基因组+代谢组", "宏基因组+代谢组")),
        max_length=100, blank=True, null=True
    )
    category = models.CharField(
        verbose_name="类别", choices=(("商业项目", "商业项目"),
                                    ("合作项目", "合作项目")),
        max_length=50, blank=True, null=True
    )
    type = models.CharField(
        verbose_name="项目类型", choices=(("16S", "16S"), ("ITS", "ITS"),
                                      ("细菌框架图", "细菌框架图"),
                                      ("细菌完成图", "细菌完成图"),
                                      ("真菌框架图", "真菌框架图"),
                                      ("真核有参", "真核有参"),
                                      ("真核无参", "真核无参"),
                                      ("原核有参", "原核有参"),
                                      ("原核无参", "原核无参"),
                                      ("人体宏基因组", "人体宏基因组"),
                                      ("完整版宏基因组", "完整版宏基因组"),
                                      ("16S全长", "16S全长"),
                                      ("功能基因", "功能基因"),
                                      ("非靶向", "非靶向"), ("靶向", "靶向"),
                                      ("短链脂肪酸", "短链脂肪酸"),
                                      ("胆汁酸", "胆汁酸")),
        max_length=50, blank=True, null=True
    )
    project_name = models.CharField(
        verbose_name="项目名称", max_length=100
    )
    analysis_type = models.CharField(
        verbose_name="分析类别", choices=(("首次分析", "首次分析"),
                                      ("重新分析", "重新分析"),
                                      ('售后分析', '售后分析')),
        max_length=50, blank=True, null=True
    )
    analysis_times = models.IntegerField(
        verbose_name="总分析次数", blank=True, null=True
    )
    begin_time = models.DateField(
        verbose_name="开始时间", blank=True, null=True
    )
    finish_time = models.DateField(
        verbose_name="结束时间", blank=True, null=True
    )
    is_finish = models.CharField(
        verbose_name="完成情况", choices=(("已交付", "已交付"),
                                      ("未交付", "未交付")),
        max_length=50, blank=True,null=True
    )
    comparison_scheme = models.CharField(
        verbose_name="比较方案", max_length=200, blank=True, null=True
    )
    sample_number = models.IntegerField(
        verbose_name="样品数量", blank=True, null=True
    )
    data_path = models.CharField(
        verbose_name="数据分析路径", max_length=100
    )
    pan_path = models.CharField(
        verbose_name="百度网盘路径", max_length=100, blank=True, null=True
    )
    analyst = models.ForeignKey(
        verbose_name="分析员", to=User, on_delete=models.SET_NULL,
        related_name="分析员", blank=True, null=True
    )
    review_user = models.ForeignKey(
        verbose_name="复核人员", to=User, on_delete=models.SET_NULL,
        related_name="复核人员", blank=True, null=True
    )
    after_sales = models.CharField(
        verbose_name="售后分析内容", blank=True, null=True, max_length=100
    )
    note = models.TextField(
        verbose_name="备注", blank=True, null=True
    )
    history_date = models.TextField(
        verbose_name="历史填写日期", blank=True, null=True
    )
    write_date = models.DateField(
        verbose_name="填写日期", blank=True, null=True
    )

    class Meta:
        verbose_name_plural = verbose_name = "01项目任务"

    def __str__(self):
        return "{0}的项目任务-{0}".format(self.analyst, self.contract)


class DevelopmentTask(models.Model):
    """
        科技服务生信部门的开发任务管理
    """
    product_name = models.CharField(
        verbose_name="产品名称", choices=(("扩增子", "扩增子"), ("宏基因组", "宏基因组"),
                                      ("转录组", "转录组"), ("代谢组", "代谢组"),
                                      ("单菌", "单菌"), ("集群管理", "集群管理"),
                                      ("扩增子+代谢组", "扩增子+代谢组"),
                                      ("宏基因组+代谢组", "宏基因组+代谢组"),
                                      ("系统开发", "系统开发")),
        max_length=100, blank=True, null=True
    )
    rd_tasks = models.CharField(
        verbose_name="研发任务", max_length=200, blank=True, null=True
    )
    cycle = models.CharField(
        verbose_name="周期", max_length=200, blank=True, null=True
    )
    test_path = models.CharField(
        verbose_name="测试路径", max_length=200, blank=True, null=True
    )
    finish_time = models.CharField(
        verbose_name="完成时间", max_length=200, blank=True, null=True
    )
    finish_status = models.CharField(
        verbose_name="完成情况简述", max_length=200, blank=True, null=True
    )
    note = models.TextField(
        verbose_name="备注", blank=True, null=True
    )
    is_finish = models.CharField(
        verbose_name="完成情况", choices=(("已完成", "已完成"),
                                      ("未完成", "未完成")),
        max_length=50, blank=True, null=True
    )
    writer = models.ForeignKey(
        verbose_name="填写人", to=User, on_delete=models.SET_NULL,
        blank=True, null=True
    )
    write_date = models.DateField(
        verbose_name="填写日期", blank=True, null=True
    )
    history_date = models.TextField(
        verbose_name="历史填写日期", blank=True, null=True
    )

    class Meta:
        verbose_name_plural = verbose_name = "02开发任务"

    def __str__(self):
        return "{}的开发任务".format(self.writer)


class OtherTask(models.Model):
    """
    科技服务生信部门的其他任务管理
    """
    task_detail = models.CharField(verbose_name="任务内容", max_length=200,
                                   blank=True, null=True)
    start_time = models.DateField(verbose_name="开始时间",
                                  blank=True, null=True)
    end_time = models.DateField(verbose_name="结束时间", blank=True, null=True)
    finish_status = models.CharField(
        verbose_name="完成情况简述", max_length=200, blank=True, null=True)
    note = models.TextField(
        verbose_name="备注", blank=True, null=True)
    is_finish = models.CharField(
        verbose_name="完成情况", max_length=200, blank=True, null=True)
    user_in_charge = models.CharField(
        verbose_name="负责人", max_length=200, blank=True, null=True)
    writer = models.ForeignKey(
        verbose_name="填写人", to=User, on_delete=models.SET_NULL,
        blank=True, null=True)
    history_date = models.TextField(
        verbose_name="历史填写日期", blank=True, null=True
    )
    write_date = models.DateField(
        verbose_name="填写日期", blank=True, null=True
    )

    class Meta:
        verbose_name_plural = verbose_name = "03其他任务"

    def __str__(self):
        return "{}的其他任务".format(self.writer)
