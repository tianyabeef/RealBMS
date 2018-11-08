from django.db import models
from django.contrib.auth.models import User
from django.utils.html import format_html


class InvoiceTitle(models.Model):
    title = models.CharField("发票抬头", max_length=100)
    tariffItem = models.CharField("税号", max_length=50, unique=True)

    class Meta:
        verbose_name = '发票抬头'
        verbose_name_plural = '发票抬头'

    def __str__(self):
        return '%s' % self.title


class Contract(models.Model):
    RANGE_CHOICES = (
        (1, '高于销售底价'),
        (2, '总监底价'),
        (3, '低于总监底价'),
    )
    TYPE_CHOICES = (
        (1, '16S/ITS'),
        (2, '宏基因组'),
        (3, '单菌'),
        (4, '转录组'),
        (5, '其它'),
    )
    contract_number = models.CharField('合同号', max_length=30, unique=True)
    name = models.CharField('合同名', max_length=100)
    type = models.IntegerField(
        '类型',
        choices=TYPE_CHOICES
    )
    salesman = models.ForeignKey(User, verbose_name='业务员', on_delete=models.SET_NULL, null=True)
    price = models.DecimalField('单价', max_digits=7, decimal_places=2, blank=True)
    range = models.IntegerField(
        '价格区间',
        choices=RANGE_CHOICES, blank=True
    )
    all_amount = models.DecimalField('总款额', max_digits=12, decimal_places=2)
    fis_amount = models.DecimalField('首款额', max_digits=12, decimal_places=2)
    fis_date = models.DateField('首款到款日', blank=True, null=True)
    fis_amount_in = models.DecimalField('已到首款额', max_digits=12, decimal_places=2, default=0)
    fin_amount = models.DecimalField('尾款额', max_digits=12, decimal_places=2, default=0)
    fin_date = models.DateField('尾款到款日', blank=True, null=True)
    fin_amount_in = models.DecimalField('已到尾款额', max_digits=12, decimal_places=2, default=0)
    send_date = models.DateField('合同寄出日', null=True, blank=True)
    tracking_number = models.CharField('快递单号', max_length=15, blank=True)
    receive_date = models.DateField('合同寄回日', null=True, blank=True)
    contract_file = models.FileField('附件', upload_to='uploads/%Y/%m', blank=True)
    contacts = models.CharField('合同联系人', max_length=15, blank=True)
    contacts_email = models.EmailField(verbose_name="合同联系人邮箱", default='')
    contact_phone = models.CharField('合同联系人电话', max_length=30, blank=True)
    contact_address = models.CharField('合同联系人地址', max_length=30, blank=True)
    partner_company = models.CharField(max_length=200, verbose_name="合作伙伴单位", default="")
    use_amount = models.DecimalField("已使用的金额", null=True, blank=True, max_digits=12, decimal_places=2, default=0)

    contact_note = models.TextField('合同备注', blank=True)

    class Meta:
        verbose_name = '合同管理'
        verbose_name_plural = '合同管理'

    def file_link(self):
        if self.contract_file:
            return format_html("<a href='%s'>下载</a>" % (self.contract_file.url,))
        else:
            return "未上传"

    file_link.short_description = "附件"
    file_link.allow_tags = True

    def __str__(self):
        return '%s' % self.contract_number


class Invoice(models.Model):
    PERIOD_CHOICES = (
        ('FIS', '首款'),
        ('FIN', '尾款'),
    )
    INVOICE_TYPE_CHOICES = (
        ('CC', '普票'),
        ('SC', '专票'),
    )
    ISSUING_UNIT_CHOICES = (
        ('sh', '上海锐翌'),
        ('hz', '杭州拓宏'),
        ('sd', '山东锐翌'),
        ('sz', '金锐生物'),
    )
    contract = models.ForeignKey(
        Contract,
        verbose_name='合同',
        on_delete=models.CASCADE,
    )
    title = models.ForeignKey(InvoiceTitle, verbose_name='发票抬头', on_delete=models.SET_NULL, null=True)
    issuingUnit = models.CharField('开票单位', choices=ISSUING_UNIT_CHOICES, max_length=25, default='sh')
    period = models.CharField('款期', max_length=3, choices=PERIOD_CHOICES, default='FIS')
    amount = models.DecimalField('发票金额', max_digits=9, decimal_places=2)
    type = models.CharField('发票类型', max_length=3, choices=INVOICE_TYPE_CHOICES, default='CC')
    content = models.TextField('发票内容', null=True)
    note = models.TextField('备注', null=True)
    submit = models.NullBooleanField('提交开票', null=True)

    class Meta:
        verbose_name = '开票申请'
        verbose_name_plural = '开票申请'

    def __str__(self):
        return '%.2f' % self.amount


class BzContract(models.Model):
    contract = models.ManyToManyField(Contract, verbose_name="对应合同", blank=True)

    contract_number = models.CharField('报账合同号', max_length=30, unique=True)
    name = models.CharField('报账合同名', max_length=100)
    salesman = models.ForeignKey(User, verbose_name='业务员', on_delete=models.SET_NULL, null=True)
    contact_note = models.TextField('报账合同备注', blank=True)

    send_date = models.DateField('合同寄出日', null=True, blank=True)
    tracking_number = models.CharField('快递单号', max_length=15, blank=True)
    receive_date = models.DateField('合同寄回日', null=True, blank=True)

    contract_file = models.FileField('附件', upload_to='uploads/报账/%Y/%m', blank=True)

    class Meta:
        verbose_name = '报账合同管理'
        verbose_name_plural = '报账合同管理'
