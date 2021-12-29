import requests as req
from bs4 import BeautifulSoup
from datetime import datetime
import json

SIGNIN_URL = "http://academic.petapop.com/sign/actionLogin.do"
APPLY_URL = "http://academic.petapop.com/self/requestSelfLrn.do"

usr_data = {
    "id": "enc2586",
    "password": "rhkgkrrh1!",
}

form_data = {
    "actCn": "키오스크",
    "actCode": "ACT004",
    "cchTcherId": "USRCNFRM_00000000013",
    "clssrmId": "CLSSRM_0000000000075",
    "lrnPd": "1",
    "roomTcherId": "USRCNFRM_00000000441",
    "sgnId": "20210830",
}

print("신청할 정보: " + str(form_data))


def tidy(str):
    str_lst = str.split()
    str_res = " ".join(str_lst)

    return str_res


with req.session() as sess:
    res = sess.post(SIGNIN_URL, data=usr_data)
    pgdata_raw = BeautifulSoup(res.content.decode("utf-8"), "html.parser")
    login_chk = tidy(pgdata_raw.li.get_text())

    if login_chk == "선생님은 가입해주세요.":
        print("Failed to log in.")

    req = sess.post(APPLY_URL, data=form_data)
    res = json.loads(req.content.decode("utf-8"))

    if res['result']['success'] == True:
        print("성공: " + res['slrnNo'])
    else:
        print("Fail")
