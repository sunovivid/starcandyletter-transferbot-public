import os
from datetime import datetime
from typing import Callable
from typing import TYPE_CHECKING

from core.army import thecampy
from core.army.thecampy.models import Soldier as TheCampArmy
from core.transferbot import TransferBot

if TYPE_CHECKING:
    from core.soldier import Army

EMAIL = os.getenv('THECAMP_ADMIN_EMAIL')
PASSWORD = os.getenv('THECAMP_ADMIN_PASSWORD')

toint: Callable[[datetime.date], int] = lambda x: int(x.strftime('%Y%m%d'))


class ArmyTransferBot(TransferBot):
    MAX_LENGTH = 1499

    @staticmethod
    def send_page(soldier: 'Army', page: str, **kwargs):
        soldier = TheCampArmy(soldier.name, toint(soldier.birth), toint(soldier.enter_date), soldier.unit_code)
        msg = thecampy.Message('오늘의 별사탕인편', page)
        tc = thecampy.Client(EMAIL, PASSWORD)
        tc.get_soldier(soldier)
        tc.send_message(soldier, msg, None)
