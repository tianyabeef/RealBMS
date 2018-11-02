from dingtalk_sdk_gmdzy2010.authority_request import AccessTokenRequest
from dingtalk_sdk_gmdzy2010.message_request import (
    SendGroupChatRequest, WorkNoticeRequest
)
from django.core.mail import send_mail


class NotificationMixinBase(object):
    """The base class for notifications including email, short message or
    dingtalk notice.
    """
    pass


class DingtalkNotificationMixin(NotificationMixinBase):
    """Mixin that supply dingtalk functions to admin"""
    appkey = None
    appsecret = None
    send_dingtalk_result = False
    
    def get_dingtalk_token(self):
        params = {"appkey": self.appkey, "appsecret": self.appsecret}
        request = AccessTokenRequest(params=params)
        request.get_json_response()
        return request.get_access_token()
    
    def send_work_notice(self, content, sender, recipient_list):
        params = {"access_token": self.get_dingtalk_token()}
        data = {
            "agent_id": sender,
            "userid_list": recipient_list,
            "msg": {"msgtype": "text", "text": {"content": content}}
        }
        request = WorkNoticeRequest(params=params, json=data)
        request.request_method = "post"
        request.get_json_response()
        self.send_dingtalk_result = request.call_status
    
    def send_group_message(self, content, chat_id):
        params = {"access_token": self.get_dingtalk_token()}
        data = {
            "chatid": chat_id,
            "msg": {"msgtype": "text", "text": {"content": content}}
        }
        request = SendGroupChatRequest(params=params, json=data)
        request.request_method = "post"
        request.get_json_response()
        self.send_dingtalk_result = request.call_status


class EmailNotificationMixin(NotificationMixinBase):
    """Mixin that supply email functions to admin"""
    send_email_result = False
    
    def send_email(self, content, sender, recipient_list, **kwargs):
        """This method is totally a copy of django send_mail()"""
        subject = kwargs.get("subject", "【BMS系统通知】")
        try:
            send_mail(subject, content, sender, recipient_list, **kwargs)
            self.send_email_result = True
        except:
            self.send_email_result = False

    
class NotificationMixin(EmailNotificationMixin, DingtalkNotificationMixin):
    """Mixin that both contain email and dingtalk"""
    pass
