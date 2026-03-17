from bs4 import BeautifulSoup
import requests, json, pytz
from datetime import datetime, timezone, timedelta

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
            'S': 'down'
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

        return data
        