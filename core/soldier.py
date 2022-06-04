from __future__ import annotations

import datetime

from core.airforce.transferbot import AirForceTransferBot
from core.army.transferbot import ArmyTransferBot
from core.mail_config import MailConfig


class Soldier:
    def __init__(self, uid: str, name: str, birth: datetime.date):
        self.mail_config: MailConfig = None
        self.uid = uid
        self.name = name
        self.birth = birth
        self.mail_content: str = ''

    def validate(self) -> Soldier:
        return self

    def get_mail_config_path(self) -> str:
        pass

    def send(self):
        pass

    def get_force_type(self) -> str:
        pass

    @property
    def birth_iso(self):
        return self.birth.isoformat()

    @property
    def birth_YYYYMMDD(self):
        return self.birth.strftime('%Y%m%d')

    def __str__(self):
        return f'[{self.force_type}] {self.name}({self.birth_iso})'


class AirForce(Soldier):
    def __init__(self, uid: str, name: str, birth: datetime.date, kisu: int):
        super().__init__(uid, name, birth)
        self.kisu = kisu

    def get_mail_config_path(self) -> str:
        return f'data/공군/{self.kisu}/{self.uid}'

    @property
    def force_type(self):
        return '공군'

    def send(self):
        AirForceTransferBot.send(self, self.mail_content)


class Army(Soldier):
    def __init__(self, uid: str, name: str, birth: datetime.date, enter_date: datetime.date, unit_code: str):
        super().__init__(uid, name, birth)
        self.enter_date = enter_date
        self.unit_code = unit_code

    def validate(self):
        return self

    def get_mail_config_path(self) -> str:
        return f'data/육군/{self.enter_date.isoformat()}/{self.uid}'

    def send(self):
        ArmyTransferBot.send(self, self.mail_content)

    @property
    def force_type(self):
        return '육군'
