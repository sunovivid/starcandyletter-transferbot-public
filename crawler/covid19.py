import traceback
from functools import lru_cache
from typing import Optional

from core.mail_config import MailConfig
from crawler.core.crawler import Crawler
from crawler.core.exception import CrawlingException


class Covid19Crawler(Crawler):
    @staticmethod
    def get_covid_dict(bsoj):  # 누적, 소계, 국내발생, 해외유입 정보를 담은 딕셔너리 객체를 반환
        try:  # 여기서 에러 발생 가능
            base_date = bsoj.select_one("#content > div > h5:nth-of-type(1) > span").string.strip()  # 누적
            total_confirmed_cases = bsoj.select_one(
                "#content > div > div.caseTable > div:nth-of-type(1) > ul > li:nth-of-type(1) > dl > dd").string.strip()  # 누적
            national_occurrence = bsoj.select_one(
                "#content > div > div.caseTable > div:nth-of-type(1) > ul > li:nth-of-type(2) > dl > dd > ul > li:nth-of-type(2) > p").string.strip()  # 국내발생
            overseas_occurrence = bsoj.select_one(
                "#content > div > div.caseTable > div:nth-of-type(1) > ul > li:nth-of-type(2) > dl > dd > ul > li:nth-of-type(3) > p").string.strip()  # 해외발생
            daily_occurrence = bsoj.select_one(
                "#content > div > div.caseTable > div:nth-of-type(1) > ul > li:nth-of-type(2) > dl > dd > ul > li:nth-of-type(1) > p").string.strip()  # 소계
            # print(base_date)
            # print(daily_occurrence)
            # print(overseas_occurrence)
            # print(national_occurrence)
            # print(total_confirmed_cases)
        except AttributeError:
            raise CrawlingException("covid.py get_covid_dict에서 딕셔너리 객체에 Null 값이 담김!!")
        else:
            covid_dict = {'total': total_confirmed_cases, 'national': national_occurrence,
                          'overseas': overseas_occurrence,
                          'daily': daily_occurrence, 'date': base_date}
            return covid_dict

    @staticmethod
    @lru_cache(maxsize=None)
    def get_covid19_data() -> Optional[dict]:
        try:
            soup = Crawler.get_bsoj('http://ncov.mohw.go.kr/bdBoardList_Real.do?brdId=1&brdGubun=11')
            return Covid19Crawler.get_covid_dict(soup)
        except CrawlingException:
            traceback.print_exc()
            return None

    @staticmethod
    def get_mail_content(mail_config: MailConfig) -> str:
        Crawler.get_mail_content(mail_config)
        if not mail_config.covid19:
            return ''

        dict_data: Optional[dict] = Covid19Crawler.get_covid19_data()
        if dict_data is None:
            return '오늘의 코로나 국내 발생 현황을 불러오지 못했어요ㅜ\n'

        mail_content: str = "<코로나 국내 발생 현황> \n"
        mail_content += f"{dict_data['date']} 누적: {dict_data['total']}, 전일대비: {dict_data['daily']} [국내발생: {dict_data['national']}, 해외유입: {dict_data['overseas']}]\n"
        return mail_content


if __name__ == "__main__":
    print(Covid19Crawler.get_mail_content(MailConfig(covid19=True)))

"""
{'total': '83,525', 'national': '304', 'overseas': '22', 'daily': '+ 326', 'date': '(2.14. 00시 기준)'}
"""
