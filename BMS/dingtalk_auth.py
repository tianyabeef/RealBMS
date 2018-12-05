# -*- coding: UTF-8 -*-
from django.contrib.auth.models import User
from em.models import Employees


class TokenAuthBackend(object):
    """
    User-defined authenticate backend for the report
    """
    def authenticate(self, request, dingtalk_id=None):
        try:
            employee = Employees.objects.get(dingtalk_id=dingtalk_id)
            login_user = User.objects.get(pk=employee.user_id)
        except Employees.DoesNotExist:
            return None
        return login_user
    
    def get_user(self, user_id):
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
        return user
