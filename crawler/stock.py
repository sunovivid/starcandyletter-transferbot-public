import traceback
from functools import lru_cache
from typing import Optional

from bs4 import BeautifulSoup

from core.mail_config import MailConfig
from crawler import stockname
from crawler.core.crawler import Crawler
from crawler.core.exception import CrawlingException

"""
stock_code = 'AAPL'
stock_market = 'NASDAQ'
나스닥(NASDAQ)의 경우 stock_code는 숫자(string)이 아니라 영어(string)이다.
"""


class StockCrawler(Crawler):
    @staticmethod
    def _get_bsoj(stock_code: str, stock_market: str) -> BeautifulSoup:  # stock_code를 받아서 beautifulSoup객체 리턴
        prefix = ''
        if stock_market == "KS":
            postfix = '.KS'  # 코스피
        elif stock_market == "NASDAQ":
            postfix = ''
        elif stock_market == "KQ":
            postfix = '.KQ'  # 코스닥
        else:
            raise CrawlingException("처리되지 않은 예외")
        url = 'https://finance.yahoo.com/quote/' + stock_code + postfix
        return Crawler.get_bsoj(url)

    @staticmethod
    def get_currency(info_string):  # 문자열을 받아 문자열 2개 리턴
        currency = ''
        if info_string.find('KRW') != -1:
            currency = 'KRW'
        elif info_string.find('USD') != -1:
            currency = 'USD'
        else:
            raise CrawlingException("통화 단위 인식 불가 예외")

        cut_index = info_string.find('watchlist') + 9  # 다쓴 정보는 자르기
        if (info_string.find('watchlist') == -1):
            raise CrawlingException("watchlist 찾기 불가")
        shortened_string = info_string[cut_index:]

        return currency, shortened_string  # 통화 string과 필요한 나머지 string만 잘라서 리턴

    @staticmethod
    def get_end_price(info_string):  # string 인자 받아서 종가 string 리턴
        cut_index = 0
        if info_string.find('+') != -1:  # 전일대비 올랐는지 떨어졌는지 확인
            cut_index = info_string.find('+')
            end_price = info_string[:cut_index]
            shortened_string = info_string[cut_index:]
        elif info_string.find('-') != -1:
            cut_index = info_string.find('-')
            end_price = info_string[:cut_index]
            shortened_string = info_string[cut_index:]
        elif info_string.rfind("0.00 (") != -1:
            cut_index = info_string.rfind("0.00 (")
            end_price = info_string[:cut_index]
            shortened_string = info_string[cut_index:]
        else:
            raise CrawlingException("전일대비 변동 확인하는 부분에서 예외 발생")

        return end_price, shortened_string

    @staticmethod
    def get_difs(info_string):
        cut_start_index = info_string.find('(')  # '('을 찾아서 인덱스 저장
        cut_finish_index = info_string.find(')')  # ')'을 찾아서 인덱스 저장
        # if(cut_start_index == -1):
        #     raise CrawlingException("cut_start_index 찾기 실패")
        # elif(cut_finish_index == -1):
        #     raise CrawlingException("cut_finish_index 찾기 실패")
        dif_vol = info_string[:cut_start_index - 1]
        dif_rate = info_string[cut_start_index + 1:cut_finish_index]
        dif_vol = dif_vol.strip()  # 혹시 몰라서 앞뒤 공백 제거
        dif_rate = dif_rate.strip()  # 혹시 몰라서 앞뒤 공백 제거
        return dif_vol, dif_rate

    @staticmethod
    def get_processed_dict(info_string: str) -> dict:  # 문자열을 읽어들여 통화,종가,변동가,변동비 데이터를 가지고 있는 딕셔너리 객체를 리턴
        currency, shortened_string = StockCrawler.get_currency(info_string)  # 둘다 문자열임
        end_price, shortened_string = StockCrawler.get_end_price(shortened_string)
        dif_vol, dif_rate = StockCrawler.get_difs(shortened_string)
        if currency == "KRW":
            info_dict = {'currency': currency, 'end_price': "(₩)" + end_price, 'dif_volume': "(₩)" + dif_vol,
                         'dif_rate': dif_rate}
        elif currency == "USD":
            info_dict = {'currency': currency, 'end_price': "($)" + end_price, 'dif_volume': "($)" + dif_vol,
                         'dif_rate': dif_rate}
        else:
            raise CrawlingException("딕셔너리 만드는 부분에서 오류 발생")
        return info_dict

    @staticmethod
    def get_info(bsoj: BeautifulSoup) -> str:  # bsoj 객체 받아서 string 형식의 필요정보 리턴
        raw_info = bsoj.text
        start_index = raw_info.find("Currency in")
        if (start_index == -1):
            raise CrawlingException("해당 종목코드에 해당하는 주식 정보를 찾을 수 없음")
        finish_index = raw_info.find(")At close:")  # 아마 마감했을때는 이렇게 뜨는듯
        if finish_index == -1:
            finish_index = raw_info.find(")As of  ")  # 장중일때는 이렇게 뜨고-->이게 문제였던듯
            if finish_index == -1:
                raise CrawlingException("finish_index를 찾을 수 없음")

        processed_info = raw_info[start_index:finish_index + 1]

        return processed_info

    @staticmethod
    @lru_cache(maxsize=None)
    def get_stock_data_dict(stock_code, stock_market) -> Optional[dict]:  # 이거 실행시키기 리턴값으로 딕셔너리 반환
        try:
            soup: BeautifulSoup = StockCrawler._get_bsoj(stock_code, stock_market)
            info_string: str = StockCrawler.get_info(soup)
            info_dict: dict = StockCrawler.get_processed_dict(info_string)
            return info_dict
        except CrawlingException:
            traceback.print_exc()
            return None

    @staticmethod
    def get_mail_content(mail_config: MailConfig) -> str:
        Crawler.get_mail_content(mail_config)
        if not mail_config.stock:
            return ''

        mail_content: str = '<주가 정보> \n'
        for market_code, stock_codes in mail_config.stock.items():
            for stock_code in stock_codes:
                stock_data: dict = StockCrawler.get_stock_data_dict(stock_code, market_code)
                if stock_data is None:
                    mail_content += f'[{market_code}] 종목코드 = {stock_code} 에 해당하는 주식이 없어요ㅜ\n'
                    continue
                mail_content += f"[{market_code} {stockname.get_stock_name_by_stock_code(market_code, stock_code)} {stock_code}] " \
                                f"종가: {stock_data['end_price']}, " \
                                f"전일비: {stock_data['dif_volume']}, " \
                                f"등락률: {stock_data['dif_rate']}\n"
        return mail_content


if __name__ == '__main__':
    print(StockCrawler.get_stock_data_dict('005930', 'KS'))
