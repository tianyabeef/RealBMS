from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.admin import ModelAdmin
from django.contrib.auth.hashers import make_password, check_password
from BMS.notice_mixin import NotificationMixin
from BMS.admin_bms import BMS_admin_site
from .models import Invoice, Contract, InvoiceTitle, BzContract
from fm.models import Invoice as fm_Invoice
from django.contrib import messages
from datetime import datetime
from django.utils.html import format_html
from django import forms
from django.forms.models import BaseInlineFormSet
from daterange_filter.filter import DateRangeFilter
from django.contrib.admin.views.main import ChangeList
from django.db.models import Sum
from django.contrib.auth.models import User,Group
from import_export import resources
from import_export.admin import ImportExportActionModelAdmin,ExportActionModelAdmin
from import_export import fields
from operator import is_not
from functools import partial
from django.utils import formats
from BMS.settings import DINGTALK_APPKEY, DINGTALK_SECRET, DINGTALK_AGENT_ID
from em.models import Employees
from nm.models import DingtalkChat
import re
from django.db.models import Q

class InvoiceTitleAdmin(ImportExportActionModelAdmin):
    """
    发票抬头的Admin
    """
    list_display = ('title', 'tariffItem')
    fields = ('title', 'tariffItem')
    search_fields = ['title','tariffItem']
    list_per_page = 50


class InvoiceForm(forms.ModelForm):
    '''
    开票申请form
    '''
    def clean_amount(self):##clean_data的验证顺序是按照fields顺序
        contract_match = re.match("【(.*)】-.*", str(self.cleaned_data['contract']))
        if contract_match:
            obj_contract = Contract.objects.filter(contract_number=contract_match.group(1)).first()
            if self.cleaned_data['period'] == 'FIS':
                q = Invoice.objects.filter(contract=self.cleaned_data['contract']).filter(period='FIS')\
                    .aggregate(Sum('amount'))
                if q['amount__sum']:
                    if q['amount__sum'] + self.cleaned_data['amount'] > obj_contract.fis_amount:
                        raise forms.ValidationError('首款已开票金额%s元，超出可开票总额' % q['amount__sum'])
            if self.cleaned_data['period'] == 'FIN':
                q = Invoice.objects.filter(contract=self.cleaned_data['contract']).filter(period='FIN')\
                    .aggregate(Sum('amount'))
                if q['amount__sum']:
                    if q['amount__sum'] + self.cleaned_data['amount'] > obj_contract.fin_amount:
                        raise forms.ValidationError('尾款已开票金额%s元，超出可开票总额' % q['amount__sum'])
        return self.cleaned_data['amount']


class ContractForm(forms.ModelForm):
    '''
    合同的from
    '''
    def clean_contract_file(self):
        if self.cleaned_data['receive_date'] and (not self.cleaned_data["contract_file"]):
            raise forms.ValidationError("合同寄回日期已填入，请把合同文件添加上！！")
        return self.cleaned_data['contract_file']


class InvoiceAdmin(admin.ModelAdmin, NotificationMixin):
    """
    合同的开票申请Admin
    """
    appkey = DINGTALK_APPKEY
    appsecret = DINGTALK_SECRET
    list_display = ('contract', 'title', 'period', 'amount', 'issuingUnit','note', 'submit')
    list_display_links = ('contract',)
    actions = ['make_invoice_submit']
    fields = (('contract', 'title'), ('issuingUnit', 'period', 'type'), 'amount',('content', 'note'))
    # raw_id_fields = ['title',]
    autocomplete_fields = ('contract', 'title',)
    radio_fields = {'issuingUnit':admin.HORIZONTAL, 'period': admin.HORIZONTAL, 'type': admin.HORIZONTAL}
    list_per_page = 50
    ordering = ['-id']
    form = InvoiceForm

    def make_invoice_submit(self, request, queryset):
        """
        批量提交开票申请
        """
        i = 0  #提交成功的数量
        n = 0  #提交过的数量
        t = 0  #选中的总数量
        for obj in queryset:
            t += 1
            if not obj.submit:
                fm_Invoice.objects.create(invoice=obj, tax_amount=6)
                obj.submit = True
                obj.save()
                i += 1
                # if obj.contract.is_status != 2:  #与市场部（方华琦）沟通不做任何限制
                #     obj.contract.is_status = 2   #提交第一个发票申请的状态,改为：已申请开票。合同就不能在修改了
                #     obj.contract.save()
                #新的开票申请 通知财务部5
                for j in User.objects.filter(groups__id=5):
                    fm_chat_id = DingtalkChat.objects.get(chat_name="财务钉钉群-BMS").chat_id # TODO改为财务的钉钉群
                    content = "【上海锐翌生物科技有限公司-BMS系统测试通知】测试消息," + " 合同名称：%s 款期： %s  金额：%s  提交了开票申请"%(obj.contract.name, obj.period, obj.amount)
                    self.send_group_message(content,fm_chat_id)
            else:
                n += 1
        if i > 0 and n > 0:
            self.message_user(request, '您选中了%s个，其中%s 个开票申请已提交过，不能再次提交，%s个提交了开票申请' % (t,n,i), level=messages.ERROR)
        elif i>0 and n==0:
            self.message_user(request, '您选中了%s个，其中%s个提交了开票申请' % (t, i), level=messages.ERROR)
        else:
            self.message_user(request, '您选中了%s个，其中%s 个开票申请已提交过，不能再次提交' % (t, n), level=messages.ERROR)
    make_invoice_submit.short_description = '提交开票申请到财务'

    def get_actions(self, request):
        actions = super().get_actions(request)
        for group in request.user.groups.all():
            if group.id == 7 or group.id == 12:  # 市场部总监，销售总监
                if "make_invoice_submit" in actions:
                    del actions["make_invoice_submit"]
        return actions

    def get_readonly_fields(self, request, obj=None):
        if obj:
            if obj.submit:
                return ('contract', 'title', 'issuingUnit', 'period', 'type', 'amount', 'content', 'note')
        return self.readonly_fields

class InvoiceInlineFormSet(BaseInlineFormSet):
    '''
    合同的开票申请的FormSet
    '''
    def clean(self):
        super().clean()
        total = {}
        total['fis'] = 0
        total['fin'] = 0
        for form in self.forms:
            if not form.is_valid():
                return
            if form.cleaned_data:
                if form.cleaned_data['period'] == 'FIS':
                    total['fis'] += form.cleaned_data['amount']
                if form.cleaned_data['period'] == 'FIN':
                    total['fin'] += form.cleaned_data['amount']
            self.instance.__total__ = total


class InvoiceInline(admin.StackedInline):
    ''''
        合同管理中的开票申请（Inline）
    '''
    # form = InvoiceForm # TODO 对发票的总款额和首付款，尾款的限制
    model = Invoice
    formset = InvoiceInlineFormSet
    extra = 1
    fields = (('title', 'amount'), ('issuingUnit', 'period', 'type'),('content', 'note'))
    # autocomplete_fields = ('title',)   # TODO 当数据量较多是，下拉框会变得很长，有待优化
    raw_id_fields = ('title',)
    radio_fields = {"period": admin.HORIZONTAL, 'issuingUnit':admin.HORIZONTAL, "type":admin.HORIZONTAL}
    def get_readonly_fields(self, request, obj=None):
        if obj.is_status == 3:
            self.readonly_fields = ['title','issuingUnit','period', 'amount','type','content', 'note']
        return self.readonly_fields


class ContractChangeList(ChangeList):
    '''
    合同的ChangeList页面统计
    '''
    def get_results(self, *args, **kwargs):
        super().get_results(*args, **kwargs)
        fis_amount = self.result_list.aggregate(fis_sum=Sum('fis_amount'))
        fin_amount = self.result_list.aggregate(fin_sum=Sum('fin_amount'))
        all_amount = self.result_list.aggregate(all_sum=Sum('all_amount'))
        fis_amount_in = self.result_list.aggregate(fis_amount_in_sum=Sum('fis_amount_in'))
        fin_amount_in = self.result_list.aggregate(fin_amount_in_sum=Sum('fin_amount_in'))
        self.amount = '%.2f' % ((fis_amount['fis_sum'] or 0) + (fin_amount['fin_sum'] or 0))
        self.amount_input = '%.2f' % (all_amount['all_sum'] or 0)
        self.amount_in = '%.2f' % ((fis_amount_in['fis_amount_in_sum'] or 0) + (fin_amount_in['fin_amount_in_sum'] or 0))


class SaleListFilter(admin.SimpleListFilter):
    '''合同中的过滤器'''
    title = '业务员'
    parameter_name = 'Sale'

    def lookups(self, request, model_admin):
        qs_sale = User.objects.filter(groups__id=3)
        qs_company = User.objects.filter(groups__id=6)
        value = ['sale'] + list(qs_sale.values_list('username', flat=True)) + \
                ['company'] + list(qs_company.values_list('username', flat=True))
        label = ['销售'] + ['——' + i.last_name + i.first_name for i in qs_sale] + \
                ['公司'] + ['——' + i.last_name + i.first_name for i in qs_company]
        return tuple(zip(value, label))

    def queryset(self, request, queryset):
        if self.value() == 'sale':
            return queryset.filter(salesman__in=list(User.objects.filter(groups__id=3)))
        if self.value() == 'company':
            return queryset.filter(salesman__in=list(User.objects.filter(groups__id=6)))
        qs = User.objects.filter(groups__in=[3, 6])
        for i in qs:
            if self.value() == i.username:
                return queryset.filter(salesman=i)


class ContractResource(resources.ModelResource):
    """
    按照合同号导出
    """
    contract_number = fields.Field(column_name="合同号",attribute="contract_number")
    contract_name = fields.Field(column_name="合同名称",attribute="name")
    invoice_issuingUnit = fields.Field(column_name="开票单位")
    receive_date = fields.Field(column_name="合同寄到日",attribute="receive_date")
    invoice_times = fields.Field(column_name="开票次数")
    invoice_date = fields.Field(column_name="开票日期")
    invoice_income = fields.Field(column_name="回款金额")
    invoice_income_date = fields.Field(column_name="回款时间")
    contract_type = fields.Field(column_name="类型")
    contract_salesman = fields.Field(column_name="业务员")
    contract_price = fields.Field(column_name="单价",attribute="price")
    contract_range = fields.Field(column_name="价格区间",attribute="range")
    contract_all_amount = fields.Field(column_name="总款额",attribute="all_amount")
    contract_fis_amount = fields.Field(column_name="首款",attribute="fis_amount")
    contract_fin_amount = fields.Field(column_name="尾款",attribute="fin_amount")
    contract_send_date = fields.Field(column_name="合同寄出日",attribute="send_date")
    class Meta:
        model = Contract
        skip_unchanged = True
        fields = ('contract_number','contract_name','invoice_issuingUnit','receive_date','invoice_times','invoice_date','invoice_income',
                  'invoice_income_date','contract_type','contract_salesman','contract_price','contract_range',
                  'contract_all_amount','contract_fis_amount','contract_fin_amount','contract_send_date')
        export_order = ('contract_number','contract_name','invoice_issuingUnit','receive_date','invoice_times','invoice_date','invoice_income',
                        'invoice_income_date','contract_type','contract_salesman','contract_price','contract_range',
                  'contract_all_amount','contract_fis_amount','contract_fin_amount','contract_send_date')
    def dehydrate_invoice_issuingUnit(self,contract):
        invoices = Invoice.objects.filter(contract = contract)
        if invoices:
            return invoices[0].title.title
        return ""
    def dehydrate_invoice_times(self, contract):
        return len(fm_Invoice.objects.filter(invoice__contract=contract))
    def dehydrate_invoice_date(self,contract):
        return  [formats.date_format(date, 'Y-m-d') for date in list(filter(partial(is_not, None),fm_Invoice.objects.filter(invoice__contract=contract).values_list('date',flat=True)))]
    def dehydrate_invoice_income(self, contract):
        return [float(income) for income in list(filter(partial(is_not, None),fm_Invoice.objects.filter(invoice__contract=contract).values_list('income',flat=True)))]
    def dehydrate_invoice_income_date(self, contract):
        return [formats.date_format(income_date, 'Y-m-d') for income_date in list(filter(partial(is_not, None),fm_Invoice.objects.filter(invoice__contract=contract).values_list('income_date',flat=True)))]
    def dehydrate_contract_type(self,contract):
        return contract.get_type_display()
    def dehydrate_contract_range(self,contract):
        return contract.get_range_display()
    def dehydrate_contract_salesman(self,contract):
        return "%s%s"%(contract.salesman.last_name,contract.salesman.first_name)


class ContractAdmin(ExportActionModelAdmin,NotificationMixin):
    """
    合同中的Admin
    """
    appkey = DINGTALK_APPKEY
    appsecret = DINGTALK_SECRET
    resource_class = ContractResource
    list_display = ('contract_number', 'name','partner_company_modify', 'contacts', 'type', 'salesman_name', 'price', 'range', 'all_amount', 'fis_income',
                    'fin_income', 'send_date', 'tracking_number', 'receive_date', 'file_link')
    date_hierarchy = 'send_date'
    inlines = [InvoiceInline,]
    radio_fields = {'type': admin.HORIZONTAL,'range':admin.HORIZONTAL}
    list_per_page = 50
    ordering = ['-id']
    fieldsets = (
        ('基本信息', {
            'fields': (('contract_number', 'name', 'type'),('contacts','contact_phone', 'contacts_email'),
                       ('contact_address', 'partner_company', 'salesman'), ('price', 'range'),
                       ('fis_amount', 'fin_amount', 'all_amount'),( 'contact_note'))
        }),
        ('邮寄信息', {
            'fields': (('tracking_number', 'send_date', 'receive_date'),)
        }),
        ('上传合同', {
            'fields': ('contract_file', 'contract_file_scanning')
        })
    )
    autocomplete_fields = ('salesman',)
    search_fields = ('contract_number', 'name', 'salesman__username')
    actions = ('make_receive',)
    form = ContractForm

    def partner_company_modify(self,obj):
        # 抬头的单位名称
        if obj.partner_company == "":
            invoices = Invoice.objects.filter(contract=obj)
            return  invoices[0].title.title if invoices else ""
        else:
            return obj.partner_company
    partner_company_modify.short_description = "单位"

    def salesman_name(self, obj):
        # 销售用户名或姓名显示
        name = obj.salesman.last_name + obj.salesman.first_name
        if name:
            return name
        return obj.salesman
    salesman_name.short_description = '业务员'

    def fis_income(self, obj):
        # 首款到账信息显示
        amount = obj.fis_amount
        if amount==0:
            if not obj.fis_date:
                obj.fis_amount_in = 0
                obj.fis_date = datetime.now().strftime("%Y-%m-%d")
                obj.save()
        income = obj.fis_amount_in or 0

        if amount - income > 0:
            return format_html('<span style="color:{};">{}</span>', 'red', '%s/%s' % (income, amount))
        elif amount - income == 0:
            if amount == 0 :
                return '%s/0'%(income)
            return '%s/%s' % (income, obj.fis_date)
        else:
            return format_html('<span style="color:{};">{}</span>', 'blue','%s/%s/%s' % (income,amount,obj.fis_date))
    fis_income.short_description = '首款'

    def fin_income(self, obj):
        # 尾款到账信息显示
        amount = obj.fin_amount
        if amount==0:
            if not obj.fin_date:
                obj.fin_amount_in = 0
                obj.fin_date = datetime.now().strftime("%Y-%m-%d")
                obj.save()
        income = obj.fin_amount_in or 0
        if amount - income > 0:
            return format_html('<span style="color:{};">{}</span>', 'red', '%s/%s' % (income, amount))
        elif amount - income == 0:
            if amount == 0 :
                return '%s/0'%(income)
            return '%s/%s' % (income, obj.fin_date)
        else:
            return format_html('<span style="color:{};">{}</span>', 'blue','%s/%s/%s' % (income,amount,obj.fin_date))
    fin_income.short_description = '尾款'

    def make_receive(self, request, queryset):
        # 批量记录合同回寄时间戳
        rows_updated = queryset.update(receive_date=datetime.now())
        for obj in queryset:
            if rows_updated:
                #合同寄到日 通知项目管理2
                content = "【上海锐翌生物科技有限公司-BMS系统测试通知】测试消息,合同号：%s寄回日期%s已经记录"% (obj.contract_number, obj.receive_date)
                if Employees.objects.filter(user=obj.salesman):
                    user_id = Employees.objects.get(user=obj.salesman).dingtalk_id
                if user_id:
                    self.send_work_notice(content, DINGTALK_AGENT_ID, user_id)
                    self.send_group_message(content, DingtalkChat.objects.get(chat_name="项目管理钉钉群-BMS").chat_id)
                self.message_user(request, '%s 个合同寄到登记已完成' % rows_updated)
            else:
                self.message_user(request, '%s 未能成功登记' % rows_updated, level=messages.ERROR)
    make_receive.short_description = '登记所选合同已收到'

    def get_changelist(self, request):
        return ContractChangeList

    def get_actions(self, request):
        actions = super().get_actions(request)
        for group in request.user.groups.all():
            if not group.id == 4:  # 除了市场部都没有登记所选合同的权限
                if "make_receive" in actions:
                    del actions["make_receive"]
        return actions

    def get_formsets_with_inlines(self, request, obj=None):
        for inline in self.get_inline_instances(request, obj):
            if isinstance(inline, InvoiceInline) and obj is None:
                continue
            yield inline.get_formset(request, obj), inline

    def get_queryset(self, request):
        # 只允许管理员,拥有该模型新增权限的人员，销售总监才能查看所有#TODO 给财务开通查询所有合同的权限，暂时先用
        haved_perm = False
        for group in request.user.groups.all():
            if group.id == 7 or group.id == 2 or group.id == 12:# 市场部总监，项目管理，销售总监
                haved_perm=True
        qs = super(ContractAdmin, self).get_queryset(request)

        if request.user.is_superuser or request.user.has_perm('mm.add_contract') or haved_perm or request.user.id == 40 or request.user.id == 6:
            return qs
        return qs.filter(salesman=request.user)

    def get_list_filter(self, request):
        #销售总监，admin，有新增权限的人可以看到salelistFilter
        haved_perm = False
        for group in request.user.groups.all():
            if group.id == 7 or group.id == 2 or group.id == 12:  # 市场部总监，项目管理，销售总监
                haved_perm=True
        if request.user.is_superuser or request.user.has_perm('mm.add_contract') or haved_perm:
            return [SaleListFilter, 'type', ('send_date', DateRangeFilter),('receive_date',DateRangeFilter)]
        return ['type', ('send_date', DateRangeFilter),('receive_date',DateRangeFilter)]

    def get_readonly_fields(self, request, obj=None):
        if obj:
            if obj.is_status >= 2:
                return ['contract_number', 'name', 'type', 'salesman','contacts','contact_phone','contacts_email','contact_address','partner_company', 'price', 'range', 'fis_amount', 'fin_amount', 'all_amount','tracking_number', 'send_date', 'receive_date', 'contract_file','contact_note']
        return self.readonly_fields

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for obj in formset.deleted_objects:
            obj.delete()
        if instances:
            fis_amount = instances[0].contract.fis_amount
            fin_amount = instances[0].contract.fin_amount
            if (fis_amount < formset.instance.__total__['fis']) or (fin_amount < formset.instance.__total__['fin']):
                self.message_user(request, '首款已开票金额%s元，超出可开票总额，未成功添加开票' % fis_amount)
            else:
                for instance in instances:
                    instance.save()
                formset.save_m2m()


    def save_model(self, request, obj, form, change):
        # 新增合同的时候，合作伙伴的email就在用户表中同步新增好了，客户提交样品信息单的时候，登入系统使用 发钉钉通知
        content = ""
        contract = Contract.objects.filter(id=obj.id)
        user = User.objects.filter(username=obj.contacts_email)
        user_id = False
        if Employees.objects.filter(user=obj.salesman):
            user_id = Employees.objects.get(user=obj.salesman).dingtalk_id
        if change:
            if obj.contacts_email and (contract[0].salesman.username != obj.contacts_email):
                if not user:
                    tt = User.objects.create(username=obj.contacts_email, password=make_password(obj.contacts_email),
                                             email=obj.contacts_email, is_staff=True)
                    group_info = Group.objects.get(name="合作伙伴")
                    tt.groups.add(group_info)
                    content = content + "【上海锐翌生物科技有限公司-BMS系统测试通知】测试消息:修改合同操作，合同编号" + obj.contract_number + "系统自动开通了老师账户一个，账户名：%s，" % (
                        obj.contacts_email)
                # else:
                #     content = content + "修改合同操作，合同编号" + obj.contract_number + "系统中已经存在老师账户一个，账户名：%s，" % (
                #         obj.contacts_email)

                if contract:
                    if obj.receive_date and contract[0].receive_date and (obj.receive_date != contract[0].receive_date):
                        content = content + "【上海锐翌生物科技有限公司-BMS系统测试通知】测试消息:收到客户新合同,合同寄回日有变更，" + "合同号：%s\t合同名称：%s\t合同联系人：%s\t电话：%s" % \
                                  (obj.contract_number, obj.name, obj.contacts, obj.contact_phone)
                    elif obj.receive_date and (not contract[0].receive_date):
                        content = content + "【上海锐翌生物科技有限公司-BMS系统测试通知】测试消息:客户收到新合同，" + "合同号：%s\t合同名称：%s\t合同联系人：%s\t电话：%s" % \
                                  (obj.contract_number, obj.name, obj.contacts, obj.contact_phone)
        else:
            if not user:#合同联系人的邮箱在系统中没有账号
                tt = User.objects.create(username=obj.contacts_email, password=make_password(obj.contacts_email),
                                         email=obj.contacts_email, is_staff=True)
                group_info = Group.objects.get(name="合作伙伴")
                tt.groups.add(group_info)
                content = content + "【上海锐翌生物科技有限公司-BMS系统测试通知】测试消息:新增合同操作，合同编号" + obj.contract_number + "系统自动开通了老师账户一个，账户名：%s，" % (obj.contacts_email)
            else:
                content = content + "【上海锐翌生物科技有限公司-BMS系统测试通知】测试消息:新增合同操作，合同编号" + obj.contract_number + "系统中已经存在老师账户一个，账户名：%s，" % (obj.contacts_email)
            if obj.receive_date:
                content = content + "【上海锐翌生物科技有限公司-BMS系统测试通知】测试消息,客户收到新合同，" + "合同号：%s\t合同名称：%s\t合同联系人：%s\t电话：%s" % \
                          (obj.contract_number, obj.name, obj.contacts, obj.contact_phone)

            message_content = ""
            if obj.fis_amount + obj.fin_amount != obj.all_amount:
                message_content += "  首款额+尾款额≠总款额"

            if user_id:
                self.send_work_notice(content, DINGTALK_AGENT_ID, user_id)
                if not self.send_dingtalk_result:
                    message_content += "  钉钉通知发送失败"
            else:
                message_content += "  这个销售的没有钉钉ID号"
            self.message_user(request, message_content)

        # 1、新增快递单号时自动记录时间戳
        if obj.tracking_number and not obj.send_date:
            obj.send_date = datetime.now()
        elif not obj.tracking_number:
            obj.send_date = None
        if content!="":
            self.send_group_message(content, DingtalkChat.objects.get(chat_name="项目管理钉钉群-BMS").chat_id)
        obj.save()

    def get_changeform_initial_data(self, request):
        initial = super(ContractAdmin,self).get_changeform_initial_data(request)
        initial["type"] = 1 #
        initial["contract_number"] = "RY"
        return initial

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "salesman":
            sales_users = User.objects.filter(Q(groups__id=3) | Q(groups__id=7))
            kwargs["queryset"] =  sales_users
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class BzContractAdmin(admin.ModelAdmin):
    '''
    报账合同的Admin
    '''
    list_display = ['contract_number', 'name', 'send_date', 'receive_date', 'file_link']
    list_per_page = 50
    filter_horizontal = ["contract", ]
    autocomplete_fields = ('salesman',)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "salesman":
            sales_users = User.objects.filter(Q(groups__id=3) | Q(groups__id=7))
            kwargs["queryset"] =  sales_users
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

BMS_admin_site.register(BzContract, BzContractAdmin)
BMS_admin_site.register(Contract, ContractAdmin)
BMS_admin_site.register(Invoice, InvoiceAdmin)
BMS_admin_site.register(InvoiceTitle,InvoiceTitleAdmin)