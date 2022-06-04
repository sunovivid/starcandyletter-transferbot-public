import requests as requests
from bs4 import BeautifulSoup

from core.mail_config import MailConfig
from crawler.core.exception import CrawlingException


class NoConfigurationException(Exception):
    pass


class Crawler:
    @staticmethod
    def get_bsoj(url):  # 뉴스 메인 페이지 beautifulSoup객체 리턴
        # 안티크롤링을 막기 위해 헤더값을 추가해줌
        try:
            response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
            # 200ok가 아니면 error발생
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            raise CrawlingException(f'Connection Error: {e.errno}')
        else:
            soup = BeautifulSoup(response.text, 'lxml')
            return soup

    @staticmethod
    def get_mail_content(mail_config: MailConfig):
        if mail_config is None:
            raise NoConfigurationException('MailConfig 객체가 None입니다.')
