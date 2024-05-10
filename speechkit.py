import requests
import math
import logging
from yandex_gpt import GET_IAM
from config import folder_id

iam = GET_IAM()
get_token = iam.get_token()

class STT(GET_IAM):
    def __init__(self):
        GET_IAM.__init__(self)

    def count_tokens(self, duration):
        if duration >= 30:
            return False, "SpeechKit STT работает с голосовыми сообщениями меньше 30 секунд"
        audio_blocks = math.ceil(duration/15)
        return True, audio_blocks
        
    def make_prompt(self):
        headers = {
        'Authorization': f'Bearer {get_token}',
                    }
        params = "&".join([
            "topic=general",
            f"folderId={folder_id}",
            "lang=ru-RU"
            ])
        return headers, params

    def send_request(self, data, duration):
        len_tokens, len_check = self.count_tokens(duration)
        if not len_tokens:
            return len_check, 0
        headers, params = self.make_prompt()
        response = requests.post(f"https://stt.api.cloud.yandex.net/speech/v1/stt:recognize?{params}", headers=headers, data=data).json()
        if response.get("error_code") is None:
            return response.get("result"), len_check 
        return f'При запросе в SpeechKit возникла ошибка: {response.get("error_code")}', 0


class TTS(GET_IAM):
    def __init__(self, max_tokens=500):
        GET_IAM.__init__(self)
        self.MAX_TOKENS = max_tokens

    def count_tokens(self, text):
        sum_tokens = len(text)
        if sum_tokens >= self.MAX_TOKENS:
            return False, "Текст слишком большой."
        return True, sum_tokens

    def make_prompt(self, text):
        headers = {
            'Authorization': f'Bearer {get_token}',
                    }
        data = {
            'text': text, 
            'lang': 'ru-RU',  
            'voice': 'filipp',  
            'folderId': folder_id,
        }
        return headers, data

    def send_request(self, text):
        if text == "":
            return "Пустой текст, введите что-нибудь, если хотите, чтобы это было озвучено."
        len_tokens, len_check = self.count_tokens(text)
        if not len_tokens:
            return len_check, 0
        headers, data = self.make_prompt(text)
        response = requests.post("https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize", headers=headers, data=data)
        if response.status_code < 200 or response.status_code >= 300:
            logging.warning(response.status_code)
            return f"ошибка {response.status_code}.", 0
        return response.content, len_check
