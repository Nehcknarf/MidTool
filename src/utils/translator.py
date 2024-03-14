import json
from typing import Optional

import PySide6
from PySide6.QtCore import QTranslator


class JsonTranslator(QTranslator):
    def __init__(self, parent: Optional[PySide6.QtCore.QObject] = ...) -> None:
        super().__init__()
        self.translations = {}

    def load(self, data: bytes, directory: str = ...) -> bool:
        try:
            with open(data, 'r', encoding='utf-8') as f:
                self.translations = json.load(f)
        except Exception as e:
            return False
        else:
            return True

    def translate(self, context: bytes, sourceText: bytes, disambiguation: Optional[bytes] = ..., n: int = ...) -> str:
        translation = self.translations.get(sourceText, sourceText)
        return translation
