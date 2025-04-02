# 전철 운행정보 API
© 2023-2025 Dark Tornado, All rights reserved.

- 이곳저곳에서 수집한 정보를 종합하여 보여줍니다.
- 정보를 얻을 수 있는 경로가 없는 경우, 자체적으로 시간표 데이터를 구축해서 사용합니다.
- FastAPI 사용
- [이 앱](https://play.google.com/store/apps/details?id=com.darktornado.metromap)의 백엔드

## 지원 노선

### 수도권
 - 수도권 1 ~ 9 호선
 - 인천 1 ~ 2호선
 - 경의·중앙선, 수인·분당선, 신분당선, 경춘선, 경강선, 서해선
 - 우이신설선, 신림선, 용인경전철, 의정부경전철, 김포골드라인
 - 공항철도
 - GTX-A

### 동남권
 - 부산 1 ~ 4호선
 - 동해선
 - 부산김해경전철

### 대전, 대구, 광주
 - 대전 1호선
 - 대구 1 ~ 3호선, 대경선
 - 광주 1호선

### 도쿄 지하철 - 도쿄도 교통국에서 운영 (도영(도에이) 지하철)
 - 아사쿠사선, 미타선, 신주쿠선, 오에도선
 - 도쿄 사쿠라 트램 (아라카와선) (교통국에서 운영하지만, 지하철은 아님)
 - 닛포리·토네리 라이너 (교통국에서 운영하지만, 지하철은 아님)

### <s>도쿄 지하철 - 도쿄메트로에서 운영</s>
 - <s>지원 예정</s>

### 요코하마 시영 지하철
 - 블루 라인, 그린 라인

### 후쿠오카 시영 지하철
 - 공항선, 하코자키선
 - 나나쿠마선

## 지원 예정 노선

### JR 큐슈
 - [ ] 가고시마 본선

### 도쿄 지하철 (도쿄메트로)
 - [x] 히비야선
 - [ ] 긴자선
 - [ ] 마루노우치선
 - [ ] 도자이선
 - [ ] 난보쿠선
 - [ ] 유라쿠초선
 - [ ] 치요다선
 - [ ] 한조몬선
 - [ ] 후쿠토신선


## 특이사항
- 경의·중앙선, 수인·분당선, 경춘선을 운행중인 급행 열차의 위치가 제대로 반영되지 않음
- `오에도선 도초마에역` 정보 보정 불가능
- 후쿠오카 지하철은 열차 위치를 .png 이미지로 주기 때문에, [node.js를 이용하여 따로 구현한 레포](https://github.com/DarkTornado/FukuokaCitySubway)에 기생하는 방식으로 구현
- JR 큐슈의 경우, HTML 태그를 열기만 하고 닫지 않은 경우가 종종 있음.

***

# 정보 출처

## [서울시 지하철 실시간 위치 정보 Open API](https://data.seoul.go.kr/dataList/OA-12601/A/1/datasetView.do) 사용
 - 수도권 1 ~ 9 호선
 - 경의·중앙선, 수인·분당선, 신분당선, 경춘선, 경강선
 - 우이신설선, 서해선, 신림선
 - 공항철도
 - GTX-A

## [서울교통공사 홈페이지](https://smss.seoulmetro.co.kr/traininfo/traininfoUserView.do) 크롤링
 - 수도권 1, 4호선 급행 열차 위치 보정
 - 4호선 상행 행선지 보정 및 진접선 구간 정보 구현
 - 종종 `서울시 지하철 API`에서 종종 2호선 정보가 넘어오지 않는데, 이 경우 임시 방편으로 알아서 서울교통공사 홈페이지에서 정보를 긁어오도록 구현

## [용인경량전철주식회사 홈페이지](https://ever-line.co.kr/) 크롤링
 - 용인경전철 (에버라인)

## 시간표 기반 운행 정보
 - [인천 1 ~ 2호선](https://github.com/DarkTornado/ictr)
 - 의정부경전철, 김포골드라인
 - 부산 1 ~ 4호선 <s>네이버 지도에서 실시간 정보 제공을 검토 중인 것으로 파악</s>
 - 동해선, 부산김해경전철
 - 대전 1호선
 - 대구 1 ~ 3호선, 대경선
 - 광주 1호선
 - 닛포리·토네리 라이너
 - <s>도쿄 지하철 중도쿄메트로에서 운영하는 노선</s>

## [도쿄도 교통국 열차 위치정보 API](https://ckan.odpt.org/dataset/r_train_location-toei) 사용
 - 아사쿠사선, 미타선, 신주쿠선, 오에도선
 - 도쿄 사쿠라 트램 (아라카와선)

## [요코하마시 홈페이지 크롤링](https://navi.hamabus.city.yokohama.lg.jp/koutuu/smart/top/Top?window=trainLocation)
 - 블루 라인, 그린 라인

## [후쿠오카시 홈페이지 크롤링?](https://unkou.subway.city.fukuoka.lg.jp/unkou/kuhako.html)
 - 공항선, 하코자키선, 나나쿠마선

***

# 서울시 지하철 실시간 위치 정보(이하 서울시 API) 버그 목록 및 특이사항

## 열차 복사 버그
 - 같은 열차가 두 번 이상 포함되어 있음, 데이터 수집 시간은 다름.
 - 담당자가 `2023년 10월 13일`에 지속적으로 모니터링하겠다고 했는데, `아직도(2023년 11월)` 발생 중
 - 애초에 해당 현상은 `서울시 API가 정보를 받아오는 데이터 원천`에서 발생중
 - 데이터 수집 시간도 함께 넘어오니, 더 최근에 수집된 데이터를 사용하도록 구현하여 해결

## 6호선 열차 복사 버그
 - 응암역을 출발한 열차가 응암순환 구간에 열차가 진입해도, 여전히 응암역에 열차가 있다고 뜨는 잔상(?) 발생
 - 열차가 응암역을 출발해서 응암순환으로 진입하면 해당 열차의 행선지와 열차번호가 변경되는데, 시스템에서는 서로 다른 열차로 인식하는 듯
   - `방금 응암순환 구간에 진입한 열차`와 `아까 응암역에 도착한 열차`는 실제로는 같은 열차지만 다른 열차로 인식하고 열차가 2대 있는 것으로 표시
 - `응암역 열차 도착 정보`로 잔상을 삭제하는 방식으로 일단 해결, 순간적으로 잔상은 계속 남음

## 급행 열차 순간이동 버그
 - 급행 열차가 `급행 열차가 정차하는 역`에 도착해야 열차 위치가 갱신됨
 - e.g. `도안역`을 출발한 `동인천급행`이 `도화역`에 도착해도 여전히 `도안역`에 있다고 표시되며, `제물포역`에 진입해야 열차 위치 갱신
 - `도안역`과 `제물포역`은 `급행 열차가 정차하는 역`, `도화역`은 두 역 사이에 있는 `급행 열차가 동과하는 역`.
 - 한국철도공사(코레일)가 노선의 일부 또는 전체를 관할하는 노선에서만 발생함. 1, 4호선, 경의중앙선, 수인분당선, 경춘선에서 발생, 9호선에서는 발생하지 않음.
 - [서울교통공사 홈페이지](https://smss.seoulmetro.co.kr/traininfo/traininfoUserView.do)에서는 정상적으로 표시되기에, 1, 3, 4 호선은 홈페이지 크롤링으로 급행 열차 위치 보정
 - <s>사실 나머지도 수정할 수 있긴 한데 읍읍</s>
 - 해당 버그는 애초에 `데이터 원천`에서 발생 중

## 1호선 서울교통공사 구간에서 급행열차가 완행으로 표시되는 버그
 - 서울교통공사 구긴에 있는 열차들이 전부 완행으로 표시됨
 - 열차번호로 구분해서 해결
   - 0XXX : 완행
   - 1XXX : 급행

## 2호선 역 id 중복
 - 본선 성수역과 지선 성수역의 id가 동일
 - 본선 신도림역과 지선 신도림역의 id가 동일
 - 열차번호로 구분 완료
   - 2XXX, 3XXX, 4XXX, 6XXX, 7XXX, 8XXX : 본선 (을지로순환선)
   - 1XXX : 성수지선
   - 5XXX : 신정지선
   - 9XXX : 지선 임시열차

## 2호선 신정지선 상/하행 방향 반대
 - 상/하행 정보를 반대로 줌

## 2호선 정보 상습적 누락
 - 그냥 계속 오락가락해서 정보가 나왔다가 말았다가 함.
 - 아예 `데이터 원천`에서 값이 넘어오지 않음
 - `서울시 API`에서 정보가 나오지 않는다면 서울교통공사 홈페이지를 크롤링하도록 구현

## 4호선 진접선 구간 정보 없음 (불암산 ~ 진접)
 - 당고개(구 당고개)역 진입 이후에는 진접행 열차의 정보가 제공되지 않음
 - 진접선 구간은 남양주시의 협조가 있어야 실시간 운행 정보를 제공할 수 있다고 답변했는데, 정작 본인들이 만든 앱에서는 진접선 구간은 아주 잘 나옴.
 - 진접선 구간과 `별내선 별내역 ~ 다산역 구간`도 같은 곳에서 관리하는데, 저 구간은 아주 잘 나옴.
 - 서울교통공사 홈페이지에도 진접선 구간이 잘 나오고 있기에, 크롤링으로 보정.

## 우이신설선 상/하행 방향 반대
 - 상/하행 정보를 반대로 줌

***

# 서울시 API 수정된 버그들

## 서해선 일산 연장 미대응 - 2023년 11월 7일에 해결됨
 - `데이터 원천`에는 서해선 일산 연장 구간이 반영되어 있으나, `서울시 API`에는 2달 넘게 반영되지 않음
 - 일산행 열차는 행선지 정보(null)가 없음
 - 서해선이 일산역으로 연장되면서 서해선 전체 역 id가 4칸 뒤로 밀렸는데, `서울시 API`에서는 밀려난게 반영되지 않음
 - 사실 일산행 열차는 행선지 정보를 `역 id` 대신 `역 code`로 주고 있었으나, `역 code`는 `데이터 원천`에서 사용하는 값으로 `서울시 API`에서는 제공하지 않음.

## 1호선 연천행 열차 관련 버그 - 2023년 12월 23일에 해결된 것 확인
 - 2023년 12월 16일에 1호선 연천 ~ 소요산 구간 연장 개통
 - 원천 데이터 및 서울시 API에 모든 연천행 열차 누락
 - 2023년 12월 18일 월요일, `데이터 원천`에서는 연천 ~ 소요산 구간 연장 구간 반영 및 연천행 열차 정상 출력, 서울시 API는 정상 작동 여부 확인 안해봄
 - 2023년 12월 19일, 서울시 API에도 연천행 열차가 출력은 되고 있으나, 행선지 정보는 누락. `서해선 일산 연장 미대응`과 증상 동일
 - 연천행 열차의 경우 `행선지의 역 id`가 `key`인 `statnTid`에 `역 id` 대신 `역 code`가 저장되고, 행선지의 역 이름은 `null`로 표시됨
 - 연천 ~ 소요산 구간은 아예 정보가 없음 (원천 데이터에는 있음)

## 5호선 전체 정보 누락 - 2024년 2월 17일에 해결된 것 확인
 - 2024년 2월 16일 17시 30분 기준, 5호선 전체 정보가 누락되는 것 확인
 - 데이터 원천에서도 정보가 나오지 않음
 
## 경강선 성남역 존재 누락 - 2024년 7월 4일에 해결된 것 확인
 - 성남역 개통 시점부터 계속 경강선 성남역이 존재하지 않는 것처럼 작동
 - 성남역을 지나 다음 역에 도착해야 열차 위치가 갱신됨
 - `데이터 원천`에서도 동일
 - 언젠가에는 수정되겠지 하면서 까먹고 살다가 확인해보니 해결됨

## GTX-A 행선지 정보 누락 - 2024년 8월 9일에 해결된 것 확인
 - `행선지의 역 id`가 `key`인 `statnTid`에 `역 id` 대신 `역 code`가 저장되고, 행선지의 역 이름은 `null`로 표시됨
 - `서해선 일산 연장 미대응`, `1호선 연천행 열차 버그`와 동일한 증상

## 신림선 행선지 정보가 잘못됨 - 2024년 8월 9일에 해결된 것 확인
 - `샛강행`과 `관안산행`이 `소요산행`과 `병점행`으로 표시됨

## 8호선 행선지 정보 누락 및 별내선이 존재하지 않는 것처럼 작동
 - `행선지의 역 id`가 `value`인 `statnTid`에 `역 id` 대신 `역 code`가 저장되고, 행선지의 역 이름은 `null`로 표시됨
 - `서해선 일산 연장 미대응`, `1호선 연천행 열차 버그`, `GTX-A 행선지 정보 누락`과 동일한 증상
 - 개통 예정인 `별내선`이 `데이터 원천`에 추가된 영향인 듯. 개통 전날에 확인했을 때 발견된 버그
 - 별내선 구간은 열차 정보가 전혀 나오지 않음. `데이터 원천`에서는 아주 잘 나옴.
 - `statnTid`에 있는  `역 code`를 확인해보면, `별내`행 열차가 전부 `암사`행으로 나오는 중임을 알 수 있음

***

# 도쿄도 교통국 열차 위치 API 특이사항

## 오에도선 도초마에역 정보 보정 불가능
 - `도에이 오에도선`은 `도초마에역`에서 환승 가능한 순환선처럼 생겼지만, 실제로는 순환선이 아니며 `6`자 모양으로 돌아서 들어갔다가 열차 방향을 돌려서 다시 나오는 구조
 - `현재 도초마에역에 있는 열차`가 어느 방향으로 와서 어느 방향으로 나가는지에 대한 정보를 알 수 없음
 - <s>사실 도에이 앱이나 도쿄메트로 앱 뜯으면 알 수 있음</s>

