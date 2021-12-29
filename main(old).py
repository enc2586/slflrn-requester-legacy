import re
import json
import pyrebase
import random

import requests
import requests as req
from bs4 import BeautifulSoup
from datetime import datetime
from cryptography.fernet import Fernet

# defining CONSTANTS
# 상수 정의
SIGNIN_URL = "http://academic.petapop.com/sign/actionLogin.do"
APPLY_URL = "http://academic.petapop.com/self/requestSelfLrn.do?sgnId="
CANCEL_URL = "http://academic.petapop.com/self/deleteSelfLrn.do?slrnNo="
TCR_REQ_URL = 'http://academic.petapop.com/self/writeSelfLrnReqst.do?searchSgnId=20210620&searchLrnPd=1'
RM_REQ_URL_1 = "http://academic.petapop.com/clssrm/buldDrw.do?buldId=BUILD_"
RM_REQ_URL_2 = "&searchSgnId=20210621&searchLrnPd="


ENCRYPT_ITEM = ['id', 'pw']

RM_REQ_CODE = {
    'md': '0001',
    'cd': '0002',
    'ed': '0005',
}

ALLAPP_BTN_DISABLED = 'disabled="disabled"'

#loading CACHE
#캐시
HMRM_TCR = {
    11: "이주형",
    12: "연광흠",
    13: "김대용",
}
TCR_ID = {

}
CLSSRM_ID = {

}
ABL_PRD = [1, 2, 3]

#reading essential infos
#필수 정보 읽어오기
with open("./components/auth.json") as f:
    config = json.load(f)
    firebase = pyrebase.initialize_app(config)
    db = firebase.database()

with open("./components/crypto.key", "rb") as f:
    key = f.read()
    cry = Fernet(key)

#defining ERRORS
#에러 정의
class signinFailErr(Exception):
    def __init__(self):
        super(signinFailErr, self).__init__("Sign-in attempt failed.")

class uidAlreadyInUseErr(Exception):
    def __init__(self):
        super(uidAlreadyInUseErr, self).__init__("Requested UID was already registered.")

class alreadyRegisteredErr(Exception):
    def __init__(self):
        super(alreadyRegisteredErr, self).__init__("Requested ID was already registered.")

class noUidFoundErr(Exception):
    def __init__(self):
        super(noUidFoundErr, self).__init__("No matching UID found.")

#defining FUNCTIONS
#함수 정의
def encrypt(data):
    if type(data) == int:
        data = str(data)
    if type(data) != bytes:
        data = data.encode("utf-8")

    encrypted_b = cry.encrypt(data)
    encrypted = encrypted_b.decode("utf-8")

    return encrypted

def decrypt(data):
    if type(data) != bytes:
        data = data.encode("utf-8")

    decrypted_b = cry.decrypt(data)
    decrypted = decrypted_b.decode("utf-8")

    return decrypted

def tidy(str):
    str_lst = str.split()
    str_res = " ".join(str_lst)

    return str_res

def sidmng(sid_raw):
    if type(sid_raw) != int:
        sid = int(sid_raw)

    if sid // 1000 == 0:
        num = sid % 10
        sid = sid // 10 * 100 + num

    return sid

def freeUid():
    while True:
        uid = str(random.randrange(1000000)).zfill(6)

        uidchk = db.child('users').child(uid).get().val()
        if uidchk:
            continue

        break

    return uid

def crlsitedata(id, pw):
    usr_data = {
        "id": id,
        "password": pw,
    }

    with req.session() as sess:
        res = sess.post(SIGNIN_URL, data=usr_data)
        pgdata_raw = BeautifulSoup(res.content.decode("utf-8"), "html.parser")

    login_chk = tidy(pgdata_raw.li.get_text())
    if login_chk == "선생님은 가입해주세요.":
        raise signinFailErr

    return pgdata_raw

def getinfo(pgdata_raw):
    pgdata = tidy(pgdata_raw.li.get_text())

    std_pos = pgdata.find("번")

    name = tidy(pgdata[std_pos + 2:std_pos + 5])
    sid_raw = "".join(re.findall('\d+', pgdata[:std_pos]))
    sid = sidmng(sid_raw)

    data = {
        "name": name,
        "sid": sid,
    }

    return data

def getusrdata(uid):
    usr_data = db.child('users').child(uid).child('info').get().val()
    if not usr_data:
        raise noUidFoundErr

    for i in ENCRYPT_ITEM:
        usr_data[i] = decrypt(usr_data[i])

    return usr_data

def gettdyapp(usr_info):
    pgdata_raw = crlsitedata(usr_info['id'], usr_info['pw'])
    tr_raw = pgdata_raw.find_all('tr')

    ABL_PRD = []
    for i in tr_raw:
        i = str(i)
        if "교시" in i:
            pos = i.find("교시")
            ABL_PRD.append(i[pos - 2:pos - 1])

    return pgdata_raw

#incomplete / might be able to be improved
def getmyapp(usr_info):
    pgdata_raw = gettdyapp(usr_info)
    slflrn_found = {}

    if ABL_PRD:
        btnchk = pgdata_raw.select_one('#main-dashboard > div:nth-child(2) > div:nth-child(1) > div > div > div.custom-list.mt-3 > table > tbody > tr:nth-child(1) > td.border-left-0 > button')

    else:
        return slflrn_found

    if ALLAPP_BTN_DISABLED in btnchk:
        blocked_mod = True
    else:
        blocked_mod = False

    # for raw_str in element_raw:
    #     pos1 = raw_str.find('교시')
    #     pos2 = raw_str.find('(')
    #     pos3 = raw_str.find('deleteSelfLrn')
    #     pos4 = raw_str.find('" title="신청취소"')
    #     pos5 = raw_str.find(') 취소')

    print()

    if blocked_mod:
        for period in ABL_PRD:
            tdp = 2 if period != "1" else 3
            clsrm_raw = pgdata_raw.select_one(f'#main-dashboard > div:nth-child(2) > div:nth-child(1) > div > div > div.custom-list.mt-3 > table > tbody > tr:nth-child({period}) > td:nth-child({tdp}) > span').get_text()
            clsrm_pos = clsrm_raw.find("(")
            clsrm = clsrm_raw[:clsrm_pos-1]
            serial = ""
            grnt_raw = tidy(pgdata_raw.select_one(f'#main-dashboard > div:nth-child(2) > div:nth-child(1) > div > div > div.custom-list.mt-3 > table > tbody > tr:nth-child({period}) > td:nth-child({tdp+1})').get_text())

            if grnt_raw == '승인':
                granted = True
            else:
                granted = False

            slflrn_found[period] = {
                'clsrm': clsrm,
                'serial': serial,
                'granted': granted,
            }

    else:
        print("YEE")



    return slflrn_found

def gettcrlst(usr_info):
    usr_data = {
        "id": usr_info['id'],
        "password": usr_info['pw'],
    }

    with req.session() as sess:
        sess.post(SIGNIN_URL, data=usr_data)
        req = sess.get(TCR_REQ_URL)
        res = req.content.decode('utf-8')

        site_data = BeautifulSoup(res, 'html.parser')

        tcr = {}
        for element in site_data.find_all('option'):
            if element['value']:
                tcr[element.get_text()] = element['value']

        tcr['지도교사없음'] = ''

    TCR_ID = tcr

    return tcr

def getclsrmdata(usr_info, period, department):
    if not period in ABL_PRD:
        return #HERE!HERE


def register(uid, data):
    for i in ENCRYPT_ITEM:
        data[i] = encrypt(data[i])

    db.child('users').child(uid).child('info').set(data)

def register_man():
    usr_data = {"ud": datetime.today().year}

    print(">> STEP 1 of 3 << : Entering ID and PW")

    while True:
        usr_data['id'] = input("ID: ")

        uidlst = db.child("users").get().val()
        if uidlst:
            try:
                for i in uidlst:
                    comp_id = decrypt(uidlst[i]['info']['id'])
                    if usr_data['id'] == comp_id:
                        raise alreadyRegisteredErr
            except alreadyRegisteredErr:
                print("This ID was already registered (uid:" + i + ").")
                continue

        usr_data['pw'] = input("PW: ")

        while True:
            loginYN = input("Can I sign in with the ID/PW to analyze additional info? ([y]es / [n]o): ")
            if loginYN == 'Y' or loginYN == 'y':
                print("Approved. Signing in... ", end="")
                break
            elif loginYN == 'N' or loginYN == 'n':
                print("\nDeclined. Terminating function")
                return
            else:
                print("\nInvalid input. Please try again.")
                continue

        try:
            pgdata_raw = crlsitedata(usr_data['id'], usr_data['pw'])
        except signinFailErr:
            print("\n\nInvalid ID or PW. Try again.")
            continue

        break

    usr_info = getinfo(pgdata_raw)
    print("success", end="\n\n")

    print(">> STEP 2 of 3 << : Verifying personal info")

    print("Automatically detected following info.")
    while True:
        print("name: " + usr_info['name'])
        print("sid : " + str(usr_info['sid']), end="\n\n")
        autoUID = input("Are those datas are valid? ([y]es / [n]o): ")
        if autoUID == 'Y' or autoUID == 'y':
            print("Approved. Saving... ", end="")
            break
        elif autoUID == 'N' or autoUID == 'n':
            print("\nPlease enter new info.")

            while True:
                usr_info['name'] = input("name: ")
                try:
                    usr_info['sid'] = int(input("sid: "))
                except ValueError:
                    print("\nWrong type of sid. Please try again.")
                    continue

                if usr_info['sid'] // 1000 < 0 or usr_info['sid'] // 1000 > 3:
                    print("\nWrong type of sid. Please try again.")
                    continue

                print("\nYou entered those info.")
                break
            continue
        else:
            print("\nInvalid input. Please try again.")
            continue

    for i in usr_info:
        usr_data[i] = usr_info[i]

    print("success", end="\n\n")

    print(">> STEP 3 of 3 << : Allocating UID")

    uid = freeUid()
    while True:
        autoUID = input("Do you want us to assign your uid randomly? ([y]es / [n]o): ")
        if autoUID == 'Y' or autoUID == 'y':
            break
        elif autoUID == 'N' or autoUID == 'n':
            print("\nDeclined. Enter your own uid.")

            while True:
                uid = input("own UID: ").zfill(6)

                uidchk = db.child('users').child(uid).get().val()
                if uidchk:
                    print("\nEntered UID("+uid+") is already in use. Please enter another UID.")
                    continue

                break
        else:
            print("\nInvalid input. Please try again.")
            continue

        break

    print("UID '" + str(uid) + "' assigned to you.", end="\n\n")
    print("Encrypting and registering infos to server... ", end="")

    register(uid, usr_data)

    print("success", end="\n\n")
    print('===[register_man process has ended]===', end="\n\n\n")

def apply(usr_info, data):
    usr_class = usr_info['sid'] // 100

    usr_data = {
        "id": usr_info['id'],
        "password": usr_info['pw'],
    }

    with req.session() as sess: #cchtcr, clsrm, period를 가진 dictionary 여러 개를 가진 리스트 입력
        res = sess.post(SIGNIN_URL, data=usr_data)
        pgdata_raw = BeautifulSoup(res.content.decode("utf-8"), "html.parser")
        pgdata_usr = tidy(pgdata_raw.li.get_text())

        std_pos = usr_data.find('번')
        name_crwl = tidy(pgdata_usr[std_pos+2:std_pos+5])

        if name_crwl != usr_info['name']:
            raise signinFailErr

        result = {}

        ## Add code for reading my apply list
        ## and save them to a dictionary 'myapp'

        myapp = getmyapp(usr_info['id'], usr_info['pw'])

        for case in data:
            if not case['period'] in myapp:
                result[case['period']] = -1 # Fail - already applied on the period
                continue

            if not case['period'] in ABL_PRD:
                result[case['period']] = -2  # Fail - no such period
                continue

            req_url = APPLY_URL + datetime.now().strftime("%Y%m%d") + "&lrnPd=" + case['period']

            form_data = {
                "clssrmId": CLSSRM_ID[case['clsrm']],
                "roomTcherId": TCR_ID[HMRM_TCR[usr_class]],
                "cchTcherId": TCR_ID[case['cchtcr']],
            }

            req = sess.post(req_url, data=form_data)
            res = json.loads(req.content.decode("utf-8"))

            if res['result']['success'] == True:
                result[case['period']] = res['slrnNo'] #Success!
            else:
                result[case['period']] = 0 #Fail - room is full

    #returns dictionary that has period as key and successity as value
    return result

def cancel(usr_info, serial):
    if type(serial) == int:
        serial = str(serial)

    usr_data = {
        "id": usr_info['id'],
        "password": usr_info['pw'],
    }

    with req.session() as sess:
        res = sess.post(SIGNIN_URL, data=usr_data)
        pgdata_raw = BeautifulSoup(res.content.decode("utf-8"), "html.parser")
        pgdata_usr = tidy(pgdata_raw.li.get_text())

        std_pos = usr_data.find('번')
        name_crwl = tidy(pgdata_usr[std_pos+2:std_pos+5])

        if name_crwl != usr_info['name']:
            raise signinFailErr

        cncl_res_raw = sess.post(CANCEL_URL + serial)
        cncl_res = json.loads(cncl_res_raw.content.decode("utf-8"))

        if cncl_res['result']['success'] == True:
            return True
        else:
            return False

#print(getmyapp('000000'))

crlsitedata('enc2586', 'rhkgkrrh1!')