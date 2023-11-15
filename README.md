# 전철 운행정보 API
© 2023 Dark Tornado, All rights reserved.

- 이곳저곳에서 수집한 정보를 종합하여 보여줍니다.
- 정보를 얻을 수 있는 경로가 없는 경우, 자체적으로 시간표 데이터를 구축해서 사용합니다.
- FastAPI 사용

## 정보 출처

### [서울시 지하철 실시간 위치 정보 Open API](https://data.seoul.go.kr/dataList/OA-12601/A/1/datasetView.do) 사용
 - 수도권 1 ~ 9 호선
 - 경의·중앙선
 - 수인·분당선
 - 신분당선
 - 경춘선
 - 경강선
 - 우이신선
 - 서해선
 - 공항철도

### [서울교통공사 홈페이지](https://smss.seoulmetro.co.kr/traininfo/traininfoUserView.do) 크롤링
 - 수도권 1, 3, 4호선 급행 열차 위치 보정

### [용인경량전철주식회사 홈페이지](https://ever-line.co.kr/) 크롤링
 - 용인경전철 (에버라인)

### 시간표 기반 운행 정보
 - [인천 1 ~ 2호선](https://github.com/DarkTornado/ictr)
 - 신림선
 - 의정부경전철
 - 김포도시철도

