from bs4 import BeautifulSoup
import requests, json, pytz
from datetime import datetime, timezone, timedelta

class Toei:
    
    def get_data(self, lineName):  # https://ckan.odpt.org/dataset/r_train_location-toei
        url = 'https://api-public.odpt.org/api/v4/odpt:Train?odpt:operator=odpt.Operator:Toei'
        response = requests.get(url)
        json = response.json()

        data = []
        line = 'odpt.Railway:Toei.' + lineName
        isUp = {
            'Asakusa': 'Southbound',
            'Mita': 'Southbound',
            'Shinjuku': 'Westbound',
            'Oedo': 'InnerLoop',
            'Arakawa': 'Minowabashi'
        }
        
        types = {
            'Local': '보통',
            'Express': '급행',
            'LimitedExpress': '특급',
            'RapidLimitedExpress': '쾌속특급',
            'AirportRapidLimitedExpress': '에어포트 쾌특',
            'AccessExpress': '엑세스 특급',
            'Rapid': '쾌속'
        }
        
        dests = {
            'Sengakuji': '센가쿠지',
            'NishiMagome': '니시마고메',
            'ImbaNihonIdai': '인바니혼이다이',
            'NaritaAirportTerminal1': '나리타공항',
            'HanedaAirportTerminal1and2': '하네다공항',
            'KeikyuKurihama': '케이큐쿠리하마',
            'ShibayamaChiyoda': '시바야마치요다',
            'InzaiMakinohara': '인자이마키노하라',
            'KeiseiNarita': '케이세이나리타',
            'KeiseiSakura': '케이세이사쿠라',
            'KeiseiTakasago': '케이세이타카사고',
            'Aoto': '아오토',
            'Misakiguchi': '미사키구치',
            'Sogosando': '소고산도',
            'Oshiage': '오시아게',
            'Miurakaigan': '미우라카이간',
            'KanagawaShimmachi': '가나가와신마치',

            'ShirokaneTakanawa': '시로카네타카나와',
            'NishiTakashimadaira': '니시타카시마다이라',
            'Hiyoshi': '히요시',
            'Ebina': '에비나',
            'MusashiKosugi': '무사시코스기',
            'ShinYokohama': '신요코하마',
            'Takashimadaira': '타카시마다이라',
            'Yamato': '야마토',
            'Shonandai': '쇼난다이',
            'Nishiya': '니시야',

            'Motoyawata': '모토야와타',
            'Hashimoto': '하시모토',
            'Sasazuka': '사사즈카',
            'KeioTamaCenter': '게이오타마센터',
            'KiyosumiShirakawa': '키요스미시라카와',

            'Tochomae': '도초마에',
            'Hikarigaoka': '히카리가오카',
            'Shinjuku': '신주쿠',
            'Shiodome': '시오도메',
            'Ojima': '오지마',
            'Wakabadai': '와카다바이',

            'Minowabashi': '미노와바시',
            'Waseda': '와세다',
            'ArakawaShakomae': '아라카와샤코마에',
            'OjiEkimae': '오지에키마에',
            'MachiyaEkimae': '마치야에키마에',
            'OtsukaEkimae': '오츠카에키마에'
        }

        for datum in json:
            if datum['odpt:railway'] == line :
                stn = datum['odpt:toStation']
                status = '접근'
                if stn == None :
                    stn = datum['odpt:fromStation']
                    status = '도착'

                ud = 'dn'
                if isUp[lineName] == datum['odpt:railDirection'].split('.')[-1].split(':')[-1]: ud = 'up'
                dest = datum['odpt:destinationStation'][0].split('.')[-1]
                if dest in dests: dest = dests[dest]

                data.append({
                    'no': datum['odpt:trainNumber'],
                    'type': types[datum['odpt:trainType'].split('.')[-1]],
                    'stn': stn.split('.')[-1],
                    'dest': dest,
                    'status': status,
                    'ud': ud
                })

        result = []
        stns = self.get_stn_list(lineName)
        for i in range(0, len(stns)):
            stn = stns[i]
            result.append({
                'stn': stn['ko'] + ' (' + stn['ja'] + ')',
                'up': [],
                'dn': []
            })

            for train in data:
                if train['stn'] == stns[i]['en']:
                    result[i][train['ud']].append({
                        'no': train['no'],
                        'type': train['type'],
                        'status': train['status'],
                        'dest': train['dest']
                    })

        return result


    def get_stn_list(self, lineName):
        if lineName == 'Asakusa':
            return [{'ko':'니시마고메','ja':'西馬込','en':'NishiMagome'},{'ko':'마고메','ja':'馬込','en':'Magome'},{'ko':'나카노부','ja':'中延','en':'Nakanobu'},{'ko':'토고시','ja':'戸越','en':'Togoshi'},{'ko':'고탄다','ja':'五反田','en':'Gotanda'},{'ko':'타카나와다이','ja':'高輪台','en':'Takanawadai'},{'ko':'센가쿠지','ja':'泉寺','en':'Sengakuji'},{'ko':'미타','ja':'三田','en':'Mita'},{'ko':'다이몬','ja':'大門','en':'Daimon'},{'ko':'신바시','ja':'新橋','en':'Shimbashi'},{'ko':'히가시긴자','ja':'東銀座','en':'HigashiGinza'},{'ko':'타카라초','ja':'宝町','en':'Takaracho'},{'ko':'니혼바시','ja':'日本橋','en':'Nihombashi'},{'ko':'닌교초','ja':'人形町','en':'Ningyocho'},{'ko':'히가시니혼바시','ja':'東日本橋','en':'HigashiNihombashi'},{'ko':'아사쿠사바시','ja':'浅草橋','en':'Asakusabashi'},{'ko':'쿠라마에','ja':'蔵前','en':'Kuramae'},{'ko':'아사쿠사','ja':'浅草','en':'Asakusa'},{'ko':'혼조아즈마바시','ja':'本所吾橋','en':'HonjoAzumabashi'},{'ko':'오시아게','ja':'押上','en':'Oshiage'}]
        if lineName == 'Mita':
            return [{'ko':'메구로','ja':'目黒','en':'Meguro'},{'ko':'시로카네다이','ja':'白金台','en':'Shirokanedai'},{'ko':'시로카네타카나와','ja':'白金高輪','en':'ShirokaneTakanawa'},{'ko':'미타','ja':'三田','en':'Mita'},{'ko':'시바코엔','ja':'芝公園','en':'Shibakoen'},{'ko':'오나리몬','ja':'御成門','en':'Onarimon'},{'ko':'우치사이와이초','ja':'内幸町','en':'Uchisaiwaicho'},{'ko':'히비야','ja':'日比谷','en':'Hibiya'},{'ko':'오테마치','ja':'大手町','en':'Otemachi'},{'ko':'진보초','ja':'神保町','en':'Jimbocho'},{'ko':'스이도바시','ja':'水道橋','en':'Suidobashi'},{'ko':'카스가','ja':'春日','en':'Kasuga'},{'ko':'하쿠산','ja':'白山','en':'Hakusan'},{'ko':'센고쿠','ja':'千石','en':'Sengoku'},{'ko':'스가모','ja':'巣鴨','en':'Sugamo'},{'ko':'니시스가모','ja':'西巣鴨','en':'NishiSugamo'},{'ko':'신이타바시','ja':'新板橋','en':'ShinItabashi'},{'ko':'이타바시쿠야쿠쇼마에','ja':'板橋区役所前','en':'ItabashiKuyakushomae'},{'ko':'이타바시혼초','ja':'板橋本町','en':'Itabashihoncho'},{'ko':'모토하스누마','ja':'本蓮沼','en':'Motohasunuma'},{'ko':'시무라사카우에','ja':'志村坂上','en':'ShimuraSakaue'},{'ko':'시무라산초메','ja':'志村三丁目','en':'ShimuraSanchome'},{'ko':'하스네','ja':'蓮根','en':'Hasune'},{'ko':'니시다이','ja':'西台','en':'Nishidai'},{'ko':'타카시마다이라','ja':'高島平','en':'Takashimadaira'},{'ko':'신타카시마다이라','ja':'新高島平','en':'ShinTakashimadaira'},{'ko':'니시타카시마다이라','ja':'西高島平','en':'NishiTakashimadaira'}]
        if lineName == 'Shinjuku':
            return [{'ko':'신주쿠','ja':'新宿','en':'Shinjuku'},{'ko':'신주쿠산초메','ja':'新宿三丁目','en':'ShinjukuSanchome'},{'ko':'아케보노바시','ja':'曙橋','en':'Akebonobashi'},{'ko':'이치가야','ja':'市ヶ谷','en':'Ichigaya'},{'ko':'쿠단시타','ja':'九段下','en':'Kudanshita'},{'ko':'진보초','ja':'神保町','en':'Jimbocho'},{'ko':'오가와마치','ja':'小川町','en':'Ogawamachi'},{'ko':'이와모토초','ja':'岩本町','en':'Iwamotocho'},{'ko':'바쿠로요코야마','ja':'馬喰横山','en':'BakuroYokoyama'},{'ko':'하마초','ja':'浜町','en':'Hamacho'},{'ko':'모리시타','ja':'森下','en':'Morishita'},{'ko':'키쿠카와','ja':'菊川','en':'Kikukawa'},{'ko':'스미요시','ja':'住吉','en':'Sumiyoshi'},{'ko':'니시오지마','ja':'西大島','en':'NishiOjima'},{'ko':'오지마','ja':'大島','en':'Ojima'},{'ko':'히가시오지마','ja':'東大島','en':'HigashiOjima'},{'ko':'후나보리','ja':'船堀','en':'Funabori'},{'ko':'이치노에','ja':'一之江','en':'Ichinoe'},{'ko':'미즈에','ja':'江','en':'Mizue'},{'ko':'시노자키','ja':'篠崎','en':'Shinozaki'},{'ko':'모토야와타','ja':'本八幡','en':'Motoyawata'}]
        if lineName == 'Oedo':
            return [{'ko':'도초마에','ja':'都庁前','en':'Tochomae'},{'ko':'신주쿠니시구치','ja':'新宿西口','en':'ShinjukuNishiguchi'},{'ko':'히가시신주쿠','ja':'東新宿','en':'HigashiShinjuku'},{'ko':'와카마츠카와다','ja':'若松河田','en':'WakamatsuKawada'},{'ko':'우시고메야나기초','ja':'牛込柳町','en':'UshigomeYanagicho'},{'ko':'우시고메카구라자카','ja':'牛込神楽坂','en':'UshigomeKagurazaka'},{'ko':'이다바시','ja':'飯田橋','en':'Iidabashi'},{'ko':'카스가','ja':'春日','en':'Kasuga'},{'ko':'혼고산초메','ja':'本郷三丁目','en':'HongoSanchome'},{'ko':'우에노오카치마치','ja':'上野御徒町','en':'UenoOkachimachi'},{'ko':'신오카치마치','ja':'新御徒町','en':'ShinOkachimachi'},{'ko':'쿠라마에','ja':'蔵前','en':'Kuramae'},{'ko':'료고쿠','ja':'両国','en':'Ryogoku'},{'ko':'모리시타','ja':'森下','en':'Morishita'},{'ko':'키요스미시라카와','ja':'清澄白河','en':'KiyosumiShirakawa'},{'ko':'몬젠나카쵸','ja':'門前仲町','en':'MonzenNakacho'},{'ko':'츠키시마','ja':'月島','en':'Tsukishima'},{'ko':'카치도키','ja':'勝どき','en':'Kachidoki'},{'ko':'츠키지시조','ja':'築地市場','en':'Tsukijishijo'},{'ko':'시오도메','ja':'汐留','en':'Shiodome'},{'ko':'다이몬','ja':'大門','en':'Daimon'},{'ko':'아카바네바시','ja':'赤羽橋','en':'Akabanebashi'},{'ko':'아자부쥬반','ja':'麻布十番','en':'AzabuJuban'},{'ko':'롯폰기','ja':'六本木','en':'Roppongi'},{'ko':'아오야마잇초메','ja':'青山一丁目','en':'AoyamaItchome'},{'ko':'코쿠리츠쿄기죠','ja':'国立競技場','en':'KokuritsuKyogijo'},{'ko':'요요기','ja':'代々木','en':'Yoyogi'},{'ko':'신주쿠','ja':'新宿','en':'Shinjuku'},
                    {'ko':'도초마에','ja':'都庁前','en':'Tochomae'},{'ko':'니시신주쿠고초메','ja':'西新宿五丁目','en':'NishiShinjukuGochome'},{'ko':'나카노사카우에','ja':'中野坂上','en':'NakanoSakaue'},{'ko':'히가시나카노','ja':'東中野','en':'HigashiNakano'},{'ko':'나카이','ja':'中井','en':'Nakai'},{'ko':'오치아이미나미나가사키','ja':'落合南長崎','en':'OchiaiMinamiNagasaki'},{'ko':'신에고타','ja':'新江古田','en':'ShinEgota'},{'ko':'네리마','ja':'練馬','en':'Nerima'},{'ko':'토시마엔','ja':'豊島園','en':'Toshimaen'},{'ko':'네리마카스가초','ja':'練馬春日町','en':'NerimaKasugacho'},{'ko':'히카리가오카','ja':'光が丘','en':'Hikarigaoka'}]
        if lineName == 'Arakawa':
            return [{'ko':'미노와바시','ja':'三ノ輪橋','en':'Minowabashi'},{'ko':'아라카와잇츄마에','ja':'荒川一中前','en':'ArakawaItchumae'},{'ko':'아라카와쿠야쿠쇼마에','ja':'荒川区役所前','en':'Arakawakuyakushomae'},{'ko':'아라카와니초메','ja':'荒川二丁目','en':'ArakawaNichome'},{'ko':'아라카와나나초메','ja':'荒川七丁目','en':'ArakawaNanachome'},{'ko':'마치야에키마에','ja':'町屋駅前','en':'MachiyaEkimae'},{'ko':'마치야니초메','ja':'町屋二丁目','en':'MachiyaNichome'},{'ko':'히가시오구산초메','ja':'東尾久三丁目','en':'HigashiOguSanchome'},{'ko':'쿠마노마에','ja':'熊野前','en':'Kumanomae'},{'ko':'미야노마에','ja':'宮ノ前','en':'Miyanomae'},{'ko':'오다이','ja':'小台','en':'Odai'},{'ko':'아라카와유엔치마에','ja':'荒川遊園地前','en':'ArakawaYuenchimae'},{'ko':'아라카와샤코마에','ja':'荒川車庫前','en':'ArakawaShakomae'},{'ko':'카지와라','ja':'梶原','en':'Kajiwara'},{'ko':'사카에쵸','ja':'栄町','en':'Sakaecho'},{'ko':'오지에키마에','ja':'王子駅前','en':'OjiEkimae'},{'ko':'아스카야마','ja':'飛鳥山','en':'Asukayama'},{'ko':'타키노가와잇초메','ja':'滝野川一丁目','en':'TakinogawaItchome'},{'ko':'니시가하라욘초메','ja':'西ヶ原四丁目','en':'NishigaharaYonchome'},{'ko':'신코신즈카','ja':'新庚申塚','en':'ShinKoshinzuka'},{'ko':'코신즈카','ja':'庚申塚','en':'Koshinzuka'},{'ko':'스가모신덴','ja':'巣鴨新田','en':'Sugamoshinden'},{'ko':'오츠카에키마에','ja':'大塚駅前','en':'OtsukaEkimae'},{'ko':'무코하라','ja':'向原','en':'Mukohara'},{'ko':'히가시이케부쿠로욘초메','ja':'東池袋四丁目','en':'HigashiIkebukuroYonchome'},{'ko':'도덴조시가야','ja':'都電雑司ヶ谷','en':'TodenZoshigaya'},{'ko':'키시보진마에','ja':'鬼子母神前','en':'Kishibojimmae'},{'ko':'가쿠슈인시타','ja':'学習院下','en':'Gakushuinshita'},{'ko':'오모카게바시','ja':'面影橋','en':'Omokagebashi'},{'ko':'와세다','ja':'早稲田','en':'Waseda'}]
        return []
