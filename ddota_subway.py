import requests, json

def get_ddota_data(lineId, stns):
    stns_ids = {}
    for e in stns:
        stns_ids[e['stn']] = e['id']

    # 웹 크롤러가 주소 찾기 어렵게 일부로 중간중간 잘라놓음
    do = '3011.do'  # 편성 정보가 평문으로 나오던 구버전은 3010.do
    sm = 'seoulmetro'
    url = 'htt' + 'ps://smss.' + sm +'.co.kr/api/' + do + '?lineNumCd=' + lineId
    response = requests.post(url, headers={
        'Content-Type': 'application/x-www-form-urlencoded',
        'Content-Length': '11',
        'Host': 'smss.seou'+'lmet'+'ro.c'+'o.kr',
        'Connection': 'Keep-gzip',
        'Accept-Encoding': 'application',
        'User-Agent': 'okhttp/4.2.2'
    }, data={
        'params': {
            'lineNumCd': lineId
        }
    })
    # print(response.text)
    json = response.json()
    
    types = ['일반', '급행']
    up_down = [None, 'down', 'up']
    status = ['출발', '접근', '도착', '출발']

    data = {}
    for e in json['ttcVOList']:
        no = e['trainY'].replace('K', '')  # Y는 열차번호를 의미
        # no2 = e['trainP']  # P는 편성번호를 의미하지만, 이제는 더 이상 제공하지 않음
        stn = e['stationNm']
        if stn == '서울역': stn = '서울'
        data[no] = {
            'status': status[e['sts']],
            'type': types[int(e['directAt'])],
            'updn': up_down[e['dir']],
            'stn': stn,
            'stnId': stns_ids[stn]
        }

    return data