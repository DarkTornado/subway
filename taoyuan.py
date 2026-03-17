import requests, json

class Taoyuan:
    
    def get_data(self, lineName):  # https://www.tymetro.com.tw/tymetro-new/kr/_pages/travel-guide/dynamictraininfo.php
        url = 'https://www.tymetro.com.tw/tymetro-new/kr/_pages/travel-guide/getimmediatestatus_cache.php'
        response = requests.post(url)
        json = response.json()

        types = {
            'COM': '보통',
            'EXP': '직통'
        }
        dests = {
            'A1': '타이베이역',
            'A12': '공항 터미널 1',
            'A13': '공항 터미널 2',
            'A22': '라오제시'
        }
        uds = {
            'N': 'up',
            'S': 'dn'
        }

        data = []
        for datum in json['Payload']:
            status = '도착'
            stn = datum['location']
            if '-' in stn:
                stn = stn.split('-')
                if stn[0] != stn[1]: status = '접근'
                stn = stn[1]
            

            data.append({
                'no': datum['train_no'],
                'type': types[datum['CAR_TYPE']],
                'stn': stn,
                'dest': dests[datum['DESTINATION']],
                'status': status,
                'ud': uds[datum['direction']]
            })

        result = []
        stns = [{'s': '타이베이역 (台北車站)', 'id': 'A01'}, {'s': '싼충 (三重)', 'id': 'A02'}, {'s': '신베이산업단지 (新北產業園區)', 'id': 'A03'}, {'s': '신좡부도심 (新莊副都心)', 'id': 'A04'}, {'s': '타이산 (泰山)', 'id': 'A05'}, {'s': '타이산구이허 (泰山貴和)', 'id': 'A06'}, {'s': '국립타이완 체육대학 (體育大學)', 'id': 'A07'}, {'s': '창겅병원 (長庚醫院)', 'id': 'A08'}, {'s': '린커우 (林口)', 'id': 'A09'}, {'s': '산비 (山鼻)', 'id': 'A10'}, {'s': '컹커우 (坑口)', 'id': 'A11'}, {'s': '공항 터미널 1 (機場第一航廈)', 'id': 'A12'}, {'s': '공항 터미널 2 (機場第二航廈)', 'id': 'A13'}, {'s': '공항호텔 (機場旅館)', 'id': 'A14a'}, {'s': '다위안 (大園)', 'id': 'A15'}, {'s': '헝산 (橫山)', 'id': 'A16'}, {'s': '링항 (領航)', 'id': 'A17'}, {'s': '타오위안 고속철도역 (高鐵桃園站)', 'id': 'A18'}, {'s': '타오위안 체육공원 (桃園體育園區)', 'id': 'A19'}, {'s': '싱난 (興南)', 'id': 'A20'}, {'s': '환베이 (環北)', 'id': 'A21'}, {'s': '라오제시 (老街溪)', 'id': 'A22'}]
        for i in range(0, len(stns)):
            stn = stns[i]
            result.append({
                'stn': stn['s'],
                'up': [],
                'dn': []
            })

            for train in data:
                if train['stn'] == stns[i]['id']:
                    result[i][train['ud']].append({
                        'no': train['no'],
                        'type': train['type'],
                        'status': train['status'],
                        'dest': train['dest']
                    })

        return result
