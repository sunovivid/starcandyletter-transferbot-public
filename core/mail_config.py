from __future__ import annotations

import traceback
from typing import List, Dict

'''
class Market:
    def __init__(self, market_code: str, stock_codes: List):
        self.market_code: str = market_code
        self.stock_codes: List = stock_codes


class CountryCodePair:
    def __init__(self, left: str, right: str):
        self.left = left
        self.right = right
'''


class MailConfig:
    def __init__(self, news: bool = True,
                 stock: Dict[List[str]] = None,
                 exchange_rate: List[str] = None,
                 weather: bool = False,
                 covid19: bool = False,
                 random_namuwiki: bool = False,
                 sports: bool = False):
        self.news = news
        self.stock = stock or []
        self.exchange_rate = exchange_rate or []
        self.weather = weather
        self.covid19 = covid19
        self.random_namuwiki = random_namuwiki
        self.sports = sports

    @classmethod
    def fromDict(cls, dict: dict) -> MailConfig:
        if 'exchangeRates' in dict:
            dict['exchange_rate'] = dict['exchangeRates']
            dict.__delitem__('exchangeRates')
        # dict.__delitem__('exchangeRate')
        # dict = convert_dict_key(dict, from, to) #TODO: 이거 구현 (exchangeRate -> exchange_rate)
        try:
            return MailConfig(**dict)
        except TypeError as e:
            print('잘못된 키가 발견되었습니다.')
            traceback.print_exc()
            return MailConfig()
