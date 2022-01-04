from functions import *

# import requests as req
# from bs4 import BeautifulSoup
# from datetime import datetime
# import re
# import json

# # const definition
# SIGNIN_URL = "http://academic.petapop.com/sign/actionLogin.do"
# APPLY_URL = "http://academic.petapop.com/self/requestSelfLrn.do"
# CANCEL_URL = "http://academic.petapop.com/self/deleteSelfLrn.do"
# TCRINFO_URL = "http://academic.petapop.com/self/writeSelfLrnReqst.do"
# ROOMINFO_URL = "http://academic.petapop.com/clssrm/buldDrw.do"
# SEATINFO_URL = "http://academic.petapop.com/clssrm/seatInfo.json"
# LRNSTAT_URL = "http://academic.petapop.com/self/mainSelfLrnReqst.do"

# BS_PROCESS = [1, 3, 4, 5, 6]

# numbers = re.compile('\d')


# def tidy(str):
#     strList = str.split()
#     result = " ".join(strList)

#     return result

# # 성공 시 시리얼번호 return
# # 실패 시 음수 return


# def apply(id, pw, rtcr, ctcr, room, pd, date, act, cont):
#     usr_data = {
#         "id": id,
#         "password": pw,
#     }

#     form_data = {
#         "actCn": cont,
#         "actCode": act,
#         "cchTcherId": ctcr,
#         "clssrmId": room,
#         "lrnPd": pd,
#         "roomTcherId": rtcr,
#         "sgnId": date,
#     }

#     with req.session() as sess:
#         res = sess.post(SIGNIN_URL, data=usr_data)
#         pgdata_raw = BeautifulSoup(res.content.decode('utf-8'), "html.parser")
#         login_chk = tidy(pgdata_raw.li.get_text())

#         if login_chk == "선생님은 가입해주세요.":
#             return -1

#         res = sess.post(APPLY_URL, data=form_data)
#         response = json.loads(res.content.decode('utf-8'))

#         if response['result']['success'] == True:
#             return response['slrnNo']

#         else:
#             return -2

# # 성공 시 True return
# # 실패 시 음수 return


# def cancel(id, pw, serial):
#     usr_data = {
#         "id": id,
#         "password": pw,
#     }

#     form_data = {
#         "slrnNo": serial,
#     }

#     with req.session() as sess:
#         res = sess.post(SIGNIN_URL, data=usr_data)
#         pgdata_raw = BeautifulSoup(res.content.decode('utf-8'), "html.parser")
#         login_chk = tidy(pgdata_raw.li.get_text())

#         if login_chk == "선생님은 가입해주세요.":
#             return -1

#         res = sess.post(CANCEL_URL, data=form_data)
#         response = json.loads(res.content.decode('utf-8'))

#         if response['result']['success'] == True:
#             return True

#         else:
#             return -2

# # 특정 특별실 잔여인원 return
# # 실패 시 음수 return


# def seatinfo(id, pw, rmid, pd, date):
#     usr_data = {
#         "id": id,
#         "password": pw,
#     }

#     form_data = {
#         "searchSgnId": date,
#         "searchLrnPd": pd,
#         "clssrmId": rmid,
#     }

#     with req.session() as sess:
#         res = sess.post(SIGNIN_URL, data=usr_data)
#         pgdata_raw = BeautifulSoup(res.content.decode('utf-8'), "html.parser")
#         login_chk = tidy(pgdata_raw.li.get_text())

#         if login_chk == "선생님은 가입해주세요.":
#             return -1

#         res = sess.post(SEATINFO_URL, data=form_data)
#         response = json.loads(res.content.decode('utf-8'))

#         if response['result']['success'] == True:
#             return response['data']['seatCo']-response['data']['stdntCnt']

#         else:
#             return -2

# # {'선생님': 'id'} dict return
# # 실패 시 음수 return


# def getTeacherInfo(id, pw):
#     usr_data = {
#         "id": id,
#         "password": pw,
#     }

#     with req.session() as sess:
#         res = sess.post(SIGNIN_URL, data=usr_data)
#         pgdata_raw = BeautifulSoup(res.content.decode('utf-8'), "html.parser")
#         login_chk = tidy(pgdata_raw.li.get_text())

#         if login_chk == "선생님은 가입해주세요.":
#             return -1

#         reqest = sess.get(TCRINFO_URL)
#         res = reqest.content.decode('utf-8')

#         site_data = BeautifulSoup(res, 'html.parser')

#         tcr = {}
#         for element in site_data.find_all('option'):
#             if element['value']:
#                 tcr[element.get_text()] = element['value']

#         if not tcr:
#             return -2

#         tcr['지도교사없음'] = ''
#         return tcr


# # {'이름': {'floor': '층', 'maxppl': '최대인원', 'tcher': '담당교사', 'id': '교샤id'}} dict return
# # 실패 시 음수 return
# def getRoomInfo(id, pw):
#     usr_data = {
#         "id": id,
#         "password": pw,
#     }

#     with req.session() as sess:
#         res = sess.post(SIGNIN_URL, data=usr_data)
#         pgdata_raw = BeautifulSoup(res.content.decode('utf-8'), "html.parser")
#         login_chk = tidy(pgdata_raw.li.get_text())

#         if login_chk == "선생님은 가입해주세요.":
#             return -1

#         res = sess.get(ROOMINFO_URL)
#         response = BeautifulSoup(
#             res.content.decode('utf-8'), "html.parser")

#         rawlst = response.select(
#             'div > div > div > div.data-list.custom-list > table > tbody > tr')

#         rmlst = {}
#         for rawhtml in rawlst:
#             datalst = rawhtml.select('td')
#             name = datalst[1].get_text()
#             if not ('삭제' in name):
#                 rmlst[name] = {
#                     "floor": datalst[0].get_text(),
#                     "maxppl": tidy(datalst[3].get_text()),
#                     "tcher": datalst[2].get_text(),
#                     "id": datalst[4].select_one('div > input')['value'],
#                 }

#         if not rmlst:
#             return -2

#         return rmlst

# # 신청 현황 dictionary return
# # 실패 시 음수 return

# def isCredentialValid(id, pw):
#     usr_data = {
#         "id": id,
#         "password": pw,
#     }

#     with req.session() as sess:
#         res = sess.post(SIGNIN_URL, data=usr_data)
#         pgdata_raw = BeautifulSoup(res.content.decode('utf-8'), "html.parser")
#         login_chk = tidy(pgdata_raw.li.get_text())

#         if login_chk == "선생님은 가입해주세요.":
#             return False
#         else:
#             return True

###################################################
################### CODE START ####################
###################################################

# 파이썬에서 직접 만든 모듈을 불러오기가 힘들군요
# from functions import * 하면 제 컴퓨터에서는 되는데
# 설정에 따라 다른 컴퓨터에서 안 되는 경우가 많습니다
# 호환성을 위해 조금 파일이 커지더라도
# 이 프로그램 속에 해당 함수들을 포함하기로 결정했습니다

print("[slflrn-requester-legacy]")
print()
print("환영합니다. 이 프로그램은 자습 신청을 파이썬으로 하고자 만든 프로그램입니다.")
print("이 프로그램을 그대로 사용하여 자습신청을 할 수도 있지만,")
print("functions.py 모듈을 사용하여 직접 자동화 코드를 짜실 수도 있습니다.")
print()

print()
print("<< 사용자 정보 등록 단계 >>")

while True:
    id = input("ID: ")
    pw = input("PW: ")

    print()
    if not isCredentialValid(id, pw):
        print("정보가 유효하지 않습니다. 다시 입력해주십시오.")
        continue  
    
    user_data = {
        'id': id,
        'pw': pw
    }

    print("교실 및 선생님 데이터를 받아오는 중... ", end="")
    classList = getRoomInfo(id, pw)
    teacherList = getTeacherInfo(id, pw)

    if type(classList) == int or type(teacherList) == int:
        print("실패")
        print("로그인 정보는 유효하지만 문제가 발생했습니다. 나중에 다시 시도하세요.")
        break
    else:
        print("성공")
        print()

    print("<< 신청 서식 작성 단계 >>")

    while True:
            print("담임 선생님의 성함을 입력해주십시오. 'ls'를 입력해 전체 리스트를 볼 수 있습니다.")
            homeroomTeacher = input("담임교사: ")

            if homeroomTeacher == "ls":
                for teacher in teacherList.keys():
                    print(f"'{teacher}'", end=" ")
                print()
                print()
                continue
            elif homeroomTeacher not in teacherList.keys():
                print("그런 선생님은 없습니다.")
                print("'ls'를 입력해 정확한 선생님 성함을 확인하세요.")
                print()
                print()
                continue
            else:
                print()
                homeroomTeacherSerial = teacherList[homeroomTeacher]
                break

    while True:
        print("교실정보를 입력해주십시오. 'ls'를 입력해 전체 리스트를 볼 수 있습니다.")
        classInput = input("교실(교실명 전체): ")

        if classInput == "ls":
            for name in classList.keys():
                print(f"'{name}'", end=" ")
            print()
            print()
            continue
        elif classInput not in classList.keys():
            print("그런 교실은 없습니다.")
            print("'ls'를 입력해 정확한 교실명을 확인하세요.")
            print()
            print()
            continue

        else:
            classData = classList[classInput]
            classSerial = classData['id']
            roomTeacher = classData['tcher']
            roomTeacherSerial = None

        print()
            
        if roomTeacher in teacherList.keys():
            print(f"기본 지도교사는 {roomTeacher} 선생님입니다.")
            defaultRoomTeacherBool = input(f"이 분을 지도교사로 선택하시겠습니까? [y/n]: ")
            print()

            if defaultRoomTeacherBool == "y" or defaultRoomTeacherBool == "":
                print(f"{roomTeacher} 선생님이 지도교사입니다.")
                roomTeacherSerial = teacherList[roomTeacher]
            elif defaultRoomTeacherBool == "n":
                print("수동으로 선택하겠습니다.")

            print()

        while True:          
            if roomTeacherSerial == None:
                print("지도교사 선생님의 성함을 입력해주십시오. 'ls'를 입력해 전체 리스트를 볼 수 있습니다.")
                roomTeacher = input("지도교사: ")

                if roomTeacher == "ls":
                    for teacher in teacherList.keys():
                        print(f"'{teacher}'", end=" ")
                    print()
                    continue
                elif roomTeacher not in teacherList.keys():
                    print("그런 선생님은 없습니다.")
                    print("'ls'를 입력해 정확한 선생님 성함을 확인하세요.")
                    print()
                    print()
                    continue
                else:
                    roomTeacherSerial = teacherList[roomTeacher]
                    break
            else:
                break

        print()

        print("사용 이유가 무엇인가요?")
        reason = input("이유: ")

        print()
        print("<< 신청 단계 >>")
        
        while True:
            print("몇 교시에 신청하고 싶으신가요?")
            try:
                period = int(input("교시: "))
            except ValueError:
                print("잘못된 교시 형식입니다. 숫자만 입력하세요.")
                print()
                continue

            form_data = {
                'rtcr': homeroomTeacherSerial,
                'ctcr': roomTeacherSerial,
                'room': classSerial,
                'pd': str(period),
                'act': "ACT999",
                'cont': reason,
                'date': datetime.now().strftime("%Y%m%d")
            }
            
            print(f"{period}교시에 신청중... ", end="")
            serial = apply(**user_data, **form_data)
            serial = 9999

            if serial <= 0:
                print("실패했습니다. 다시 시도해보세요.")
                print()
                continue
            else:
                print("성공")
                print()
                print(f"{period}교시에 {classInput}(으)로 신청되었습니다.")
                print(f"고유번호는 {serial}입니다.")
                print("고유번호를 통해 자습을 취소할 수 있습니다. 번호를 숙지하십시오.")
            
            moreApply = input("이 교실로 다른 교시에 신청하시겠습니까? [y/n]: ")
            if moreApply == "y" or moreApply == "":
                print()
                continue
            else:
                print(f"{classInput}에 대한 신청 단계를 종료합니다.")
                print()
                print("다른 교실로 신청하거나 [Ctrl+C]를 통해 프로그램을 종료하세요.")
                print()
                break