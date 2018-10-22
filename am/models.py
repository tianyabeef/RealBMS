from django.db import models
from django.contrib.auth.models import User
from pm.models import AnaSubmit


class AnaExecute(models.Model):
    """执行生信分析步骤"""
    ana_submit = models.OneToOneField(
        AnaSubmit, verbose_name="子项目编号（分析）"
    )
    analyst = models.ForeignKey(
        User, verbose_name="生信分析员"
    )
    end_date = models.DateField(
        verbose_name="实际结束日期", blank=True, null=True
    )
    submit_date = models.DateField(
        verbose_name="分析提交日期", auto_now_add=True
    )
    confirmation_sheet = models.URLField(
        verbose_name="分析确认单", max_length=512, blank=True, null=True
    )
    ana_result_path = models.CharField(
        verbose_name="分析结果路径", max_length=512, blank=True, null=True
    )
    baidu_link = models.CharField(
        verbose_name="分析结果链接", max_length=512, blank=True, null=True
    )
    notes = models.TextField(
        verbose_name="备注", null=True, blank=True
    )
    is_submit = models.BooleanField(
        verbose_name="是否提交", default=False,
    )
    
    class Meta:
        verbose_name = '4分析任务执行'
        verbose_name_plural = verbose_name

    def __str__(self):
        return '%s' % self.ana_submit.ana_slug

    
class WeeklyReport(models.Model):
    """
    TODO: 周报管理
    科技服务生信部门的周报管理;
    初级目标：团队成员登陆BMS上传周报，然后主管登陆下载，具体字段    
    高级目标：团队成员登陆BMS系统填写具体事项，然后主管登陆点击下载，生成具体周报
    字段：填写人，记录时间，汇报周期（时间段），附件，子项，总体进度，负责人    
    """
    reporter = None
    submit_date = None
    report_interval = None
    

class SubWeeklyReport(models.Model):
    """
    TODO: 周报子项目管理
    字段：项目，预计开始时间，预计完成时间，目前状态，是否完成，
    """
