import json
import traceback
import urllib.parse
from functools import lru_cache

import requests


class CrawlingException(Exception):
    pass


def get_url(date):  # '20210206' 형식의 문자열을 입력받음
    # full_naver_url = 'https://sports.news.naver.com/esports/schedule/index.nhn?year=2021&leagueCode=lck_2021_spring&month=02&category=lol'
    naver_sports_url = 'https://sports.news.naver.com/esports/schedule/index.nhn'  # HTTP 바디
    date = date.strip()
    year = date[0:4]
    month = date[4:6]
    date = date[6:8]
    # 이 부분은 주기적으로 수동으로 손봐야함!!!!!!!
    values = {
        'year': year,
        'leagueCode': 'lck_%s_spring' % (year),
        'month': month,
        'category': 'lol'
    }
    params = urllib.parse.urlencode(values)  # GET메서드
    url = naver_sports_url + "?" + params  # 최종 URL
    return url  # url을 리턴 (string 형식)


def get_full_json(url):  # 롤 대회 페이지 beautifulSoup객체 리턴
    try:
        # 안티크롤링을 막기 위해 헤더값을 추가해줌
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        # 200ok가 아니면 error발생
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        raise CrawlingException

    data_text = response.text
    # 소스코드에서 json 객체 부분만 추출하는 부분
    start_idx = data_text.rfind('scheduleData')
    data_text = data_text[start_idx + 14:]
    finish_idx = data_text.find('</script>')
    data_text = data_text[:finish_idx]
    finish_idx = data_text.find('});')
    data_text = data_text[:finish_idx]
    data_text = data_text.strip()
    # 여기까지하면 json객체 추출 완료
    try:
        json_obj = json.loads(data_text)
    except json.decoder.JSONDecodeError:
        raise CrawlingException
    return json_obj  # json 딕셔너리 리턴


def get_dict_of_date(json_obj, date):  # json 파일과 원하는 날짜를 입력. 날짜는 '20210206'의 형태로 입력
    scheduleList = json_obj.get("monthlyScheduleDailyGroup")
    # monthlyScheduleDailyGroup key 에 대응되는 value들이 dictionary 형태로 날짜,해당 날짜의 게임 정보들을 담고 있음
    # todayDate=date.today()
    # yesterdayDate=todayDate-timedelta(1)
    # yesterdayDateStr=yesterdayDate.strftime('%Y%m%d')

    result_dict = {}
    for dict in scheduleList:
        if dict['date'] == date:
            result_dict['date'] = date
            if dict['empty'] == False:  # 비어있는 객체가 아니면, 즉 그날 경기가 있었으면 실행
                result_dict['empty'] = False
                result_dict['scheduleList'] = []
                for subList in dict['scheduleList']:  # 보통 하루에 경기(딕셔너리)가 두개 있는데, scheduleList가 리스트 형식임
                    result_dict['scheduleList'].append(subList)
            else:  # 비어있는 객체라면, 즉 그날 경기가 없었으면 실행
                result_dict['empty'] = True
        else:  # 어제가 아닌 날은 제외
            continue
    if result_dict == {}:
        raise CrawlingException

    return result_dict


@lru_cache(maxsize=None)
def execute_this(date):
    try:
        url = get_url(date)
        json = get_full_json(url)
        dict = get_dict_of_date(json, date)

        return dict
    except CrawlingException:
        traceback.print_exc()
        return {}


if __name__ == "__main__":
    print(execute_this('20210821'))  # 이런식으로 실행하면 됨
