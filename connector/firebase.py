import os
from datetime import date, timedelta
from typing import List
from typing import OrderedDict

import pyrebase

from connector.dbconnector import DBConnector
from core.mail_config import MailConfig
from core.soldier import Soldier, AirForce, Army

EMAIL = os.getenv('ADMIN_EMAIL')
PASSWORD = os.getenv('ADMIN_PASSWORD')

API_KEY = os.getenv('FIREBASE_API_KEY')
AUTH_DOMAIN = os.getenv('FIREBASE_AUTH_DOMAIN')
DATABASE_URL = os.getenv('FIREBASE_DATABASE_URL')


def _is_empty(query_get_result):
    return query_get_result.pyres == []


class NoTargetAirForceKisuException(Exception):
    pass


class FirebaseConnector(DBConnector):
    def __init__(self):
        pyrebase.pyrebase.quote = lambda s: s  # pyrebase order_by_key 안되는 이슈 해결
        config = {
            "apiKey": API_KEY,
            "authDomain": AUTH_DOMAIN,
            "databaseURL": DATABASE_URL,
            "storageBucket": "",
        }
        self.firebase = pyrebase.initialize_app(config)
        self.db = self.firebase.database()
        self.bind_login_token_on_db_get_func()

    def bind_login_token_on_db_get_func(self):
        '''관리자 계정으로 로그인후 로그인 토큰 받아와서
        db.get() 메서드를 token 인자를 채운 메서드로 교체한다'''
        self.auth = self.firebase.auth()
        user = self.auth.sign_in_with_email_and_password(EMAIL, PASSWORD)

        self.db.original_get = self.db.get

        def get_with_token(**kwargs):
            return self.db.original_get(token=user['idToken'], **kwargs)

        self.db.get = get_with_token

    def get_target_soldiers(self) -> List[Soldier]:
        return [*self._get_target_army(), *self._get_target_airforce()]

    def get_mail_config(self, soldier: Soldier) -> MailConfig:
        mail_config_path: str = soldier.get_mail_config_path()
        mail_config_dict: dict = self.db.child(mail_config_path).get().val()
        if mail_config_dict is None:
            return MailConfig()
        mail_config: MailConfig = MailConfig.fromDict(mail_config_dict)
        return mail_config

    def _get_target_airforce(self) -> List[AirForce]:
        try:
            kisu: int = self._get_target_kisu()
            target_af_dict: OrderedDict = self.db.child('users').order_by_child('forceType').equal_to(
                '공군').order_by_child('kisu').equal_to(kisu).get().val()
            target_af: List[AirForce] = list(map(self._dict_item_to_airforce, target_af_dict.items()))
            print(f'공군 인편 발송 대상자 불러오기 완료: size = {target_af.__len__()}')
            return target_af
        except NoTargetAirForceKisuException as e:
            print(e)
            return []

    def _dict_item_to_airforce(self, item):
        key, value = item
        return AirForce(uid=key, name=value['name'], birth=date.fromisoformat(value['birth']), kisu=value['kisu'])

    def _get_target_kisu(self):
        MAIL_OPEN_DELAY_DATE: timedelta = timedelta(days=7 * 2)  # 2주차 화요일부터 발송가능 -> 입영일 + "8일"
        MAIL_END_DATE: timedelta = timedelta(days=7 * 4 + 2)  # 5주간 교육한다고 가정

        target_kisu_query_result = self.db.child('target').child('공군') \
            .order_by_value() \
            .start_at(f'{date.today() - MAIL_END_DATE}') \
            .end_at(f'{date.today() - MAIL_OPEN_DELAY_DATE}') \
            .get()
        if _is_empty(target_kisu_query_result):
            raise NoTargetAirForceKisuException("인편 발송 대상 기수가 없습니다.")
        target_kisu_dict = target_kisu_query_result.val()
        return [*target_kisu_dict.keys()][0]

    def _get_target_army(self) -> List[Army]:
        # 육군 중 [ 입영일 + 인편 열린날 <= 오늘 <= 입영일 + 인편 닫히는날 ] 인 사람 필터링해 리턴
        army_dict_items = self.db.child('users').order_by_child('forceType').equal_to('육군').get().val().items()
        target_army_dict_items: List[dict] = list(filter(self._is_target_army, army_dict_items))
        target_army: List[Army] = list(map(self._dict_item_to_army, target_army_dict_items))
        print(f'육군 인편 발송 대상자 불러오기 완료: size = {target_army.__len__()}')
        return target_army

    def _is_target_army(self, item: dict) -> bool:
        key, value = item
        MAIL_OPEN_DELAY_DATE: timedelta = timedelta(days=8)  # 2주차 화요일부터 발송가능 -> 입영일 + "8일"
        MAIL_END_DATE: timedelta = timedelta(days=7 * 5)  # 5주간 교육한다고 가정
        enter_date: date = date.fromisoformat(value['enterDate'])
        return (date.today() >= enter_date + MAIL_OPEN_DELAY_DATE) and (date.today() <= enter_date + MAIL_END_DATE)

    def _dict_item_to_army(self, item: dict) -> Army:
        key, value = item
        return Army(uid=key, name=value['name'], birth=date.fromisoformat(value['birth']),
                    enter_date=date.fromisoformat(value['enterDate']), unit_code=value['unitName'])
