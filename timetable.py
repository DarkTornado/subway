import time, json, os, pytz
from datetime import datetime
from typing import Optional

class TrainLocation:
    
    @staticmethod
    def calc_location(fileName, stns, updn_no: Optional[int] = 0):
        result = []
        for stn in stns:
            result.append({
                'stn': stn,
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

            tym = time[-1]['time']
            if tym==':' or tym=='' : tym = time[-2]['time']
            tym = TrainLocation.time2sec(tym)
            if tym < now: continue
            tym = TrainLocation.time2sec(time[0]['time'])
            if now < tym: continue

            no = int(train[-1])
            ud = 'up' if no % 2 == updn_no else 'dn'
            stn = TrainLocation.get_train_location(now, time)
            index = stns.index(stn)

            result[index][ud].append({
                'status': None,
                'type': '일반',
                'dest': time[-1]['stn'],
                'no': train
            })

        return result

    @staticmethod
    def get_train_location(now, time):
        for n in range(len(time)-1, -1, -1):
            if time[n]['time'] == ':': continue
            tym = TrainLocation.time2sec(time[n]['time'])
            if tym == now : return time[n]['stn']
            if tym < now: return time[n + 1]['stn']
        return 0

    @staticmethod
    def time2sec(time):
        t = time.split(':')
        if len(t) == 2 : t.append(0)
        t[0] = int(t[0])
        if t[0] == 0 : t[0] = 24
        return t[0] * 60 * 60 + int(t[1]) * 60 + int(t[2]);

