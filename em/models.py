from django.contrib.auth.models import User
from django.db import models


class Departments(models.Model):
    """公司部门管理"""
    # TODO: 最好在之后对不确定层级的逐级一对多非二叉树结构进行简化，统一取消外键
    name = models.CharField(
        verbose_name="部门名称", max_length=32,
    )
    created_at = models.DateField(
        verbose_name="记录时间", auto_now_add=True,
    )
    manager = models.ForeignKey(
        User, verbose_name="部门主管", on_delete=models.CASCADE
    )
    is_valid = models.BooleanField(
        verbose_name="是否有效", default=True,
    )
    
    class Meta:
        abstract = True


class Lv1Departments(Departments):
    """公司部门管理"""
    
    class Meta:
        verbose_name_plural = verbose_name = "一级部门"

    def __str__(self):
        return '%s' % self.name


class Lv2Departments(Departments):
    """子部门管理"""
    superior = models.ForeignKey(
        Lv1Departments, verbose_name="上级部门", on_delete=models.CASCADE
    )
    
    class Meta:
        verbose_name_plural = verbose_name = "二级部门"

    def __str__(self):
        return '%s-%s' % (self.superior, self.name)


class Employees(models.Model):
    """公司在职员工管理"""
    user = models.OneToOneField(
        User, verbose_name="登陆名", on_delete=models.CASCADE
    )
    department = models.ForeignKey(
        Lv2Departments, verbose_name="所属部门", null=True, blank=True,
        on_delete=models.CASCADE
    )
    dingtalk_id = models.CharField(
        verbose_name="钉钉编号", max_length=32,
    )
    dingtalk_name = models.CharField(
        verbose_name="钉钉姓名", max_length=32,
    )
    submit_date = models.DateField(
        verbose_name="提交日期", auto_now_add=True,
    )
    is_on_job = models.BooleanField(
        verbose_name="是否在职", default=True
    )

    class Meta:
        verbose_name_plural = verbose_name = '部门员工'

    def __str__(self):
        return '【{:s}】-【{:s}】'.format(self.user.username, self.dingtalk_id)
