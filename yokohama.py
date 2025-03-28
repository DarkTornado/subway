from bs4 import BeautifulSoup
import requests, json, pytz
from datetime import datetime, timezone, timedelta

class Yokohama:
    
    def get_data(self, lineId):  # https://navi.hamabus.city.yokohama.lg.jp/koutuu/smart/top/Top?window=trainLocation
        lines = {
            'B': 'blue-line',
            'G': 'green-line'
        }

        url = 'https://yokohama.train-location.transfer.navitime.biz/' + lines[lineId] + '/locations?lang=ja&format=json'
        response = requests.get(url)
        json = response.json()

        data = []
        
        dests = {
            '湘南台行': '쇼난다이',
            'あざみ野行': '아자미노',
            '新羽行': '닛파',
            '踊場行': '오도리바',

            '中山行':'나카야마',
            '日吉行': '히요시'
        }

        for datum in json['trains']:
            pos = datum['position_id']
            index = int(pos / 2)

            ud = 'up'  #상/하행 반대로 줌. 남쪽 방향이 상행이라서 그런 듯
            if datum['direction'] == 'up': ud = 'dn'

            status = '도착'
            if pos % 2 == 0:
                if ud == 'up': index = index - 1
                status = '접근'
            
            dest = dests.get(datum['destination'])
            if dest == None: dest = datum['destination']

            data.append({
                'no': datum['train_id'],
                'index': index,
                'dest': dest,
                'status': status,
                'ud': ud
            })

        result = []
        stns = self.get_stn_list(lineId)
        for i in range(0, len(stns)):
            stn = stns[i]
            result.append({
                'stn': stn['ko'] + ' (' + stn['ja'] + ')',
                'up': [],
                'dn': []
            })

            for train in data:
                if train['index'] == i:
                    result[i][train['ud']].append({
                        'no': train['no'],
                        'type': '보통',
                        'status': train['status'],
                        'dest': train['dest']
                    })

        return result


    def get_stn_list(self, lineId):
        if lineId == 'B':
            return [{'ko':'쇼난다이','ja':'湘南台'},{'ko':'시모이다','ja':'下飯田'},{'ko':'타테바','ja':'立場'},{'ko':'나카다','ja':'中田'},{'ko':'오도리바','ja':'踊場'},{'ko':'토츠카','ja':'戸塚'},{'ko':'마이오카','ja':'舞岡'},{'ko':'시모나가야','ja':'下永谷'},{'ko':'카미나가야','ja':'上永谷'},{'ko':'코난츄오','ja':'港南中央'},{'ko':'카미오오카','ja':'上大岡'},{'ko':'구묘지','ja':'弘明寺'},{'ko':'마이타','ja':'蒔田'},{'ko':'요시노쵸','ja':'吉野町'},{'ko':'반도바시','ja':'阪東橋'},{'ko':'이세자키쵸자마치','ja':'伊勢佐木長者町'},{'ko':'칸나이','ja':'関内'},{'ko':'사쿠라기초','ja':'桜木町'},{'ko':'타카시마쵸','ja':'高島町'},{'ko':'요코하마','ja':'横浜'},{'ko':'미츠자와시모쵸','ja':'三ツ沢下町'},{'ko':'미츠자와카미쵸','ja':'三ツ沢上町'},{'ko':'카타쿠라쵸','ja':'片倉町'},{'ko':'키시네코엔','ja':'岸根公園'},{'ko':'신요코하마','ja':'新横浜'},{'ko':'키타신요코하마','ja':'北新横浜'},{'ko':'닛파','ja':'新羽'},{'ko':'나카마치다이','ja':'仲町台'},{'ko':'센터미나미','ja':'センター南'},{'ko':'센터키타','ja':'センター北'},{'ko':'나카가와','ja':'中川'},{'ko':'아자미노','ja':'あざみ野'}]
        if lineId == 'G':
            return [{'ko':'나카야마','ja':'中山'},{'ko':'카와와쵸','ja':'川和町'},{'ko':'츠즈키후레아이노오카','ja':'都筑ふれあいの丘'},{'ko':'센터미나미','ja':'センター南'},{'ko':'센터키타','ja':'センター北'},{'ko':'키타야마타','ja':'北山田'},{'ko':'히가시야마타','ja':'東山田'},{'ko':'타카타','ja':'高田'},{'ko':'히요시혼쵸','ja':'日吉本町'},{'ko':'히요시','ja':'日吉'}]
        return []
