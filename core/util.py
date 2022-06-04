import traceback
from typing import List

from connector import firebase
from connector.dbconnector import DBConnector
from core.soldier import Soldier
from crawler.core.crawler import Crawler
from crawler.covid19 import Covid19Crawler
from crawler.currency import CurrencyCrawler
from crawler.news import NewsCrawler
from crawler.stock import StockCrawler


class TransferUtil:
    def __init__(self):
        self.db_connector: DBConnector = firebase.FirebaseConnector()

    def get_target_soldiers(self) -> List[Soldier]:
        return self.db_connector.get_target_soldiers()

    def validate(self, soldier) -> bool:
        return isinstance(soldier, Soldier)

    def get_mail_config(self, soldier: Soldier) -> Soldier:
        print(f'{soldier}의 인편 설정 불러오기 시작')
        soldier.mail_config = self.db_connector.get_mail_config(soldier)
        print(f'{soldier}의 인편 설정 불러오기 완료')
        return soldier

    def generate_mail_content(self, soldier: Soldier) -> Soldier:
        print(f'{soldier}의 메일 내용 생성 시작')
        crawlers: List[Crawler] = [NewsCrawler, StockCrawler, CurrencyCrawler, Covid19Crawler]
        for crawler in crawlers:
            soldier.mail_content += crawler.get_mail_content(soldier.mail_config)
        print(f'{soldier}의 메일 내용 생성 완료')
        return soldier

    def send(self, soldier: Soldier):
        try:
            print(f'{soldier}의 메일 발송 시작')
            soldier.send()
            print(f'{soldier}의 메일 발송 완료\n')
        except Exception as e:
            print('메일 발송 중 에러가 발생했습니다.')
            print(e)
            traceback.print_exc()
