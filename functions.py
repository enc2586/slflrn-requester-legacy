import requests as req
from bs4 import BeautifulSoup
from datetime import datetime
import re
import json

# const definition
SIGNIN_URL = "http://academic.petapop.com/sign/actionLogin.do"
APPLY_URL = "http://academic.petapop.com/self/requestSelfLrn.do"
CANCEL_URL = "http://academic.petapop.com/self/deleteSelfLrn.do"
TCRINFO_URL = "http://academic.petapop.com/self/writeSelfLrnReqst.do"
ROOMINFO_URL = "http://academic.petapop.com/clssrm/buldDrw.do"
SEATINFO_URL = "http://academic.petapop.com/clssrm/seatInfo.json"
LRNSTAT_URL = "http://academic.petapop.com/self/mainSelfLrnReqst.do"

BS_PROCESS = [1, 3, 4, 5, 6]

numbers = re.compile('\d')


def tidy(str):
    strList = str.split()
    result = " ".join(strList)

    return result

# 성공 시 시리얼번호 return
# 실패 시 음수 return


def apply(id, pw, rtcr, ctcr, room, pd, date, act, cont):
    usr_data = {
        "id": id,
        "password": pw,
    }

    form_data = {
        "actCn": cont,
        "actCode": act,
        "cchTcherId": ctcr,
        "clssrmId": room,
        "lrnPd": pd,
        "roomTcherId": rtcr,
        "sgnId": date,
    }

    with req.session() as sess:
        res = sess.post(SIGNIN_URL, data=usr_data)
        pgdata_raw = BeautifulSoup(res.content.decode('utf-8'), "html.parser")
        login_chk = tidy(pgdata_raw.li.get_text())

        if login_chk == "선생님은 가입해주세요.":
            return -1

        res = sess.post(APPLY_URL, data=form_data)
        response = json.loads(res.content.decode('utf-8'))

        if response['result']['success'] == True:
            return response['slrnNo']

        else:
            return -2

# 성공 시 True return
# 실패 시 음수 return


def cancel(id, pw, serial):
    usr_data = {
        "id": id,
        "password": pw,
    }

    form_data = {
        "slrnNo": serial,
    }

    with req.session() as sess:
        res = sess.post(SIGNIN_URL, data=usr_data)
        pgdata_raw = BeautifulSoup(res.content.decode('utf-8'), "html.parser")
        login_chk = tidy(pgdata_raw.li.get_text())

        if login_chk == "선생님은 가입해주세요.":
            return -1

        res = sess.post(CANCEL_URL, data=form_data)
        response = json.loads(res.content.decode('utf-8'))

        if response['result']['success'] == True:
            return True

        else:
            return -2

# 특정 특별실 잔여인원 return
# 실패 시 음수 return


def seatinfo(id, pw, rmid, pd, date):
    usr_data = {
        "id": id,
        "password": pw,
    }

    form_data = {
        "searchSgnId": date,
        "searchLrnPd": pd,
        "clssrmId": rmid,
    }

    with req.session() as sess:
        res = sess.post(SIGNIN_URL, data=usr_data)
        pgdata_raw = BeautifulSoup(res.content.decode('utf-8'), "html.parser")
        login_chk = tidy(pgdata_raw.li.get_text())

        if login_chk == "선생님은 가입해주세요.":
            return -1

        res = sess.post(SEATINFO_URL, data=form_data)
        response = json.loads(res.content.decode('utf-8'))

        if response['result']['success'] == True:
            return response['data']['seatCo']-response['data']['stdntCnt']

        else:
            return -2

# {'선생님': 'id'} dict return
# 실패 시 음수 return


def getTeacherInfo(id, pw):
    usr_data = {
        "id": id,
        "password": pw,
    }

    with req.session() as sess:
        res = sess.post(SIGNIN_URL, data=usr_data)
        pgdata_raw = BeautifulSoup(res.content.decode('utf-8'), "html.parser")
        login_chk = tidy(pgdata_raw.li.get_text())

        if login_chk == "선생님은 가입해주세요.":
            return -1

        reqest = sess.get(TCRINFO_URL)
        res = reqest.content.decode('utf-8')

        site_data = BeautifulSoup(res, 'html.parser')

        tcr = {}
        for element in site_data.find_all('option'):
            if element['value']:
                tcr[element.get_text()] = element['value']

        if not tcr:
            return -2

        tcr['지도교사없음'] = ''
        return tcr


# {'이름': {'floor': '층', 'maxppl': '최대인원', 'tcher': '담당교사', 'id': '교샤id'}} dict return
# 실패 시 음수 return
def getRoomInfo(id, pw):
    usr_data = {
        "id": id,
        "password": pw,
    }

    with req.session() as sess:
        res = sess.post(SIGNIN_URL, data=usr_data)
        pgdata_raw = BeautifulSoup(res.content.decode('utf-8'), "html.parser")
        login_chk = tidy(pgdata_raw.li.get_text())

        if login_chk == "선생님은 가입해주세요.":
            return -1

        res = sess.get(ROOMINFO_URL)
        response = BeautifulSoup(
            res.content.decode('utf-8'), "html.parser")

        rawlst = response.select(
            'div > div > div > div.data-list.custom-list > table > tbody > tr')

        rmlst = {}
        for rawhtml in rawlst:
            datalst = rawhtml.select('td')
            name = datalst[1].get_text()
            if not ('삭제' in name):
                rmlst[name] = {
                    "floor": datalst[0].get_text(),
                    "maxppl": tidy(datalst[3].get_text()),
                    "tcher": datalst[2].get_text(),
                    "id": datalst[4].select_one('div > input')['value'],
                }

        if not rmlst:
            return -2

        return rmlst

# 신청 현황 dictionary return
# 실패 시 음수 return

def isCredentialValid(id, pw):
    usr_data = {
        "id": id,
        "password": pw,
    }

    with req.session() as sess:
        res = sess.post(SIGNIN_URL, data=usr_data)
        pgdata_raw = BeautifulSoup(res.content.decode('utf-8'), "html.parser")
        login_chk = tidy(pgdata_raw.li.get_text())

        if login_chk == "선생님은 가입해주세요.":
            return False
        else:
            return True


id = "enc2586"
pw = "rhkgkrrh1!"

print(getTeacherInfo(id, pw))