import html
from singleton_decorator import singleton
from google.cloud import translate


@singleton
class Translate:
    def __init__(self):
        self.client = translate.TranslationServiceClient()
        self.parent = f"projects/PROJECT NAME/locations/global"

    def translate_to_eng(self, user_msg: str) -> str:
        response = self.client.translate_text(
            request={
                "parent": self.parent,
                "contents": [user_msg],
                "mime_type": "text/plain",
                "source_language_code": "es",
                "target_language_code": "en-US",
            }
        )

        translated_text = response.translations[0].translated_text
        translated_text = html.unescape(translated_text)
        return translated_text

    def translate_to_spa(self, user_msg: str) -> str:
        response = self.client.translate_text(
            request={
                "parent": self.parent,
                "contents": [user_msg],
                "mime_type": "text/plain",
                "source_language_code": "en-US",
                "target_language_code": "es",
            }
        )

        translated_text = response.translations[0].translated_text
        translated_text = html.unescape(translated_text)
        return translated_text


if __name__ == "__main__":
    t = Translate()
    print(t.translate_to_spa('hello my friend'))
    print(t.translate_to_eng('¿qué hago después?'))
