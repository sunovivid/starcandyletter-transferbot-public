from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.soldier import Soldier


class TransferBot:
    MAX_LENGTH = 0  # 인편 최대 글자수

    @classmethod
    def send(cls: TransferBot, user: Soldier, content: str, **kwargs):
        for page in cls.paginate_content(content):
            cls.send_page(user, page, **kwargs)

    @staticmethod
    def send_page(user, page, **kwargs):
        pass  # TODO: 추상 메소드로 만들기

    @classmethod
    def paginate_content(cls: TransferBot, content: str):
        return [content[cut_index: min(len(content), cut_index + cls.MAX_LENGTH)] for cut_index in
                range(0, len(content), cls.MAX_LENGTH)]
