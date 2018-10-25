from django.db import models
from em.models import Employees


class DingtalkChat(models.Model):
    chat_id = models.CharField(
        verbose_name="群聊编号", primary_key=True, max_length=64
    )
    chat_name = models.CharField(
        verbose_name="群聊名称", max_length=32, null=True, blank=True,
        default="内部群聊"
    )
    chat_owner = models.ForeignKey(
        Employees, related_name="chat_owner", verbose_name="群主",
    )
    members = models.ManyToManyField(
        Employees, related_name="chat_members", verbose_name="群聊成员"
    )
    create_at = models.DateField(
        verbose_name="创建时间", auto_now_add=True
    )
    is_valid = models.BooleanField(
        verbose_name="是否有效", default=True
    )
    
    class Meta:
        verbose_name_plural = verbose_name = "钉钉群组"

    def __str__(self):
        return '%s' % self.chat_name


class ChatTemplates(models.Model):
    TEMPLATE_KIND = (
        "msg", u"文本消息"
        "2", u"msg"
        "3", u"msg"
    )
    name = models.CharField(
        verbose_name="名称", max_length=16, null=True, blank=True,
    )
    sign = models.CharField(
        verbose_name="签名", max_length=32, null=True, blank=True,
    )
    text = models.TextField(
        verbose_name="内容", null=True, blank=True,
    )
    link = models.CharField(
        verbose_name="链接", max_length=256, null=True, blank=True,
    )
    create_at = models.DateField(
        verbose_name="创建时间", auto_now_add=True
    )
    is_valid = models.BooleanField(
        verbose_name="是否有效", default=True
    )
    
    @property
    def msg_text(self):
        return self.sign + self.text
    
    class Meta:
        verbose_name_plural = verbose_name = "消息模板"
    
    def __str__(self):
        return '%s' % self.name
