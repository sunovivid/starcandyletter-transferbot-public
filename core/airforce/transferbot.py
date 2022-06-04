import os
import re
import traceback
from typing import TYPE_CHECKING
from urllib import parse

import requests as requests

if TYPE_CHECKING:
    from core.soldier import AirForce, Soldier

from core.transferbot import TransferBot
from bs4 import BeautifulSoup

MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')


class SoldierNotFoundException(Exception):
    pass


class MailBoxNotOpenException(Exception):
    pass


class AirForceTransferBot(TransferBot):
    MAX_LENGTH = 1199

    METADATA = {
        "senderZipcode": "52634",
        "senderAddr1": "경상남도 진주시 금산면 송백로 46",
        "senderAddr2": "사서함",
        "senderName": "별사탕인편",
        "relationship": "인편지기",
        "title": "오늘의 별사탕인편",
        "prolog": "오늘 하루도 고된 훈련소 생활 수고 많으셨습니다! 하루를 마무리하며 오늘의 별사탕인편이 사회소식을 보내드립니다~!! ^^ ",
        "epilog": "오늘의 뉴스는 여기까지입니다! 하루하루 가다보면 어느새 수료가 눈앞으로 다가올 거예요! 화이팅입니다! 필승!",
        "password": MAIL_PASSWORD
    }

    @classmethod
    def send(cls: TransferBot, soldier: 'Soldier', content: str, **kwargs):
        content = AirForceTransferBot.METADATA['prolog'] + content + AirForceTransferBot.METADATA['epilog']
        with requests.Session() as s:
            mail_list_page_url = AirForceTransferBot._get_mail_list_page_url(soldier)
            mail_list_page_response = AirForceTransferBot._get_mail_list_page(mail_list_page_url, session=s)
            if '교육생의 인터넷 편지 작성 기간이 아닙니다' in mail_list_page_response.text:
                raise MailBoxNotOpenException("메일함이 아직 열리지 않았습니다.")
            for page in cls.paginate_content(content):
                cls.send_page(soldier, page, mail_list_page_url=mail_list_page_url,
                              mail_list_page_response=mail_list_page_response, session=s)

    @staticmethod
    def send_page(soldier: 'AirForce', page: str, **kwargs):
        mail_write_page_response = AirForceTransferBot._get_mail_write_page(kwargs['mail_list_page_url'],
                                                                            prev_response=kwargs[
                                                                                'mail_list_page_response'],
                                                                            session=kwargs['session'])
        http_request_body = AirForceTransferBot._create_request_form_data(AirForceTransferBot.METADATA, page)
        AirForceTransferBot._click_send_button(http_request_body, mail_write_page_response, session=kwargs['session'])

    @staticmethod
    def _create_request_form_data(metadata, content):
        default_form_data = {
            "siteId": "last2",
            "command2": "writeEmail",
        }
        form_data = {
            **default_form_data,
            **metadata,
            'contents': content
        }
        return form_data

    @staticmethod
    def _get_mail_list_page_url(soldier: 'Soldier'):
        _url = f"http://www.airforce.mil.kr:8081/user/indexSub.action?" \
               f"codyMenuSeq=156893223&siteId=last2&menuUIType=sub&dum=dum&command2=getEmailList" \
               f"&searchName={soldier.name}" \
               f"&searchBirth={soldier.birth_YYYYMMDD}" \
               f"&memberSeq={AirForceTransferBot._get_member_seq_by_name_and_birth(soldier)}"  # 247460901
        return AirForceTransferBot._encode_url(_url)

    @staticmethod
    def _get_mail_list_page(url, session):
        response = session.get(url)

        print("_get_mail_list_page: " + str(response))
        return response

    @staticmethod
    def _get_mail_write_page(mail_list_page_url, prev_response, session):
        additional_headers = {
            "Referer": mail_list_page_url  # referer가 지정되어야 요청시 편지쓰기 페이지로 이동하는듯!!
        }
        mail_write_page_url = "http://www.airforce.mil.kr:8081/user/indexSub.action?codyMenuSeq=156893223&siteId" \
                              "=last2&menuUIType=sub" \
                              "&dum=dum&command2=writeEmail&searchCate=&searchVal=&page=1"
        # 편지쓰기 페이지 접근시 referer, 세션 쿠키 필요
        mail_write_page_response = session.get(mail_write_page_url, cookies=prev_response.cookies,
                                               headers=additional_headers)

        print("_get_mail_write_page: " + str(mail_write_page_response))
        return mail_write_page_response

    @staticmethod
    def _click_send_button(data, prev_response, session):
        additional_headers = {
            "Referer": "http://www.airforce.mil.kr:8081/user/indexSub.action?codyMenuSeq=156893223&siteId=last2&menuUIType=sub&dum=dum&command2=writeEmail&searchCate=&searchVal=&page=1"
        }
        post_mail_url = "http://www.airforce.mil.kr:8081/user/emailPicSaveEmail.action"
        post_mail_response = session.post(post_mail_url, cookies=prev_response.cookies, headers=additional_headers,
                                          data=data)

        print("_click_send_button: " + str(post_mail_response))

    @staticmethod
    def _get_member_seq_by_name_and_birth(soldier: 'Soldier'):
        url = AirForceTransferBot._get_member_list_url(soldier)
        bs = AirForceTransferBot._get_bs(url)

        try:
            onclick_func = bs.body.li.input['onclick']  # TODO: li가 여러 개일때 처리 (생년월일과 이름 모두 같은 사람들이 존재하는 경우)
            pattern = re.compile('\d+')
            onclick_func_param = pattern.findall(onclick_func)[0]
            return onclick_func_param
        except TypeError as e:
            traceback.print_exc()
            raise SoldierNotFoundException(f'"{soldier.name}" (생년월일: {soldier.birth_iso})에 해당하는 군인을 찾을 수 없습니다.')

    @staticmethod
    def _get_member_list_url(soldier: 'Soldier') -> str:
        return f"http://airforce.mil.kr:8081/user/emailPicViewSameMembers.action?siteId=last2&searchName={soldier.name}&searchBirth={soldier.birth_YYYYMMDD}"

    @staticmethod
    def _get_bs(url):
        response = requests.get(url)
        response.raise_for_status()
        return BeautifulSoup(response.text, 'lxml')
        # TODO: 파이썬 라이브러리에 lxml 설치되어 있어야 함. 없으면 설치하거나 html.parser 사용

    @staticmethod
    def _encode_url(_url):
        p = parse.urlparse(_url)
        query = parse.parse_qs(p.query)
        return p.scheme + '://' \
               + p.netloc + p.path + p.params + '?' + parse.urlencode(query=query, doseq=True)
