from typing import List

from dotenv import load_dotenv

load_dotenv(verbose=True)

from core.soldier import Soldier
from core.util import TransferUtil


def print_line(title):
    print('\n' + '-' * 20 + ' ' + title + ' ' + '-' * 20)


util = TransferUtil()
print_line('인편 설정 불러오기')
target_soldiers: List[Soldier] = util.get_target_soldiers()[:5]
print_line('validate')
target_soldiers = list(filter(util.validate, target_soldiers))
print_line('get_mail_config')
target_soldiers = list(map(util.get_mail_config, target_soldiers))
print_line('generate_mail_content')
target_soldiers = list(map(util.generate_mail_content, target_soldiers))
print_line('send')
# target_soldiers = list(map(util.send, target_soldiers))
