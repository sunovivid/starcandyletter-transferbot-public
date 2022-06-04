import traceback
import urllib.parse
from functools import lru_cache, reduce
from typing import List

from core.mail_config import MailConfig
from crawler.core.crawler import Crawler
from crawler.core.exception import CrawlingException

# 입력할 뉴스 개수
NEWS_MAX_NUMBER = 8


class NewsCrawler(Crawler):
    @staticmethod
    def pick_news_list(bsoj):  # 하이라이트 뉴스 url링크 리스트 형식으로 리턴
        news_list = []
        # base Url
        base_url = 'https://news.naver.com/'
        # 하이라이트 뉴스들 모여있는 li들 조사
        news = bsoj.select("ul.press_ranking_list > li")
        # news_list 리스트에 string 형식으로 각 기사의 url 넣기
        if news is None:
            return CrawlingException
        for li in news:
            try:
                article_tag = li.select_one("a").attrs['href']
            except AttributeError:
                raise CrawlingException
            sub_url = article_tag
            full_url = urllib.parse.urljoin(base_url, sub_url)
            news_list.append(full_url)

        return news_list

    @staticmethod
    def get_sum_url(url):  # 해당 기사의 url을 받아서 그 기사의 요약페이지 url을 string 형식으로 리턴함
        """
        본문링크:https://n.news.naver.com/article/052/0001747565?ntype=RANKING
        요약링크:https://tts.news.naver.com/article/052/0001747565/summary
        """
        try:
            oid, raw_aid = url.split('/')[4:6]  # ['052', '0001747565?ntype=RANKING']
            aid = raw_aid.split('?')[0]  # '0001747565'
            return f'https://tts.news.naver.com/article/{oid}/{aid}/summary'
        except Exception:
            raise CrawlingException("url 변환 실패 ")

    @staticmethod
    def read_news_sum(bsoj):  # 뉴스 요약 기사를 string 형식으로 리턴
        sum_text_raw = bsoj.text
        index = sum_text_raw.find("summary")
        if (index == -1):
            raise CrawlingException
        sum_text_raw = sum_text_raw[index + 10:]  # summary: 앞까지 자르기
        sum_text_raw = sum_text_raw[:len(sum_text_raw) - 2]  # "}자르기
        sum_text = sum_text_raw.replace("\\", '')

        return sum_text

    @staticmethod
    def analyze_news(bsoj) -> List[str]:  # 기사 요약 string 리스트 형식으로 리턴
        news_list = NewsCrawler.pick_news_list(bsoj)[:NEWS_MAX_NUMBER]
        article_sum_list = []
        for li in news_list:
            sum_url = NewsCrawler.get_sum_url(
                li)  # 요약페이지의 링크를 받아옴 "https://tts.news.naver.com/article/003/0010307406/summary"
            soup = NewsCrawler.get_bsoj(sum_url)  # 요약페이지의 soup객체 받기
            sum_article = NewsCrawler.read_news_sum(soup)
            article_sum_list.append(sum_article)

        return article_sum_list

    @staticmethod
    @lru_cache(maxsize=None)
    def get_news() -> str:  # 이거 실행하면 됨
        naver_url = 'https://media.naver.com/press/052/ranking?type=popular'
        try:
            soup = NewsCrawler.get_bsoj(naver_url)
            return reduce(lambda acc, cur: acc + cur + ' / ', NewsCrawler.analyze_news(soup), '')
        except CrawlingException:
            traceback.print_exc()
            return ''

    @staticmethod
    def get_mail_content(mail_config: MailConfig) -> str:
        Crawler.get_mail_content(mail_config)
        if not mail_config.news:
            return ''

        mail_content: str = f'<헤드라인 뉴스> \n {NewsCrawler.get_news()} \n'
        return mail_content


if __name__ == "__main__":
    print(NewsCrawler.get_mail_content(MailConfig(news=True)))
