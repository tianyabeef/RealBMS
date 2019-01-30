from django.db import models
from django.contrib.auth.models import User


class TrainingCourse(models.Model):
    saler = models.ForeignKey(
        User, verbose_name='业务员', on_delete=models.SET_NULL,
        blank=True, null=True)
    partner = models.CharField(
        max_length=50, verbose_name="客户姓名", blank=True, null=True
    )
    issuingUnit = models.CharField(
        '开票单位', max_length=25, default='sh', blank=True, null=True)
    registration_fee = models.DecimalField(
        '报名费', max_digits=12, decimal_places=2, blank=True, null=True)
    content = models.CharField('发票内容', max_length=200,blank=True, null=True)
    amount = models.DecimalField('开票金额', max_digits=9,
                                 decimal_places=2,blank=True, null=True)
    invoice_date = models.DateField('开票日期', null=True, blank=True)
    amount_in = models.DecimalField('到款金额', max_digits=12, null=True,
                                    decimal_places=2, blank=True)
    amount_in_date = models.DateField('到款日期', null=True, blank=True)
    trainingcourse = models.CharField('培训班', max_length=50,
                                      blank=True, null=True)
    note = models.CharField('备注', max_length=200,
                                      blank=True, null=True)
    is_submit = models.BooleanField('提交', default=False)

    def __str__(self):
        return self.partner + "---" + self.trainingcourse

    class Meta:
        verbose_name = "培训班管理"
        verbose_name_plural = "培训班管理"
