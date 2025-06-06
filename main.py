from fastapi import FastAPI, Response
from typing import Optional
import requests, time, json, os, pytz
from datetime import datetime
from topis import Topis
from toei import Toei
from yokohama import Yokohama
from naver_map import NaverMap
# from jr_kyushu import JRK
from timetable import TrainLocation
from bs4 import BeautifulSoup

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
        '109': '신림선',  # 이 파일을 작성할 시점에 이미 관련 협조요청 등이 있었고, 2024년 7월 말에 추가된 것 확인
        '108': '공항철도', # 사실 공항철도 홈페이지에도 열차 위치 정보가 있으나, 행선지가 안뜸
        '151': 'GTX-A'
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
    if lineId == '110' or lineId == '112':
        stns = -1
        if lineId == '109':
            stns = ['샛강역','대방','서울지방병무청','보라매','보라매공원','보라매병원','당곡','신림','서원','서울대벤처타운','관악산']
        if lineId == '110':
            stns = ['탑석', '송산', '어룡', '곤제', '효자', '경기도청북부청사', '새말', '동오', '의정부중앙', '흥선', '의정부시청', '경전철의정부', '범골', '회룡', '발곡']
        if lineId == '112':
            stns = ['양촌', '구래', '마산', '장기', '운양', '걸포북변', '사우 (김포시청)', '풍무', '고촌', '김포공항']

        if stns != -1 : return {
            'isTimeTable': True,
            'data': TrainLocation.calc_location('seoul_' + lineId, stns)
        }
    
    return []

@app.get("/subway/busan")
def busan(response: Response, lineId: Optional[str] = None):
    response.headers['Access-Control-Allow-Origin'] = '*'

    # 네이버 지도에서 실시간 정보 뜯어오기
    # 2025년 5월 8일부터 네이버 지도에서 부산 지하철 실시간 위치 지원하기 시작
    if lineId == '1' or lineId == '2' or lineId == '3' or lineId == '4':
        stns = -1
        if lineId == '1':
            stns = ['다대포해수욕장','다대포항','낫개','신장림','장림','동매','신평','하단','당리','사하','괴정','대티','서대신','동대신','토성','자갈치','남포','중앙','부산역','초량','부산진','좌천','범일','범내골','서면','부전','양정','시청','연산','교대','동래','명륜','온천장','부산대','장전','구서','두실','남산','범어사','노포']
        if lineId == '2':
            stns = ['장산', '중동', '해운대', '동백', '벡스코', '센텀시티', '민락', '수영', '광안', '금련산', '남천', '경성대·부경대', '대연', '못골', '지게골', '문현', '국제금융센터·부산은행', '전포', '서면', '부암', '가야', '동의대', '개금', '냉정', '주례', '감전', '사상', '덕포', '모덕', '모라', '구남', '구명', '덕천', '수정', '화명', '율리', '동원', '금곡', '호포', '증산', '부산대양산캠퍼스', '남양산', '양산']
        if lineId == '3':
            stns = ['수영', '망미', '배산', '물만골', '연산', '거제', '종합운동장', '사직', '미남', '만덕', '남산정', '숙등', '덕천', '구포', '강서구청', '체육공원', '대저']
        if lineId == '4':
            stns = ['미남', '동래', '수안', '낙민', '충렬사', '명장', '서동', '금사', '반여농산물시장', '석대', '영산대', '윗반송', '고촌', '안평']

        return {
            'isTimeTable': False,
            'data': NaverMap.get_data(stns, '7000'+lineId)
        }
    

    # 시간표 기반으로 열차 위치 계산
    if lineId == '101' or lineId == '102':
        stns = -1
        if lineId == '101':
            stns = ['부전', '거제해맞이', '거제', '교대', '동래', '안락', '부산원동', '재송', '센텀', '벡스코', '신해운대', '송정', '오시리아', '기장', '일광', '좌천', '월내', '서생', '남창', '망양', '덕하', '개운포', '태화강']
        if lineId == '102':
           stns = ['사상', '괘법르네시떼', '서부산유통지구', '공항', '덕두', '등구', '대저', '평강', '대사', '불암', '지내', '김해대학', '인제대', '김해시청', '부원', '봉황', '수로왕릉', '박물관', '연지공원', '장신대', '가야대']

        return {
            'isTimeTable': True,
            'data': TrainLocation.calc_location('busan_' + lineId, stns, None, 0)
        }
        
    return []

@app.get("/subway/daejeon")
def busan(response: Response, lineId: Optional[str] = None):
    response.headers['Access-Control-Allow-Origin'] = '*'

    # 시간표 기반으로 열차 위치 계산
    if lineId == '1':
        stns = ['판암', '신흥', '대동', '대전역', '중앙로', '중구청', '서대전네거리', '오룡', '용문', '탄방', '시청', '정부청사', '갈마', '월평', '갑천', '유성온천', '구암', '현충원', '월드컵경기장', '노은', '지족', '반석']
    else:
        return []

    return {
            'isTimeTable': True,
            'data': TrainLocation.calc_location('daejeon_' + lineId, stns, 0)
        }

@app.get("/subway/daegu")
def busan(response: Response, lineId: Optional[str] = None):
    response.headers['Access-Control-Allow-Origin'] = '*'

    # 시간표 기반으로 열차 위치 계산
    stns = -1
    if lineId == '1':
        stns = ['설화명곡', '화원', '대곡', '진천', '월배', '상인', '월촌', '송현', '서부정류장', '대명', '안지랑', '현충로', '영대병원', '교대', '명덕', '반월당', '중앙로', '대구역', '칠성시장', '신천', '동대구역', '동구청', '아양교', '동촌', '해안', '방촌', '용계', '율하', '신기', '반야월', '각산', '안심', '부호', '대구한의대병원', '하양']
    if lineId == '2':
        stns = ['문양', '다사', '대실', '강창', '계명대', '성서산업단지', '이곡', '용산', '죽전', '감삼', '두류', '내당', '반고개', '청라언덕', '반월당', '경대병원', '대구은행', '범어', '수성구청', '만촌', '담티', '연호', '수성알파시티', '고산', '신매', '사월', '정평', '임당', '영남대']
    if lineId == '3':
        stns = ['칠곡경대병원', '학정', '팔거', '동천', '칠곡운암', '구암', '태전', '매천', '매천시장', '팔달', '공단', '만평', '팔달시장', '원대', '북구청', '달성공원', '서문시장', '청라언덕', '남산', '명덕', '건들바위', '대봉교', '수성시장', '수성구민운동장', '어린이세상', '황금', '수성못', '지산', '범물', '용지']
    if lineId == '101':
        stns = ['구미', '사곡', '약목', '왜관', '연화', '신동', '지천', '서대구', '대구', '동대구', '고모', '가천', '경산']

    if stns != -1 : return {
        'isTimeTable': True,
        'data': TrainLocation.calc_location('daegu_' + lineId, stns, 0)
    }
    
    return []

@app.get("/subway/gwangju")
def busan(response: Response, lineId: Optional[str] = None):
    response.headers['Access-Control-Allow-Origin'] = '*'

    # 시간표 기반으로 열차 위치 계산
    if lineId == '1':
        stns = ['녹동', '소태', '학동·증심사입구', '남광주', '문화전당', '금남로4가', '금남로5가', '양동시장', '돌고개', '농성', '화정', '쌍촌', '운천', '상무', '김대중컨벤션센터', '공항', '송정공원', '광주송정역', '도산', '평동']
    else:
        return []

    return {
            'isTimeTable': True,
            'data': TrainLocation.calc_location('gwangju_' + lineId, stns, 0)
        }

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


@app.get("/subway/tokyo")
def tokyo(response: Response, lineId: Optional[str] = None):
    response.headers['Access-Control-Allow-Origin'] = '*'

    lineNames = {
        'A': 'Asakusa',
        'I': 'Mita',
        'S': 'Shinjuku',
        'E': 'Oedo',
        'SA': 'Arakawa'
    }

    # 일본 대중교통오픈테이터센터 사용
    if lineNames.get(lineId): return {
            'isTimeTable': False,
            'data': Toei().get_data(lineNames[lineId])
        }
    
    stns = -1
    
    # 시간표 기반으로 열차 위치 계산
    if lineId == 'NT':
        stns = ['닛포리', '니시닛포리', '아카도쇼갓코마에', '쿠마노마에', '아다치오다이', '오기오하시', '고야', '코호쿠', '니시아라이다이시니시', '야자이케', '토네리코엔', '토네리', '미누마다이신스이코엔']

    if lineId == 'H':
        stns = ['나카메구로','에비스','히로오','롯폰기','카미야쵸','토라노몬힐즈','카스미가세키','히비야','긴자','히가시긴자','츠키지','핫쵸보리','카야바쵸','닌교초','코덴마쵸','아키하바라','나카오카치마치','우에노','이리야','미노와','미나미센쥬','키타센쥬']
    
    if lineId == 'G':
        stns = ['시부야','오모테산도','가이엔마에','아오야마잇초메','아카사카미츠케','타메이케산노','토라노몬','신바시','긴자','쿄바시','니혼바시','미츠코시마에','칸다','스에히로쵸','우에노히로코지','우에노','이나리초','타와라마치','아사쿠사']
        stns_ja = ['渋谷','表参道','外苑前','青山一丁目','赤坂見附','溜池山王','虎ノ門','新橋','銀座','京橋','日本橋','三越前','神田','末広町','上野広小路','上野','稲荷町','田原町','浅草']
        
    if lineId == 'M':
        stns = ['오기쿠보','미나미아사가야','신코엔지','히가시코엔지','신나카노','나카노사카우에','니시신주쿠','신주쿠','신주쿠산초메','신주쿠교엔마에','요츠야산초메','요츠야','아카사카미츠케','콧카이기지도마에','카스미가세키','긴자','도쿄','오테마치','아와지초','오차노미즈','혼고산초메','코라쿠엔','묘가다니','신오츠카','이케부쿠로',
            '나카노신바시', '나카노후지미초', '호난초']
        stns_ja = ['荻窪','南阿佐ケ谷','新高円寺','東高円寺','新中野','中野坂上','西新宿','新宿','新宿三丁目','新宿御苑前','四谷三丁目','四ツ谷','赤坂見附','国会議事堂前','霞ケ関','銀座','東京','大手町','淡路町','御茶ノ水','本郷三丁目','後楽園','茗荷谷','新大塚','池袋',
            '中野新橋', '中野富士見町', '方南町']

    if lineId == 'T':
        stns = ['나카노','오치아이','타카다노바바','와세다','카구라자카','이다바시','쿠단시타','타케바시','오테마치','니혼바시','카야바쵸','몬젠나카쵸','키바','토요쵸','미나미스나마치','니시카사이','카사이','우라야스','미나미교토쿠','교토쿠','묘덴','바라키나카야마','니시후나바시']
        stns_ja = ['中野','落合','高田馬場','早稲田','神楽坂','飯田橋','九段下','竹橋','大手町','日本橋','茅場町','門前仲町','木場','東陽町','南砂町','西葛西','葛西','浦安','南行徳','行徳','妙典','原木中山','西船橋']

    if lineId == 'N':
        stns = ['메구로','시로카네다이','시로카네타카나와','아자부쥬반','롯폰기잇초메','타메이케산노','나가타쵸','요츠야','이치가야','이다바시','코라쿠엔','토다이마에','혼코마고메','코마고메','니시가하라','오지','오지카미야','시모','아카바네이와부치']
        stns_ja = ['目黒','白金台','白金高輪','麻布十番','六本木一丁目','溜池山王','永田町','四ツ谷','市ケ谷','飯田橋','後楽園','東大前','本駒込','駒込','西ケ原','王子','王子神谷','志茂','赤羽岩淵']

    if lineId == 'Y':
        stns = ['와코시','치카테츠나리마스','치카테츠아카츠카','헤이와다이','히카와다이','코타케무카이하라','센카와','카나메초','이케부쿠로','히가시이케부쿠로','고코쿠지','에도가와바시','이다바시','이치가야','코지마치','나가타쵸','사쿠라다몬','유라쿠초','긴자잇초메','신토미초','츠키시마','토요스','타츠미','신키바']
        stns_ja = ['和光市','地下鉄成増','地下鉄赤塚','平和台','氷川台','小竹向原','千川','要町','池袋','東池袋','護国寺','江戸川橋','飯田橋','市ケ谷','麴町','永田町','桜田門','有楽町','銀座一丁目','新富町','月島','豊洲','辰巳','新木場']

    if lineId == 'C':
        stns = ['요요기우에하라','요요기코엔','메이지진구마에<하라주쿠>','오모테산도','노기자카','아카사카','콧카이기지도마에','카스미가세키','히비야','니주바시마에<마루노우치>','오테마치','신오차노미즈','유시마','네즈','센다기','니시닛포리','마치야','키타센쥬','아야세','키타아야세']
        stns_ja = ['代々木上原','代々木公園','明治神宮前<原宿>','表参道','乃木坂','赤坂','国会議事堂前','霞ヶ関','日比谷','二重橋前<丸の内>','大手町','新御茶ノ水','湯島','根津','千駄木','西日暮里','町屋','北千住','綾瀬','北綾瀬']

    if lineId == 'Z':
        stns = ['시부야','오모테산도','아오야마잇초메','나가타쵸','한조몬','쿠단시타','진보초','오테마치','미츠코시마에','스이텐구마에','키요스미시라카와','스미요시','킨시쵸','오시아게<스카이트리마에>']
        stns_ja = ['渋谷','表参道','青山一丁目','永田町','半蔵門','九段下','神保町','大手町','三越前','水天宮前','清澄白河','住吉','錦糸町','押上<スカイツリー前>']

    if lineId == 'F':
        stns = ['와코시','치카테츠나리마스','치카테츠아카츠카','헤이와다이','히카와다이','코타케무카이하라','센카와','카나메초','이케부쿠로','조시가야','니시와세다','히가시신주쿠','신주쿠산초메','키타산도','메이지진구마에<하라주쿠>','시부야']
        stns_ja = ['和光市','地下鉄成増','地下鉄赤塚','平和台','氷川台','小竹向原','千川','要町','池袋','雑司が谷','西早稲田','東新宿','新宿三丁目','北参道','明治神宮前<原宿>','渋谷']

    if stns != -1 : return {
        'isTimeTable': True,
        'data': TrainLocation.calc_location('tokyo_' + lineId, stns)
    }
    
    return []

@app.get("/subway/yokohama")
def yokohama(response: Response, lineId: Optional[str] = None):
    response.headers['Access-Control-Allow-Origin'] = '*'
    
    # 일본 대중교통오픈테이터센터 사용
    if lineId == 'B' or lineId == 'G': return {
            'isTimeTable': False,
            'data': Yokohama().get_data(lineId)
        }
    
    return []

@app.get("/subway/fukuoka") #see https://github.com/DarkTornado/FukuokaCitySubway
def toei(response: Response, lineId: Optional[str] = None):
    response.headers['Access-Control-Allow-Origin'] = '*'

    if lineId == 'A' or lineId == 'H' or lineId == 'N' :
        url = 'http://localhost?lineCode=' + lineId
        response = requests.get(url)
        return {
            'isTimeTable': False,
            'data': response.json()
        }
    
    return []

@app.get("/subway/jrk")
def jrKyushu(response: Response, lineId: Optional[str] = None):
    response.headers['Access-Control-Allow-Origin'] = '*'

    ids = {
        '1': '2' # 가고시마 본선
    }
    
    if ids.get(lineId) == None : return []


    url = 'https://george-doredore.jrkyushu.co.jp/ip/jrqSEN' + ids[lineId] + '.html'
    # https://george-doredore.jrkyushu.co.jp/ip/jrqSEN2.html
    print(url)
    response = requests.get(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
        'Upgrade-Insecure-Requests': '1'
    })
    response.encoding = 'utf-8'

    fixed = response.text
    
    # 가고시마 본선은 <tr> 태그 두 번이나 안닫음
    fixed = fixed.replace('<tr title="KUKANH1" s', '</tr><tr title="KUKANH1" s', 1)
    fixed = fixed.replace('<tr title="KUKAN2" ', '</tr><tr title="KUKAN2" ', 1)
    

    html = BeautifulSoup(fixed, 'html.parser')

    # f = open("jrk.html", 'w')
    # f.write(response.text)
    # f.close()

    result = []
    # data = html.find('table').select('tr')[1].select('tr') # 가고시마 본선은 <tr> 태그 안닫은 듯?
    data = html.find('table').select('tr')
    
    for i in range(1, len(data)-1):
        if data[i].get('id') == None: continue

        datum = data[i].select('td')
        ups, dns = searchTrain(datum, data[i+1].select('td'))
        
        # if i+2 < data.length and data[i+2].id.strip() == '':
        #     t2 = searchTrain(data[i+2].querySelectorAll('td'), data[i+1].querySelectorAll('td'));
        #     trains.ups = trains.ups.concat(t2.ups)
        #     trains.dns = trains.dns.concat(t2.dns)
        
        result.append({
            'stn': datum[4].text.strip(),
            'up': ups,
            'dn': dns
        })
    
    
    return result

def searchTrain(data, meta):
    ups = []
    dns = []
    for i in range(0, 4):
        # print(i, data[i].attrs)

        if data[i].get('title') == None: continue
        datum = data[i] # 뭔가 반대로된 듯한 느낌
        no = datum['title'].strip()
        
        # print(str(datum).split('<br/>'))
        # print('---')
        # print(datum.contents)
        # print('-----')

        terminal = None
        name = None
        dd = datum.contents
        if len(dd) > 2: 
            terminal = dd[0].strip()[0:-1]
            if terminal == '': terminal = '???'
            if dd[2].strip() != '': name = dd[2].strip()
        if no[0] == '回':
            name = '회송'
        
        line = meta[i].text.strip()
        if line == '': line = None
        ups.append({
            'trainNo': no,
            'terminal': terminal,
            'type': name,
            'line': line
        })


    for i in range(5, 9):
        # print(i, data[i].attrs)

        if data[i].get('title') == None: continue
        datum = data[i] # 뭔가 반대로된 듯한 느낌
        no = datum['title'].strip()
        
        # print(str(datum).split('<br/>'))
        # print('---')
        # print(datum.contents)
        # print('-----')

        terminal = None
        name = None
        dd = datum.contents
        if data != '': 
            terminal = dd[0].strip()[0:-1]
            if terminal == '': terminal = '???'
            if dd[2].strip() != '': name = dd[2].strip()
        if no[0] == '回':
            name = '회송'
        
        line = meta[i].text.strip()
        if line == '': line = None
        dns.append({
            'trainNo': no,
            'terminal': terminal,
            'name': name,
            'line': line
        })
        
    return ups, dns


