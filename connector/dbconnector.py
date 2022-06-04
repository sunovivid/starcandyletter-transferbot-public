from typing import List

from core.mail_config import MailConfig
from core.soldier import Soldier


class DBConnector:
    def __init__(self):
        pass

    def get_target_soldiers(self) -> List[Soldier]:
        pass

    def get_mail_config(self, soldier: Soldier) -> MailConfig:
        pass

    def generate_mail_content(self, soldier: Soldier) -> Soldier:
        pass
