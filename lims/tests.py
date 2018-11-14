from django.core.mail import send_mail
from django.test import TestCase

# Create your tests here.
from BMS import settings

if __name__ == '__main__':
    import os
    os.environ.update({"DJANGO_SETTINGS_MODULE": "BMS.settings"})
    send_mail(subject="通知",message="内容",html_message="<h1>我啊啊啊啊啊啊啊啊啊</h1>",
              from_email=settings.EMAIL_FROM,
              recipient_list=["love949872618@qq.com", ],
              fail_silently=False)
