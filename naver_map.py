from bs4 import BeautifulSoup
import requests, json, pytz

class NaverMap:
    
    @staticmethod
    def get_data(stns, lineId):
        data = []

        # 하행
        url = 'https://pts.map.naver.com/end-subway/api/realtime/location/subway/integrated?direction=0&routeId=' + lineId + '&caller=pc_web&lang=ko'
        response = requests.get(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36'
        })
        json = response.json()
        for e in json:
            index = e['stationSeq']
            status = ['접근', '도착', '출발'][int(e['statusCd'])]
            if e['statusCd'] != e['movingStatus']:
                if e['statusCd'] == '2' and e['movingStatus'] == '4':
                    status = '도착'
                    index += 1
                elif e['statusCd'] == '2' and e['movingStatus'] == '3':
                    status = '접근'
                    index += 1
                elif e['statusCd'] == '1' and e['movingStatus'] == '2':
                    status = '출발'
                elif e['statusCd'] == '1' and e['movingStatus'] == '3':
                    status = '접근'
                    index += 1
                elif e['statusCd'] == '1' and e['movingStatus'] == '4':
                    status = '도착'
                    index += 1
                else :
                    status = '???'
            data.append({
                'no': e['trainNo'][0]['trainNo'],
                'index': index,
                'dest': e['heading'],
                'status': status,
                'ud': 'dn',
            })

        # 상행
        url = 'https://pts.map.naver.com/end-subway/api/realtime/location/subway/integrated?direction=1&routeId=' + lineId + '&caller=pc_web&lang=ko'
        response = requests.get(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36'
        })
        json = response.json()
        for e in json:
            index = e['stationSeq']
            status = ['접근', '도착', '출발'][int(e['statusCd'])]
            if e['statusCd'] != e['movingStatus']:
                if e['statusCd'] == '2' and e['movingStatus'] == '4':
                    status = '도착'
                    index -= 1
                elif e['statusCd'] == '2' and e['movingStatus'] == '3':
                    status = '접근'
                    index -= 1
                elif e['statusCd'] == '1' and e['movingStatus'] == '2':
                    status = '출발'
                elif e['statusCd'] == '1' and e['movingStatus'] == '3':
                    status = '접근'
                    index -= 1
                elif e['statusCd'] == '1' and e['movingStatus'] == '4':
                    status = '도착'
                    index -= 1
                else :
                    status = '???'
            data.append({
                'no': e['trainNo'][0]['trainNo'],
                'index': index,
                'dest': e['heading'],
                'status': status,
                'ud': 'up',
            })

        result = []
        for i in range(0, len(stns)):
            stn = stns[i]
            result.append({
                'stn': stn,
                'up': [],
                'dn': []
            })

            for train in data:
                if train['index'] == i:
                    result[i][train['ud']].append({
                        'no': train['no'],
                        'type': '일반',
                        'status': train['status'],
                        'dest': train['dest']
                    })

        return result