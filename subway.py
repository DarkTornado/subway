from fastapi import FastAPI
from typing import Optional
import requests, time
from bs4 import BeautifulSoup

app = FastAPI()

@app.get("/subway/seoul")
def seoul(lineId: Optional[str] = None):
    lineNames = {
        '1': '1호선', # 급행 순간이동 버그 수정 필요
        '2': '2호선',
        '3': '3호선',
        '4': '4호선', # 진접선 예외처리 및 급행 순간이동 버그 수정 필요
        '5': '5호선',
        '6': '6호선',
        '7': '7호선',
        '8': '8호선',
        '9': '9호선',
        '101': '경의중앙선', # 급행 순간이동 버그 수정 필요
        '102': '수인분당선', # 급행 순간이동 버그 수정 필요
        '103': '신분당선',
        '104': '경춘선', # 급행 순간이동 버그 수정 필요
        '105': '경강선',
        '106': '우이신설선',
        '107': '서해선',
        '108': '공항철도',
        # '109': '신림선',  # 곧 지원할 것으로 추정. 관련 협조요청 등이 있음
        # '110': '의정부경전철',  # 시간표 기반으로 구축 예정
        # '111': '용인경전철',  # 에버라인 홈페이지 크롤링 예정
        # '112': '김포도시철도',  # 일처리 정말 아름답게 해서 구현 계획 없음
        # '201': '인천1호선',  # https://darktornado.github.io/ictr/
        # '202': '인천2호선'
    }

    if lineNames.get(lineId): return topis(lineNames[lineId], lineId)

    return []

def topis(lineName, lineId): # https://data.seoul.go.kr/dataList/OA-12601/A/1/datasetView.do
    key = '안알랴줌'
    url = 'http://swopenapi.seoul.go.kr/api/subway/' + key + '/json/realtimePosition/0/141/' + lineName
    response = requests.get(url)
    json = response.json()
    if not json.get('realtimePositionList'): 
        result = []
        stns = get_stn_list(lineId)
        for stn in stns:
            result.append({
                'stn': stn['stn'],
                'up': [],
                'dn': []
            })
        return result
        
    json = json['realtimePositionList']
    # return json

    statuses = ['접근', '도착', '출발', '접근'] # 진입, 도착, 출발, 전역출발
    types = ['일반', '급행', '직동', None, None, None, None, '특급']
    data = {}
    for datum in json:
        if lineId == '2': datum = line2_fix(datum)
        if lineId == '6': datum = line6_fix(datum)
        if lineId == '106': datum = lineUI_fix(datum)
        if lineId == '107': datum = lineW_fix(datum)
        if lineId == '108': datum = lineA_fix(datum)

        # 동일한 열차가 두 번 표시되는 버그 수정용. 정보 수집 시점도 함께 오니, 가장 최신 시점 정보만 사용
        # 10월 13일에 지속적으로 모니터링하겠다고 하더니, 하고 있는지 모르겠음
        no = datum['trainNo']
        if data.get(no) and data[no]['time'] > datum['recptnDt']: continue
        
        data[no] = {
            'stn': datum['statnNm'],
            'stnId': datum['statnId'],
            'updn': 'up' if datum['updnLine'] == '0' else 'dn',
            'dest': datum['statnTnm'],
            'status': statuses[int(datum['trainSttus'])],
            'type': types[int(datum['directAt'])],
            'time': datum['recptnDt']
        }
    # return data

    stns = get_stn_list(lineId)

    if lineId == '1' or lineId == '4':
        trains = seoul_metro(lineId)
        stn_id_map = None
        for no in data:
            if data[no]['type'] != '일반' and trains.get(no):
                if stn_id_map == None:
                    stn_id_map = {}
                    for stn in stns:
                        stn_id_map[stn['stn']] = stn['id']

                train = trains[no]
                if not stn_id_map.get(train['stn']): continue

                # print(data[n]['stn'], train['stn'])
                data[no]['stn'] = train['stn']
                data[no]['stnId'] = stn_id_map[train['stn']]
                data[no]['sts'] = train['sts']

    result = []
    for stn in stns:
        datum = {
            'stn': stn['stn'],
            'up': [],
            'dn': []
        }
        for no in data:
            train = data[no]
            if train['stnId'] == stn['id']: 
                datum[train['updn']].append({
                    'status': train['status'],
                    'type': train['type'],
                    'dest': train['dest'],
                    'no': no
                })
        result.append(datum)
    
    # 6호선 열차 복사 버그 수정
    # - 응암역을 출발해서 응암순환으로 진입한 열차의 행선지와 열차번호가 변경됨
    # - 동일한 열차여도 "응암순한 진입 전 열차번호"와 "응암순한 진입 후 열차번호"가 달라서, 시스템에서는 별개의 열차로 인식하는 듯
    # - 따라서, 응암순환 구간에 열차가 진입해도 응암역에 여전히 열차가 있다고 뜨는 잔상(?) 발생
    # - "응암역 열차 도착 정보"로 잔상을 삭제하는 방식으로 해결은 일단 되었으나, 순간적으로 잔상은 계속 남음
    if lineId == '6' and len(result[5]['up']) > 0:
        url = 'http://swopenapi.seoul.go.kr/api/subway/' + key + '/json/realtimeStationArrival/0/5/응암순환(상선)'
        response = requests.get(url)
        json = response.json()['realtimeArrivalList']
        trains = {}
        for train in json:
            if train['subwayId'] == '1006' and train['updnLine'] == '상행':
                trains[train['btrainNo']] = True
            
        up = []
        for train in result[5]['up']:
            if trains.get(train['no']): up.append(train)
        result[5]['up'] = up
        

    return result

def get_stn_list(lineId):
    if lineId == '1':
        return [{'stn':'소요산','id':'1001000100'},{'stn':'동두천','id':'1001000101'},{'stn':'보산','id':'1001000102'},{'stn':'동두천중앙','id':'1001000103'},{'stn':'지행','id':'1001000104'},{'stn':'덕정','id':'1001000105'},{'stn':'덕계','id':'1001000106'},{'stn':'양주','id':'1001000107'},{'stn':'녹양','id':'1001000108'},{'stn':'가능','id':'1001000109'},{'stn':'의정부','id':'1001000110'},{'stn':'회룡','id':'1001000111'},{'stn':'망월사','id':'1001000112'},{'stn':'도봉산','id':'1001000113'},{'stn':'도봉','id':'1001000114'},{'stn':'방학','id':'1001000115'},{'stn':'창동','id':'1001000116'},{'stn':'녹천','id':'1001000117'},{'stn':'월계','id':'1001000118'},{'stn':'광운대','id':'1001000119'},{'stn':'석계','id':'1001000120'},{'stn':'신이문','id':'1001000121'},{'stn':'외대앞','id':'1001000122'},{'stn':'회기','id':'1001000123'},{'stn':'청량리','id':'1001000124'},{'stn':'제기동','id':'1001000125'},{'stn':'신설동','id':'1001000126'},{'stn':'동묘앞','id':'1001000127'},{'stn':'동대문','id':'1001000128'},{'stn':'종로5가','id':'1001000129'},{'stn':'종로3가','id':'1001000130'},{'stn':'종각','id':'1001000131'},{'stn':'시청','id':'1001000132'},{'stn':'서울','id':'1001000133'},{'stn':'남영','id':'1001000134'},{'stn':'용산','id':'1001000135'},{'stn':'노량진','id':'1001000136'},{'stn':'대방','id':'1001000137'},{'stn':'신길','id':'1001000138'},{'stn':'영등포','id':'1001000139'},{'stn':'신도림','id':'1001000140'},{'stn':'구로','id':'1001000141'},{'stn':'가산디지털단지','id':'1001080142'},{'stn':'독산','id':'1001080143'},{'stn':'금천구청','id':'1001080144'},{'stn':'석수','id':'1001080145'},{'stn':'관악','id':'1001080146'},{'stn':'안양','id':'1001080147'},{'stn':'명학','id':'1001080148'},{'stn':'금정','id':'1001080149'},{'stn':'군포','id':'1001080150'},{'stn':'당정','id':'1001080151'},{'stn':'의왕','id':'1001080152'},{'stn':'성균관대','id':'1001080153'},{'stn':'화서','id':'1001080154'},{'stn':'수원','id':'1001080155'},{'stn':'세류','id':'1001080156'},{'stn':'병점','id':'1001080157'},{'stn':'세마','id':'1001080158'},{'stn':'오산대','id':'1001080159'},{'stn':'오산','id':'1001080160'},{'stn':'진위','id':'1001080161'},{'stn':'송탄','id':'1001080162'},{'stn':'서정리','id':'1001080163'},{'stn':'평택지제','id':'1001080164'},{'stn':'평택','id':'1001080165'},{'stn':'성환','id':'1001080166'},{'stn':'직산','id':'1001080167'},{'stn':'두정','id':'1001080168'},{'stn':'천안','id':'1001080169'},{'stn':'봉명','id':'1001080170'},{'stn':'쌍용','id':'1001080171'},{'stn':'아산','id':'1001080172'},{'stn':'탕정','id':'1001080173'},{'stn':'배방','id':'1001080174'},{'stn':'온양온천','id':'1001080175'},{'stn':'신창','id':'1001080176'},
                {'stn':'구일','id':'1001000142'},{'stn':'개봉','id':'1001000143'},{'stn':'오류동','id':'1001000144'},{'stn':'온수','id':'1001000145'},{'stn':'역곡','id':'1001000146'},{'stn':'소사','id':'1001000147'},{'stn':'부천','id':'1001000148'},{'stn':'중동','id':'1001000149'},{'stn':'송내','id':'1001000150'},{'stn':'부개','id':'1001000151'},{'stn':'부평','id':'1001000152'},{'stn':'백운','id':'1001000153'},{'stn':'동암','id':'1001000154'},{'stn':'간석','id':'1001000155'},{'stn':'주안','id':'1001000156'},{'stn':'도화','id':'1001000157'},{'stn':'제물포','id':'1001000158'},{'stn':'도원','id':'1001000159'},{'stn':'동인천','id':'1001000160'},{'stn':'인천','id':'1001000161'},{'stn':'광명','id':'1001080141'},{'stn':'서동탄','id':'1001801571'}]
    if lineId == '2':
        return [{'stn':'성수','id':'1002000211'},{'stn':'건대입구','id':'1002000212'},{'stn':'구의','id':'1002000213'},{'stn':'강변','id':'1002000214'},{'stn':'잠실나루','id':'1002000215'},{'stn':'잠실','id':'1002000216'},{'stn':'잠실새내','id':'1002000217'},{'stn':'종합운동장','id':'1002000218'},{'stn':'삼성','id':'1002000219'},{'stn':'선릉','id':'1002000220'},{'stn':'역삼','id':'1002000221'},{'stn':'강남','id':'1002000222'},{'stn':'교대','id':'1002000223'},{'stn':'서초','id':'1002000224'},{'stn':'방배','id':'1002000225'},{'stn':'사당','id':'1002000226'},{'stn':'낙성대','id':'1002000227'},{'stn':'서울대입구','id':'1002000228'},{'stn':'봉천','id':'1002000229'},{'stn':'신림','id':'1002000230'},{'stn':'신대방','id':'1002000231'},{'stn':'구로디지털단지','id':'1002000232'},{'stn':'대림','id':'1002000233'},
                {'stn':'신도림','id':'1002000234'},{'stn':'문래','id':'1002000235'},{'stn':'영등포구청','id':'1002000236'},{'stn':'당산','id':'1002000237'},{'stn':'합정','id':'1002000238'},{'stn':'홍대입구','id':'1002000239'},{'stn':'신촌 (지하)','id':'1002000240'},{'stn':'이대','id':'1002000241'},{'stn':'아현','id':'1002000242'},{'stn':'충정로','id':'1002000243'},{'stn':'시청','id':'1002000201'},{'stn':'을지로입구','id':'1002000202'},{'stn':'을지로3가','id':'1002000203'},{'stn':'을지로4가','id':'1002000204'},{'stn':'동대문역사문화공원','id':'1002000205'},{'stn':'신당','id':'1002000206'},{'stn':'상왕십리','id':'1002000207'},{'stn':'왕십리','id':'1002000208'},{'stn':'한양대','id':'1002000209'},{'stn':'뚝섬','id':'1002000210'},
                {'stn':'성수 (지선)','id':'1002000211_2'},{'stn':'용답','id':'1002002111'},{'stn':'신답','id':'1002002112'},{'stn':'용두','id':'1002002113'},{'stn':'신설동','id':'1002002114'},
                {'stn':'신도림 (지선)','id':'1002000234_2'},{'stn':'도림천','id':'1002002341'},{'stn':'양천구청','id':'1002002342'},{'stn':'신정네거리','id':'1002002343'},{'stn':'까치산','id':'1002002344'}] #,{'stn':'성수종착','id':'1002000211'}
    if lineId == '3':
        return [{'stn':'대화','id':'1003000309'},{'stn':'주엽','id':'1003000310'},{'stn':'정발산','id':'1003000311'},{'stn':'마두','id':'1003000312'},{'stn':'백석','id':'1003000313'},{'stn':'대곡','id':'1003000314'},{'stn':'화정','id':'1003000315'},{'stn':'원당','id':'1003000316'},{'stn':'원흥','id':'1003000317'},{'stn':'삼송','id':'1003000318'},
                {'stn':'지축','id':'1003000319'},{'stn':'구파발','id':'1003000320'},{'stn':'연신내','id':'1003000321'},{'stn':'불광','id':'1003000322'},{'stn':'녹번','id':'1003000323'},{'stn':'홍제','id':'1003000324'},{'stn':'무악재','id':'1003000325'},{'stn':'독립문','id':'1003000326'},{'stn':'경복궁','id':'1003000327'},{'stn':'안국','id':'1003000328'},{'stn':'종로3가','id':'1003000329'},{'stn':'을지로3가','id':'1003000330'},{'stn':'충무로','id':'1003000331'},{'stn':'동대입구','id':'1003000332'},{'stn':'약수','id':'1003000333'},{'stn':'금호','id':'1003000334'},{'stn':'옥수','id':'1003000335'},{'stn':'압구정','id':'1003000336'},{'stn':'신사','id':'1003000337'},{'stn':'잠원','id':'1003000338'},{'stn':'고속터미널','id':'1003000339'},{'stn':'교대','id':'1003000340'},{'stn':'남부터미널','id':'1003000341'},{'stn':'양재','id':'1003000342'},{'stn':'매봉','id':'1003000343'},{'stn':'도곡','id':'1003000344'},{'stn':'대치','id':'1003000345'},{'stn':'학여울','id':'1003000346'},{'stn':'대청','id':'1003000347'},{'stn':'일원','id':'1003000348'},{'stn':'수서','id':'1003000349'},{'stn':'가락시장','id':'1003000350'},{'stn':'경찰병원','id':'1003000351'},{'stn':'오금','id':'1003000352'}]
    if lineId == '4':
        return [{'stn':'진접','id':'1004000406'},{'stn':'오남','id':'1004000407'},{'stn':'별내별가람','id':'1004000408'},
                {'stn':'당고개','id':'1004000409'},{'stn':'상계','id':'1004000410'},{'stn':'노원','id':'1004000411'},{'stn':'창동','id':'1004000412'},{'stn':'쌍문','id':'1004000413'},{'stn':'수유','id':'1004000414'},{'stn':'미아','id':'1004000415'},{'stn':'미아사거리','id':'1004000416'},{'stn':'길음','id':'1004000417'},{'stn':'성신여대입구','id':'1004000418'},{'stn':'한성대입구','id':'1004000419'},{'stn':'혜화','id':'1004000420'},{'stn':'동대문','id':'1004000421'},{'stn':'동대문역사문화공원','id':'1004000422'},{'stn':'충무로','id':'1004000423'},{'stn':'명동','id':'1004000424'},{'stn':'회현','id':'1004000425'},{'stn':'서울','id':'1004000426'},{'stn':'숙대입구','id':'1004000427'},{'stn':'삼각지','id':'1004000428'},{'stn':'신용산','id':'1004000429'},{'stn':'이촌','id':'1004000430'},{'stn':'동작','id':'1004000431'},{'stn':'총신대입구 (이수)','id':'1004000432'},
                {'stn':'사당','id':'1004000433'},{'stn':'남태령','id':'1004000434'},{'stn':'선바위','id':'1004000435'},{'stn':'경마공원','id':'1004000436'},{'stn':'대공원','id':'1004000437'},{'stn':'과천','id':'1004000438'},{'stn':'정부과천청사','id':'1004000439'},{'stn':'인덕원','id':'1004000440'},{'stn':'평촌','id':'1004000441'},{'stn':'범계','id':'1004000442'},
                {'stn':'금정','id':'1004000443'},{'stn':'산본','id':'1004000444'},{'stn':'수리산','id':'1004000445'},{'stn':'대야미','id':'1004000446'},{'stn':'반월','id':'1004000447'},{'stn':'상록수','id':'1004000448'},{'stn':'한대앞','id':'1004000449'},{'stn':'중앙','id':'1004000450'},{'stn':'고잔','id':'1004000451'},{'stn':'초지','id':'1004000452'},{'stn':'안산','id':'1004000453'},{'stn':'신길온천','id':'1004000454'},{'stn':'정왕','id':'1004000455'},{'stn':'오이도','id':'1004000456'}]
    if lineId == '5':
        return [{'stn':'방화','id':'1005000510'},{'stn':'개화산','id':'1005000511'},{'stn':'김포공항','id':'1005000512'},{'stn':'송정','id':'1005000513'},{'stn':'마곡','id':'1005000514'},{'stn':'발산','id':'1005000515'},{'stn':'우장산','id':'1005000516'},{'stn':'화곡','id':'1005000517'},{'stn':'까치산','id':'1005000518'},{'stn':'신정','id':'1005000519'},{'stn':'목동','id':'1005000520'},{'stn':'오목교','id':'1005000521'},{'stn':'양평','id':'1005000522'},{'stn':'영등포구청','id':'1005000523'},{'stn':'영등포시장','id':'1005000524'},{'stn':'신길','id':'1005000525'},{'stn':'여의도','id':'1005000526'},{'stn':'여의나루','id':'1005000527'},{'stn':'마포','id':'1005000528'},{'stn':'공덕','id':'1005000529'},{'stn':'애오개','id':'1005000530'},{'stn':'충정로','id':'1005000531'},{'stn':'서대문','id':'1005000532'},{'stn':'광화문','id':'1005000533'},{'stn':'종로3가','id':'1005000534'},{'stn':'을지로4가','id':'1005000535'},{'stn':'동대문역사문화공원','id':'1005000536'},{'stn':'청구','id':'1005000537'},{'stn':'신금호','id':'1005000538'},{'stn':'행당','id':'1005000539'},{'stn':'왕십리','id':'1005000540'},{'stn':'마장','id':'1005000541'},{'stn':'답십리','id':'1005000542'},{'stn':'장한평','id':'1005000543'},{'stn':'군자','id':'1005000544'},{'stn':'아차산','id':'1005000545'},{'stn':'광나루','id':'1005000546'},{'stn':'천호','id':'1005000547'},{'stn':'강동','id':'1005000548'},
                {'stn':'길동','id':'1005000549'},{'stn':'굽은다리','id':'1005000550'},{'stn':'명일','id':'1005000551'},{'stn':'고덕','id':'1005000552'},{'stn':'상일동','id':'1005000553'},
                {'stn':'강일','id':'1005000554'},{'stn':'미사','id':'1005000555'},{'stn':'하남풍산','id':'1005000556'},{'stn':'하남시청','id':'1005000557'},{'stn':'하남검단산','id':'1005000558'},
                {'stn':'둔촌동','id':'1005080549'},{'stn':'올림픽공원','id':'1005080550'},{'stn':'방이','id':'1005080551'},{'stn':'오금','id':'1005080552'},{'stn':'개롱','id':'1005080553'},{'stn':'거여','id':'1005080554'},{'stn':'마천','id':'1005080555'}]
    if lineId == '6':
        return [ # {'stn':'응암순환(상선)','id':'1006000610'},
                {'stn':'역촌','id':'1006000611'},{'stn':'불광','id':'1006000612'},{'stn':'독바위','id':'1006000613'},{'stn':'연신내','id':'1006000614'},{'stn':'구산','id':'1006000615'},
                {'stn':'응암','id':'1006000610'}, # {'stn':'응암(하선-종착)','id':'1006000610'},
                {'stn':'새절','id':'1006000616'},{'stn':'증산','id':'1006000617'},{'stn':'디지털미디어시티','id':'1006000618'},{'stn':'월드컵경기장','id':'1006000619'},{'stn':'마포구청','id':'1006000620'},{'stn':'망원','id':'1006000621'},{'stn':'합정','id':'1006000622'},{'stn':'상수','id':'1006000623'},{'stn':'광흥창','id':'1006000624'},{'stn':'대흥','id':'1006000625'},{'stn':'공덕','id':'1006000626'},{'stn':'효창공원앞','id':'1006000627'},{'stn':'삼각지','id':'1006000628'},{'stn':'녹사평','id':'1006000629'},{'stn':'이태원','id':'1006000630'},{'stn':'한강진','id':'1006000631'},{'stn':'버티고개','id':'1006000632'},{'stn':'약수','id':'1006000633'},{'stn':'청구','id':'1006000634'},{'stn':'신당','id':'1006000635'},{'stn':'동묘앞','id':'1006000636'},{'stn':'창신','id':'1006000637'},{'stn':'보문','id':'1006000638'},{'stn':'안암','id':'1006000639'},{'stn':'고려대','id':'1006000640'},{'stn':'월곡','id':'1006000641'},{'stn':'상월곡','id':'1006000642'},{'stn':'돌곶이','id':'1006000643'},{'stn':'석계','id':'1006000644'},{'stn':'태릉입구','id':'1006000645'},{'stn':'화랑대','id':'1006000646'},{'stn':'봉화산','id':'1006000647'},{'stn':'신내','id':'1006000648'}]
    if lineId == '7':
        return [{'stn':'장암','id':'1007000709'},{'stn':'도봉산','id':'1007000710'},{'stn':'수락산','id':'1007000711'},{'stn':'마들','id':'1007000712'},{'stn':'노원','id':'1007000713'},{'stn':'중계','id':'1007000714'},{'stn':'하계','id':'1007000715'},{'stn':'공릉','id':'1007000716'},{'stn':'태릉입구','id':'1007000717'},{'stn':'먹골','id':'1007000718'},{'stn':'중화','id':'1007000719'},{'stn':'상봉','id':'1007000720'},{'stn':'면목','id':'1007000721'},{'stn':'사가정','id':'1007000722'},{'stn':'용마산','id':'1007000723'},{'stn':'중곡','id':'1007000724'},{'stn':'군자','id':'1007000725'},{'stn':'어린이대공원','id':'1007000726'},{'stn':'건대입구','id':'1007000727'},{'stn':'뚝섬유원지','id':'1007000728'},{'stn':'청담','id':'1007000729'},{'stn':'강남구청','id':'1007000730'},{'stn':'학동','id':'1007000731'},{'stn':'논현','id':'1007000732'},{'stn':'반포','id':'1007000733'},{'stn':'고속터미널','id':'1007000734'},{'stn':'내방','id':'1007000735'},{'stn':'총신대입구 (이수)','id':'1007000736'},{'stn':'남성','id':'1007000737'},{'stn':'숭실대입구','id':'1007000738'},{'stn':'상도','id':'1007000739'},{'stn':'장승배기','id':'1007000740'},{'stn':'신대방삼거리','id':'1007000741'},{'stn':'보라매','id':'1007000742'},{'stn':'신풍','id':'1007000743'},{'stn':'대림','id':'1007000744'},{'stn':'남구로','id':'1007000745'},{'stn':'가산디지털단지','id':'1007000746'},{'stn':'철산','id':'1007000747'},{'stn':'광명사거리','id':'1007000748'},{'stn':'천왕','id':'1007000749'},{'stn':'온수','id':'1007000750'},{'stn':'까치울','id':'1007000751'},{'stn':'부천종합운동장','id':'1007000752'},{'stn':'춘의역','id':'1007000753'},{'stn':'신중동','id':'1007000754'},{'stn':'부천시청','id':'1007000755'},{'stn':'상동','id':'1007000756'},{'stn':'삼산체육관','id':'1007000757'},{'stn':'굴포천','id':'1007000758'},{'stn':'부평구청','id':'1007000759'},{'stn':'산곡','id':'1007000760'},{'stn':'석남','id':'1007000761'}]
    if lineId == '8':
        return [{'stn':'암사','id':'1008000810'},{'stn':'천호','id':'1008000811'},{'stn':'강동구청','id':'1008000812'},{'stn':'몽촌토성','id':'1008000813'},{'stn':'잠실','id':'1008000814'},{'stn':'석촌','id':'1008000815'},{'stn':'송파','id':'1008000816'},{'stn':'가락시장','id':'1008000817'},{'stn':'문정','id':'1008000818'},{'stn':'장지','id':'1008000819'},{'stn':'복정','id':'1008000820'},{'stn':'남위례','id':'1008000821'},{'stn':'산성','id':'1008000822'},{'stn':'남한산성입구','id':'1008000823'},{'stn':'단대오거리','id':'1008000824'},{'stn':'신흥','id':'1008000825'},{'stn':'수진','id':'1008000826'},{'stn':'모란','id':'1008000827'}]
    if lineId == '9':
        return [{'stn':'개화','id':'1009000901'},{'stn':'김포공항','id':'1009000902'},{'stn':'공항시장','id':'1009000903'},{'stn':'신방화','id':'1009000904'},{'stn':'마곡나루','id':'1009000905'},{'stn':'양천향교','id':'1009000906'},{'stn':'가양','id':'1009000907'},{'stn':'증미','id':'1009000908'},{'stn':'등촌','id':'1009000909'},{'stn':'염창','id':'1009000910'},{'stn':'신목동','id':'1009000911'},{'stn':'선유도','id':'1009000912'},{'stn':'당산','id':'1009000913'},{'stn':'국회의사당','id':'1009000914'},{'stn':'여의도','id':'1009000915'},{'stn':'샛강','id':'1009000916'},{'stn':'노량진','id':'1009000917'},{'stn':'노들','id':'1009000918'},{'stn':'흑석','id':'1009000919'},{'stn':'동작','id':'1009000920'},{'stn':'구반포','id':'1009000921'},{'stn':'신반포','id':'1009000922'},{'stn':'고속터미널','id':'1009000923'},{'stn':'사평','id':'1009000924'},{'stn':'신논현','id':'1009000925'},{'stn':'언주','id':'1009000926'},{'stn':'선정릉','id':'1009000927'},{'stn':'삼성중앙','id':'1009000928'},{'stn':'봉은사','id':'1009000929'},{'stn':'종합운동장','id':'1009000930'},{'stn':'삼전','id':'1009000931'},{'stn':'석촌고분','id':'1009000932'},{'stn':'석촌','id':'1009000933'},{'stn':'송파나루','id':'1009000934'},{'stn':'한성백제','id':'1009000935'},{'stn':'올림픽공원','id':'1009000936'},{'stn':'둔촌오륜','id':'1009000937'},{'stn':'중앙보훈병원','id':'1009000938'}]
    
    if lineId == '101':
        return [{'stn':'문산','id':'1063075335'},{'stn':'파주','id':'1063075334'},{'stn':'월롱','id':'1063075333'},{'stn':'금촌','id':'1063075331'},{'stn':'금릉','id':'1063075330'},{'stn':'운정','id':'1063075329'},{'stn':'야당','id':'1063075328'},{'stn':'탄현','id':'1063075327'},{'stn':'일산','id':'1063075326'},{'stn':'풍산','id':'1063075325'},{'stn':'백마','id':'1063075324'},{'stn':'곡산','id':'1063075323'},{'stn':'대곡','id':'1063075322'},{'stn':'능곡','id':'1063075321'},{'stn':'행신','id':'1063075320'},{'stn':'강매','id':'1063075319'},{'stn':'화전','id':'1063075318'},{'stn':'수색','id':'1063075317'},{'stn':'디지털미디어시티','id':'1063075316'},
                {'stn':'가좌','id':'1063075315'},
                {'stn':'신촌','id':'1063080312'},{'stn':'서울','id':'1063080313'},
                {'stn':'홍대입구','id':'1063075314'},{'stn':'서강대','id':'1063075313'},{'stn':'공덕','id':'1063075312'},{'stn':'효창공원앞','id':'1063075826'},{'stn':'용산','id':'1063075110'},{'stn':'이촌','id':'1063075111'},{'stn':'서빙고','id':'1063075112'},{'stn':'한남','id':'1063075113'},{'stn':'옥수','id':'1063075114'},{'stn':'응봉','id':'1063075115'},{'stn':'왕십리','id':'1063075116'},{'stn':'청량리','id':'1063075117'},{'stn':'회기','id':'1063075118'},{'stn':'중랑','id':'1063075119'},{'stn':'상봉','id':'1063075120'},{'stn':'망우','id':'1063075121'},{'stn':'양원','id':'1063075122'},{'stn':'구리','id':'1063075123'},{'stn':'도농','id':'1063075124'},{'stn':'양정','id':'1063075125'},{'stn':'덕소','id':'1063075126'},{'stn':'도심','id':'1063075127'},{'stn':'팔당','id':'1063075128'},{'stn':'운길산','id':'1063075129'},{'stn':'양수','id':'1063075130'},{'stn':'신원','id':'1063075131'},{'stn':'국수','id':'1063075132'},{'stn':'아신','id':'1063075133'},{'stn':'오빈','id':'1063075134'},{'stn':'양평','id':'1063075135'},{'stn':'원덕','id':'1063075136'},{'stn':'용문','id':'1063075137'},{'stn':'지평','id':'1063075138'}]
    if lineId == '102':
        return [{'stn':'청량리','id':'1075075209'},
                {'stn':'왕십리','id':'1075075210'},{'stn':'서울숲','id':'1075075211'},{'stn':'압구정로데오','id':'1075075212'},{'stn':'강남구청','id':'1075075213'},{'stn':'선정릉','id':'1075075214'},{'stn':'선릉','id':'1075075215'},{'stn':'한티','id':'1075075216'},{'stn':'도곡','id':'1075075217'},{'stn':'구룡','id':'1075075218'},{'stn':'개포동','id':'1075075219'},{'stn':'대모산입구','id':'1075075220'},{'stn':'수서','id':'1075075221'},{'stn':'복정','id':'1075075222'},{'stn':'가천대','id':'1075075223'},{'stn':'태평','id':'1075075224'},{'stn':'모란','id':'1075075225'},{'stn':'야탑','id':'1075075226'},{'stn':'이매','id':'1075075227'},{'stn':'서현','id':'1075075228'},{'stn':'수내','id':'1075075229'},{'stn':'정자','id':'1075075230'},{'stn':'미금','id':'1075075231'},{'stn':'오리','id':'1075075232'},{'stn':'죽전','id':'1075075233'},{'stn':'보정','id':'1075075234'},{'stn':'구성','id':'1075075235'},{'stn':'신갈','id':'1075075236'},{'stn':'기흥','id':'1075075237'},{'stn':'상갈','id':'1075075238'},{'stn':'청명','id':'1075075239'},{'stn':'영통','id':'1075075240'},{'stn':'망포','id':'1075075241'},{'stn':'매탄권선','id':'1075075242'},{'stn':'수원시청','id':'1075075243'},{'stn':'매교','id':'1075075244'},
                {'stn':'수원','id':'1075075245'},{'stn':'고색','id':'1075075246'},{'stn':'오목천','id':'1075075247'},{'stn':'어천','id':'1075075248'},{'stn':'야목','id':'1075075249'},{'stn':'사리','id':'1075075250'},{'stn':'한대앞','id':'1075075251'},{'stn':'중앙','id':'1075075252'},{'stn':'고잔','id':'1075075253'},{'stn':'초지','id':'1075075254'},{'stn':'안산','id':'1075075255'},{'stn':'신길온천','id':'1075075256'},{'stn':'정왕','id':'1075075257'},{'stn':'오이도','id':'1075075258'},{'stn':'달월','id':'1075075259'},{'stn':'월곶','id':'1075075260'},{'stn':'소래포구','id':'1075075261'},{'stn':'인천논현','id':'1075075262'},{'stn':'호구포','id':'1075075263'},{'stn':'남동인더스파크','id':'1075075264'},{'stn':'원인재','id':'1075075265'},{'stn':'연수','id':'1075075266'},{'stn':'송도','id':'1075075267'},{'stn':'인하대','id':'1075075268'},{'stn':'숭의','id':'1075075269'},{'stn':'신포','id':'1075075270'},{'stn':'인천','id':'1075075271'}]
    if lineId == '103':
        return [{'stn':'신사','id':'1077000684'},{'stn':'논현','id':'1077000685'},{'stn':'신논현','id':'1077000686'},{'stn':'강남','id':'1077000687'},{'stn':'양재','id':'1077000688'},{'stn':'양재시민의숲','id':'1077000689'},{'stn':'청계산입구','id':'1077006810'},{'stn':'판교','id':'1077006811'},{'stn':'정자','id':'1077006812'},{'stn':'미금','id':'1077006813'},{'stn':'동천','id':'1077006814'},{'stn':'수지구청','id':'1077006815'},{'stn':'성복','id':'1077006816'},{'stn':'상현','id':'1077006817'},{'stn':'광교중앙','id':'1077006818'},{'stn':'광교','id':'1077006819'}]
    if lineId == '104':
        return [{'stn':'청량리','id':'1067080116'},{'stn':'회기','id':'1067080117'},{'stn':'중랑','id':'1067080118'},{'stn':'상봉','id':'1067080120'},{'stn':'망우','id':'1067080121'},{'stn':'신내','id':'1067080122'},{'stn':'갈매','id':'1067080123'},{'stn':'별내','id':'1067080124'},{'stn':'퇴계원','id':'1067080125'},{'stn':'사릉','id':'1067080126'},{'stn':'금곡','id':'1067080127'},{'stn':'평내호평','id':'1067080128'},{'stn':'천마산','id':'1067080129'},{'stn':'마석','id':'1067080130'},{'stn':'대성리','id':'1067080131'},{'stn':'청평','id':'1067080132'},{'stn':'상천','id':'1067080133'},{'stn':'가평','id':'1067080134'},{'stn':'굴봉산','id':'1067080135'},{'stn':'백양리','id':'1067080136'},{'stn':'강촌','id':'1067080137'},{'stn':'김유정','id':'1067080138'},{'stn':'남춘천','id':'1067080139'},{'stn':'춘천','id':'1067080140'}]
    if lineId == '105':
        return [{'stn':'판교','id':'1081037410'},{'stn':'이매','id':'1081037411'},{'stn':'삼동','id':'1081037412'},{'stn':'경기광주','id':'1081037413'},{'stn':'초월','id':'1081037414'},{'stn':'곤지암','id':'1081037415'},{'stn':'신둔도예촌','id':'1081037416'},{'stn':'이천','id':'1081037417'},{'stn':'부발','id':'1081037418'},{'stn':'세종왕릉','id':'1081037419'},{'stn':'여주','id':'1081037420'}]
    if lineId == '106':
        return [{'stn':'북한산우이','id':'1092004701'},{'stn':'솔밭공원','id':'1092004702'},{'stn':'4.19 민주묘지','id':'1092004703'},{'stn':'가오리','id':'1092004704'},{'stn':'화계','id':'1092004705'},{'stn':'삼양','id':'1092004706'},{'stn':'삼양사거리','id':'1092004707'},{'stn':'솔샘','id':'1092004708'},{'stn':'북한산보국문','id':'1092004709'},{'stn':'정릉','id':'1092004710'},{'stn':'성신여대입구','id':'1092004711'},{'stn':'보문','id':'1092004712'},{'stn':'신설동','id':'1092004713'}]
    if lineId == '107':
        # 원천 데이터에는 일산 연장이 반영되어 있으나, 2달이 지났음에도 Open API에는 아직도 반영되어 있지 않음 - 11월 7일에 반영됨
        return [{'stn':'일산','id':'1093004001'},{'stn':'풍산','id':'1093004002'},{'stn':'백마','id':'1093004003'},{'stn':'곡산','id':'1093004004'},
                {'stn':'대곡','id':'1093004005'},{'stn':'능곡','id':'1093004006'},{'stn':'김포공항','id':'1093004007'},{'stn':'원종','id':'1093004008'},{'stn':'부천종합운동장','id':'1093004009'},
                {'stn':'소사','id':'1093004010'},{'stn':'소새울','id':'1093004011'},{'stn':'시흥대야','id':'1093004012'},{'stn':'신천','id':'1093004013'},{'stn':'신현','id':'1093004014'},{'stn':'시흥시청','id':'1093004016'},{'stn':'시흥능곡','id':'1093004017'},{'stn':'달미','id':'1093004018'},{'stn':'선부','id':'1093004019'},{'stn':'초지','id':'1093004020'},{'stn':'시우','id':'1093004021'},{'stn':'원시','id':'1093004022'}]
        # return [{'stn':'대곡','id':'1093004001'},{'stn':'능곡','id':'1093004002'},{'stn':'김포공항','id':'1093004003'},{'stn':'원종','id':'1093004004'},{'stn':'부천종합운동장','id':'1093004005'},
        #         {'stn':'소사','id':'1093004006'},{'stn':'소새울','id':'1093004007'},{'stn':'시흥대야','id':'1093004008'},{'stn':'신천','id':'1093004009'},{'stn':'신현','id':'1093004010'},
        #         # {'stn':'하중','id':'1093004011'}, # 공사는 확정되었으나, 아직 공사 시작도 안한 역
        #         {'stn':'시흥시청','id':'1093004012'},{'stn':'시흥능곡','id':'1093004013'},{'stn':'달미','id':'1093004014'},{'stn':'선부','id':'1093004015'},{'stn':'초지','id':'1093004016'},{'stn':'시우','id':'1093004017'},{'stn':'원시','id':'1093004018'}]
    if lineId == '108':
        return [{'stn':'서울역','id':'1065006501'},{'stn':'공덕','id':'1065006502'},{'stn':'홍대입구','id':'1065006503'},{'stn':'디지털미디어시티','id':'1065006504'},{'stn':'마곡나루','id':'1065065042'},{'stn':'김포공항','id':'1065006505'},{'stn':'계양','id':'1065006506'},{'stn':'검암','id':'1065006507'},{'stn':'청라국제도시','id':'1065065071'},{'stn':'영종','id':'1065065072'},{'stn':'운서','id':'1065006508'},{'stn':'공항화물청사','id':'1065006509'},{'stn':'인천공항1터미널','id':'1065006510'},{'stn':'인천공항2터미널','id':'1065006511'}]
    return []

def line2_fix(datum):
    # 열차번호 시작 숫자 : 행선지
    # 1 성수지선 열차
    # 2 본선 순환
    # 3 본선 (성수발 아님)
    # 4 본선 신도림행
    # 5 신정지선 열차
    # 6 본선 성수행
    # 7 순환 아님, 성수 종착 아님
    # 8 순환 아님, 성수 종착 아님
    # 9 지선 임시열차
    no = datum['trainNo'][0]

    # 성수지선
    if no == '1': 
        if datum['statnTnm'] == '성수지선':
            datum['statnTnm'] = '성수 (지선)'
        if datum['statnId'] == '1002000211': #본선이랑 역 id 겹침
           datum['statnId'] = '1002000211_2'

    # 신정지선
    elif no == '5': 
        if datum['statnTnm'] == '신도림지선':
            datum['statnTnm'] = '신도림 (지선)'
        if datum['statnId'] == '1002000234': #본선이랑 역 id 겹침
            datum['statnId'] = '1002000234_2'
        if datum['updnLine'] == '0': datum['updnLine'] = '1' # 상하행 반대로 나옴
        else: datum['updnLine'] = '0'

    # 을지로순환선
    elif no == '4':
        datum['statnTnm'] = '신도림'
    elif no == '6': 
        datum['statnTnm'] = '성수'
    else:
        if datum['updnLine'] == '0': datum['statnTnm'] = '내선순환'
        else: datum['statnTnm'] = '외선순환'

    return datum

def line6_fix(datum):
    if datum['statnTnm'] == '응암순환(상선)': # 행선지 보정
        datum['statnTnm'] = '응암순환'
    
    return datum

def lineUI_fix(datum):
    if datum['updnLine'] == '0': datum['updnLine'] = '1' # 상하행 반대로 나옴
    else: datum['updnLine'] = '0'
    return datum

def lineW_fix(datum):
    if datum['updnLine'] == '0' and datum['statnTnm'] == None: # 일산행은 행선지가 사라짐
        datum['statnTnm'] = '일산'
    return datum

def lineA_fix(datum):
    if datum['directAt'] == '1': # 직통열차 예외처리
        datum['directAt'] = '2'
    return datum

def seoul_metro(line):
    url = 'https://smss.seoulmetro.co.kr/traininfo/traininfoUserMap.do?line=' + line + '&isCb=N'
    response = requests.post(url)
    html = BeautifulSoup(response.text, 'html.parser')

    result = {}
    data = html.select('div[class="1line_metro"]') #div.1line_metro 사용시 invalid 라면서 오류 발생
    data = data[0].select('div')
    for datum in data:
        # print(datum['data-statnTcd'])
        # print(datum)
        datum = datum['title'].split(' ')
        train = datum[0].replace('열차', '').replace('S', '').replace('K', '')
        stn = datum[2]
        sts = datum[3]
        if sts == '이동': sts = '접근'
        result[train] = {
            'stn': stn,
            'sts': sts
        }
        
    data = html.select('div[class="1line_korail"]')
    data = data[0].select('div')
    for datum in data:
        # print(datum['data-statnTcd'])
        # print(datum)
        datum = datum['title'].split(' ')
        train = datum[0].replace('열차', '').replace('S', '').replace('K', '')
        stn = datum[2]
        sts = datum[3]
        if sts == '이동': sts = '접근'
        result[train] = {
            'stn': stn,
            'sts': sts
        }
    
    return result

