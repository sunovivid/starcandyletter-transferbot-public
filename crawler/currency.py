import traceback
from functools import lru_cache
from typing import List, Optional

from bs4 import BeautifulSoup

from core.mail_config import MailConfig
# first_currency = "USD"
# last_currency = "KRW"
from crawler.core.crawler import Crawler
from crawler.core.exception import CrawlingException


class CurrencyCrawler(Crawler):
    @staticmethod
    def get_exchange_rate(bsoj):  # bsoj 객체 받아서 해당 환율의 날짜 string 형식으로 리턴
        try:
            rate = bsoj.select_one("body > div > table > tbody > tr:nth-of-type(1) > td:nth-of-type(2)")
            return rate.string.strip()
        except AttributeError:
            raise CrawlingException

    @staticmethod
    def get_diff_dict(
            bsoj):  # bsoj객체를 받아서 키-값 두쌍을 가지고 있는 딕셔너리 객체를 리턴함(하나는 올라갔는지 내려갔는지를 표현, 다른 하나는 그 값을 표현:둘다 string 형식)
        # 하향, 상향, 보합에 해당하는 기능
        up_or_down = ''
        diff_volume = ''  # 숫자를 string 형태로 지정(,가 들어있는 형식으로 리턴)
        diff_price_up_down = \
            bsoj.select_one("body > div > table > tbody > tr:nth-of-type(1) > td:nth-of-type(3) > img").attrs[
                'alt']  # string 형식임. '하락','상승','보합'
        if diff_price_up_down is None:
            raise CrawlingException

        # 전일 대비 하락인지 상승인지 보합인지
        if diff_price_up_down == "하락":
            up_or_down = 'up'
        elif diff_price_up_down == "상승":
            up_or_down = 'down'
        elif diff_price_up_down == "보합":
            up_or_down = 'same'
        else:
            raise CrawlingException

        # 전일 대비 변동가 알아내는 구간
        diff_price_raw = bsoj.select_one("body > div > table > tbody > tr:nth-of-type(1) > td:nth-of-type(3)")
        if diff_price_raw is None:
            raise CrawlingException

        try:
            diff_volume = diff_price_raw.next.next.string.strip()
        except AttributeError:
            raise CrawlingException
        else:
            # 딕셔너리 형태로 만들기
            diff_dict = {'up_or_down': up_or_down, 'diff_volume': diff_volume}
            return diff_dict

    @staticmethod
    def get_date(bsoj):  # bsoj 객체 받아서 해당 환율의 날짜 string 형식으로 리턴
        try:
            date = bsoj.select_one("body > div > table > tbody > tr:nth-of-type(1) > td.date")
            return date.string.strip()
        except AttributeError:
            raise CrawlingException

    @staticmethod
    def _get_bsoj(first_currency, last_currency) -> BeautifulSoup:
        url = 'https://finance.naver.com/marketindex/exchangeDailyQuote.nhn?marketindexCd=FX_' + first_currency + last_currency
        return Crawler.get_bsoj(url)

    @staticmethod
    @lru_cache(maxsize=None)
    def get_final_dict(first_currency, last_currency) -> Optional[dict]:  # 최종 딕셔너리를 얻기 위한 함수
        try:
            bsoj = CurrencyCrawler._get_bsoj(first_currency, last_currency)
            date = CurrencyCrawler.get_date(bsoj)
            exchange_rate = CurrencyCrawler.get_exchange_rate(bsoj)
            diff_dict = CurrencyCrawler.get_diff_dict(bsoj)
            final_dict = diff_dict
            final_dict['date'] = date
            final_dict['exchange_rate'] = exchange_rate
            return final_dict
        except CrawlingException:
            traceback.print_exc()
            return None

    @staticmethod
    def get_mail_content(mail_config: MailConfig):
        Crawler.get_mail_content(mail_config)
        exchange_rate_list: List[str] = mail_config.exchange_rate
        if not exchange_rate_list:
            return ''

        content = "<환율 정보> \n"
        for rate in exchange_rate_list:
            first_currency, last_currency = rate.split('-')
            dict_data = CurrencyCrawler.get_final_dict(first_currency=first_currency, last_currency=last_currency)
            if dict_data is None:
                content += f'{rate} 환율 정보를 불러올 수 없어요ㅜ\n'
                continue
            if dict_data['up_or_down'] == 'up':
                content += f"{dict_data['date']} 기준 {rate} 환율: {dict_data['exchange_rate']}, 전일대비: +{dict_data['diff_volume']}\n"
            elif dict_data['up_or_down'] == 'down':
                content += f"{dict_data['date']} 기준 {rate} 환율: {dict_data['exchange_rate']}, 전일대비: -{dict_data['diff_volume']}\n"
            elif dict_data['up_or_down'] == 'same':
                content += f"{dict_data['date']} 기준 {rate} 환율: {dict_data['exchange_rate']}, 전일대비: {dict_data['diff_volume']}\n"
        return content


if __name__ == '__main__':
    print(CurrencyCrawler.get_mail_content(MailConfig(exchange_rate=['USD-KRW'])))
