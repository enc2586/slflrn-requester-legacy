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


def gettcrlst(id, pw):
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
def getrminfo(id, pw):
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


def getlrninfo(id, pw, date):
    usr_data = {
        "id": id,
        "password": pw,
    }

    form_data = {
        "searchSgnId": date,
    }

    with req.session() as sess:
        res = sess.post(SIGNIN_URL, data=usr_data)
        pgdata_raw = BeautifulSoup(res.content.decode('utf-8'), "html.parser")
        login_chk = tidy(pgdata_raw.li.get_text())

        if login_chk == "선생님은 가입해주세요.":
            return -1

        res = sess.get(LRNSTAT_URL, params=form_data)
        pgdata_raw = BeautifulSoup(res.content.decode('utf-8'), "html.parser")

        lrnlst = pgdata_raw.select(
            'div.custom-list.mt-3 > div > table > tbody > tr')

        lrndetail = []
        for item in lrnlst:
            datas = item.select('td')
            lrndetail.append(datas)

        lrndetail[0].pop(0)  # 전체학습 신청버튼 부분

        lrnstat = {}
        for item in lrndetail:
            item = list(map(str, item))
            for index in BS_PROCESS:
                item[index] = BeautifulSoup(item[index], 'html.parser')

            pd = ''.join(numbers.findall(item[0]))

            site = item[1].select_one('input')['value']
            area = site[site.find('[')+1:site.find(']')]
            room = tidy(site[site.find(']')+1:])

            act = item[3].select_one('option[selected=""]').get_text()
            content = item[4].select_one('input')['value']

            rawSerial = item[5].select_one('a')['href']
            serial = rawSerial[rawSerial.find('=')+1:]

            authchk = tidy(item[6].get_text())
            auth = True if authchk == '승인' else False

            lrnconfig = {
                "area": area,
                "room": room,
                "act": act,
                "content": content,
                "serial": serial,
                "auth": auth,
                "overlapped": lrnstat[pd]['overlapped']+1 if pd in lrnstat else 0,
            }
            lrnstat[pd] = lrnconfig

        return lrnstat

# 코드 사용시
# 이런 식으로 사용해보시죠

# 앞에 ** 을 붙이면
# dictionary를 풀어줍니다

# usr_data = {
#     'id': 'enc2586',
#     'pw': 'rhkgkrrh1!',
# }

usr_data = {
    'id': 'enc2586',
    'pw': 'rhkgkrrh1!',
}

datedata = {
    'date': '20211202'
}

form_data = {
    'rtcr': "USRCNFRM_00000000441",
    'ctcr': "USRCNFRM_00000000013", #지도
    'room': "CLSSRM_0000000000075",
    'pd': '3',
    'act': "ACT001",
    'cont': "세특작성",
    'date': datetime.now().strftime("%Y%m%d"),
}

# print(apply(**usr_data, **form_data))

# with open("roomData.json", "w", encoding='utf8') as f:
#     json.dump(gettcrlst(**usr_data), f, indent=4, ensure_ascii=False)
# roomData = json.loads(getrminfo(**usr_data))

# print(getrminfo(**usr_data))

print(apply(**usr_data, **form_data))
# print(gettcrlst(**usr_data))

# print(cancel('gungun625', 'spqjqldnlsj0625;', 136972))


# 수1실:  CLSSRM_00000000000423
# 코딩랩: CLSSRM_0000000000075
# 1-3:   CLSSRM_0000000000066
# 합동강의실: CLSSRM_0000000000040

# 연광흠: USRCNFRM_00000000441
# 최승재: USRCNFRM_00000000013
# 김대용: USRCNFRM_00000000437