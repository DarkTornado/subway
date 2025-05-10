import time, json, os, pytz
from datetime import datetime
from typing import Optional

class TrainLocation:
    
    @staticmethod
    def calc_location(fileName, stns, stns_ja, updn_no: Optional[int] = 0):
        result = []
        if stns_ja == None: 
            for stn in stns:
                result.append({
                    'stn': stn,
                    'up': [],
                    'dn': []
                })
        else:
            for n in range(0, len(stns)):
                result.append({
                    'stn': stns[n] + ' ('+ stns_ja[n] +')',
                    'up': [],
                    'dn': []
                })

        time = datetime.now(pytz.timezone('Asia/Seoul'))

        day = time.weekday()
        path = './timetable/' + fileName
        if day == 5 : path = path + '_2'  # 토요일
        elif day == 6 : path = path + '_1'  # 일요일 또는 휴일
        else : path = path + '_0'  # 평일
        path = path + '.json'
        # print(day)

        if (day == 5) and (not os.path.exists(path)):
            path = './timetable/' + fileName + '_1.json'

        file = open(path, encoding='utf-8')
        input = file.read()
        file.close()

        data = json.loads(input)
        hour = time.hour
        if hour == 0 : hour = 24
        now = 60 * 60 * hour + 60 * time.minute + time.second
        # print(hour)

        for train in data:
            time = data[train]
            if isinstance(time, dict):
                time = time['time']
                dest = data[train]['dest']
                trainType = data[train]['type']
            else:
                dest = time[-1]['stn']
                trainType = '일반'

            tym = time[-1].get('time')
            if tym == None or tym==':' or tym=='' : tym = time[-2]['time']
            tym = TrainLocation.time2sec(tym)
            if tym < now: continue

            tym = time[0].get('time')
            if tym == None or tym==':' or tym=='' : tym = time[1]['time']
            tym = TrainLocation.time2sec(tym)
            if now < tym: continue

            if train[-2:] == '_U':
                train = train[0:-2]
                ud = 'up'
            elif train[-2:] == '_D':
                train = train[0:-2]
                ud = 'dn'
            else:
                no = int(train[-1])
                ud = 'up' if no % 2 == updn_no else 'dn'
            
            stn = TrainLocation.get_train_location(now, time)
            index = stns.index(stn[0])

            result[index][ud].append({
                'status': stn[1],
                'type': trainType,
                'dest': dest,
                'no': train
            })

        # 대경선 통과역 표시
        if fileName == 'daegu_101':
            result[2]['stn'] += ' (미정차)'
            result[4]['stn'] += ' (미정차)'
            result[5]['stn'] += ' (미정차)'
            result[6]['stn'] += ' (미정차)'
            result[10]['stn'] += ' (미정차)'
            result[11]['stn'] += ' (미정차)'

        return result

    @staticmethod
    def get_train_location(now, time):
        for n in range(len(time)-1, -1, -1):
            if time[n]['time'] == ':': continue
            tym = TrainLocation.time2sec(time[n]['time'])
            
            status = time[n].get('sts')
            # 시간표에 도착/출발 시간이 따로 있는 경우
            if status and tym <= now:
                if status == '도착':
                    return time[n]['stn'], '도착'
                if status == '출발':
                    if tym == now : return time[n]['stn'], '도착'
                    if tym < now: return time[n + 1]['stn'], '접근'
                if status == '통과':
                    if tym == now : return time[n]['stn'], '통과'
                    if tym < now: return time[n + 1]['stn'], '접근'

            # 시간표에 시간만 하나 있는 경우
            else:
                if tym == now : return time[n]['stn'], None
                if tym < now: return time[n + 1]['stn'], None

        return 0

    @staticmethod
    def time2sec(time):
        t = time.split(':')
        if len(t) == 2 : t.append(0)
        t[0] = int(t[0])
        if t[0] == 0 : t[0] = 24
        return t[0] * 60 * 60 + int(t[1]) * 60 + int(t[2]);

