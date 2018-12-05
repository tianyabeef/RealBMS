from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect
from dingtalk_sdk_gmdzy2010.authority_request import (
    AccessTokenRequest, SnsAccessTokenRequest, PersistentCodeRequest,
    SnsTokenRequest, UserInfoRequest,
)
from dingtalk_sdk_gmdzy2010.user_request import UseridByUnionidRequest
from BMS.settings import (
    DINGTALK_APPKEY, DINGTALK_SECRET, DINGTALK_APPID, DINGTALK_APPSECRET
)


def dingtalk_auth(request):
    # STEP 1. Get sns access_token
    params_1 = {"appid": DINGTALK_APPID, "appsecret": DINGTALK_APPSECRET}
    req_sns_access_token = SnsAccessTokenRequest(params=params_1)
    req_sns_access_token.get_json_response()
    sns_access_token = req_sns_access_token.get_sns_access_token()
    
    # STEP 2. Get persistent code
    params_2 = {"access_token": sns_access_token}
    data = {"tmp_auth_code": request.GET["code"]}
    req_persistent_code = PersistentCodeRequest(params=params_2, json=data)
    req_persistent_code.request_method = "post"
    req_persistent_code.get_json_response()
    ticket = req_persistent_code.get_ticket_for_sns_token()
    
    # STEP 3. Get sns token
    params_3 = {"access_token": sns_access_token}
    req_sns_token = SnsTokenRequest(params=params_3, json=ticket)
    req_sns_token.request_method = "post"
    req_sns_token.get_json_response()
    sns_token = req_sns_token.get_sns_token()
    
    # STEP 4. Get unionid
    params_4 = {"sns_token": sns_token}
    req_user_info = UserInfoRequest(params=params_4)
    req_user_info.get_json_response()
    user_info = req_user_info.get_user_info()
    
    # STEP 5. Get userid
    params_5 = {"appkey": DINGTALK_APPKEY, "appsecret": DINGTALK_SECRET}
    req_access_token = AccessTokenRequest(params=params_5)
    req_access_token.get_json_response()
    params_6 = {
        "access_token": req_access_token.get_access_token(),
        "unionid": user_info["unionid"]
    }
    req_userid = UseridByUnionidRequest(params=params_6)
    req_userid.get_json_response()
    
    # STEP 6. Authenticate the specified django-user
    user_check = authenticate(request, dingtalk_id=req_userid.get_userid())
    if user_check is not None:
        login(request, user_check)
    return HttpResponseRedirect("/")


