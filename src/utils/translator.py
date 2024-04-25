import json

from PySide6.QtCore import QTranslator


class JsonTranslator(QTranslator):
    def __init__(self, parent=None):
        super().__init__()
        self.translations = {}

    def load(self, data, directory=...):
        try:
            with open(data, 'r', encoding='utf-8') as f:
                self.translations = json.load(f)
        except Exception as e:
            return False
        else:
            return True

    def translate(self, context, sourceText, disambiguation=..., n=...):
        translation = self.translations.get(sourceText, sourceText)
        return translation
