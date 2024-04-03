from fastapi import FastAPI, Response
from typing import Optional
import requests, time, json, os, pytz
from datetime import datetime
from topis import Topis
from timetable import TrainLocation

app = FastAPI()

@app.get("/subway/seoul")
def seoul(response: Response, lineId: Optional[str] = None):
    response.headers['Access-Control-Allow-Origin'] = '*'
    lineNames = {
        '1': '1호선', # 서울교통공사 홈페이지 크롤링으로 급행 순간이동 버그 수정
        '2': '2호선',
        '3': '3호선',
        '4': '4호선', # 서울교통공사 홈페이지 크롤링으로 급행 순간이동 버그 수정 및 진접선 구간 구현
        '5': '5호선',
        '6': '6호선',
        '7': '7호선',
        '8': '8호선',
        '9': '9호선',
        '101': '경의중앙선', # 급행 순간이동 버그 수정 필요
        '102': '수인분당선', # 급행 순간이동 버그 수정 필요
        '103': '신분당선',
        '104': '경춘선', # 급행 순간이동 버그 수정 필요
        '105': '경강선', # 성남역 정보 없음
        '106': '우이신설선',
        '107': '서해선',
        '108': '공항철도', # 사실 공항철도 홈페이지에도 열차 위치 정보가 있으나, 행선지가 안뜸
        '151': 'GTX-A'
        # '109': '신림선',  # 곧 지원할 것으로 추정. 관련 협조요청 등이 있음
        # '110': '의정부경전철',  # 시간표 기반으로 구축
        # '111': '용인경전철',  # 에버라인 홈페이지 크롤링
        # '112': '김포도시철도',  # 시간표 기반으로 구축
        # '201': '인천1호선',  # https://darktornado.github.io/ictr/
        # '202': '인천2호선'   #   "
    }

    # 서울시 Open API (1 ~ 9호선, 경의중앙선, 수인분당선, 신분당선, 경춘선, 경강선, 우이신설선, 서해선, 공항철도) + 서울교통공사 크롤링
    if lineNames.get(lineId): return {
            'isTimeTable': False,
            'data': Topis().get_data(lineNames[lineId], lineId)
        }

    # 자체 구현 시간표 기반 인천 도시철도 API (인천 1 ~ 2호선)
    if lineId == '201' or lineId == '202': return {
            'isTimeTable': True,
            'data': ictr(lineId)
        }

    # 용인경전철 홈페이지 크롤링
    if lineId == '111': return {
            'isTimeTable': False,
            'data': everline()
        }
    
    # 시간표 기반으로 열차 위치 계산
    if lineId == '109' or lineId == '110' or lineId == '112':
        stns = -1
        if lineId == '109':
            stns = ['샛강역','대방','서울지방병무청','보라매','보라매공원','보라매병원','당곡','신림','서원','서울대벤처타운','관악산']
        if lineId == '110':
            stns = ['탑석', '송산', '어룡', '곤제', '효자', '경기도청북부청사', '새말', '동오', '의정부중앙', '흥선', '의정부시청', '경전철의정부', '범골', '회룡', '발곡']
        if lineId == '112':
            stns = ['양촌', '구래', '마산', '장기', '운양', '걸포북변', '사우 (김포시청)', '풍무', '고촌', '김포공항']

        if stns != -1 : return {
            'isTimeTable': True,
            'data': TrainLocation.calc_location(lineId, stns)
        }
    
    return []


@app.get("/subway/busan")
def seoul(response: Response, lineId: Optional[str] = None):
    response.headers['Access-Control-Allow-Origin'] = '*'

    # 시간표 기반으로 열차 위치 계산
    if lineId == '1' or lineId == '2' or lineId == '3' or lineId == '4' or lineId == '101' or lineId == '102':
        stns = -1
        if lineId == '1':
            stns = ["다대포해수욕장","다대포항","낫개","신장림","장림","동매","신평","하단","당리","사하","괴정","대티","서대신","동대신","토성","자갈치","남포","중앙","부산역","초량","부산진","좌천","범일","범내골","서면","부전","양정","시청","연산","교대","동래","명륜","온천장","부산대","장전","구서","두실","남산","범어사","노포"]

        if stns != -1 : return {
            'isTimeTable': True,
            'data': TrainLocation.calc_location(lineId, stns)
        }
    
    return []

def ictr(lineId):
    line = '1'
    if lineId == '202': line = '2'
    url = 'https://api.darktornado.net/subway/ictr/info?line=' + line + '&key=sample'
    response = requests.get(url)
    data = response.json()['data']

    result = []
    for info in data:
        datum = {
            'stn': info['stn'],
            'up': [],
            'dn': []
        }
        if info['up'] == 1:
            datum['up'].append({
                'status': None,
                'type': '일반',
                'dest': info['up_terminal'],
                'no': None
            })
        if info['dn'] == 1:
            datum['dn'].append({
                'status': None,
                'type': '일반',
                'dest': info['dn_terminal'],
                'no': None
            })
        result.append(datum)

    return result

def everline():
    url = 'https://everlinecu.com/api/api009.json'
    response = requests.get(url)
    data = response.json()['data']

    result = []
    stas = ['기흥', '강남대', '지석', '어정', '동백', '초당', '삼가', '시청·용인대', '명지대', '김량장', '운동장·송담대', '고진', '보평', '둔전', '전대·에버랜드']
    for stn in stas:
        result.append({
            'stn': stn,
            'up': [],
            'dn': []
        })

    for train in data:
        ud = 'dn'
        if train['updownCode'] == '1':
            ud = 'up'
        index = int(train['StCode'].replace('Y', '')) - 110
        dest = stas[int(train['DestCode'].replace('Y', '')) - 110]
        status = '도착'
        if train['StatusCode'] == '3':
            status = '출발'
        result[index][ud].append({
            'status': status,
            'type': '일반',
            'dest': dest,
            'no': train['TrainNo']
        })

    return result
