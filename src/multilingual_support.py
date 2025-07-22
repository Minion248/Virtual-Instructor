from deep_translator import GoogleTranslator
from typing import List, Union


class MultilingualSupport:
    def __init__(self):
        self.default_language = "ur"

    def translate_text(self, text: str, dest_language: str = None) -> str:
        """
        Translate a single text string to the specified language.

        :param text: Text to translate
        :param dest_language: Language code to translate into (default is Urdu)
        :return: Translated string or error message
        """
        dest_language = dest_language or self.default_language
        try:
            return GoogleTranslator(source='auto', target=dest_language).translate(text)
        except Exception as e:
            return f"Translation error: {str(e)}"

    def translate_multiple(self, texts: Union[List[str], str], dest_language: str = None) -> Union[List[str], str]:
        """
        Translate a list of texts or a single string to the specified language.

        :param texts: A list of text strings or a single string
        :param dest_language: Language code to translate into
        :return: A list of translated texts or a single translated string
        """
        dest_language = dest_language or self.default_language

        if isinstance(texts, str):
            return self.translate_text(texts, dest_language)

        translated_list = []
        for text in texts:
            translated_list.append(self.translate_text(text, dest_language))
        return translated_list
