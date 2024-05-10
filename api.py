import requests
import time
import logging
from json_work import read_file, write_file

from config import LOG_PATH, folder_id, metadata_url


class GET_IAM:
    
    def __init__(self):
        self.FOLDER_ID = folder_id
        logging.basicConfig(filename=LOG_PATH, level=logging.DEBUG, format="%(asctime)s %(message)s", filemode="w")
        self.headers = {"Metadata-Flavor": "Google"}
        self.metadata_url = metadata_url
        
    @staticmethod
    def create_token():
        try:
            response = requests.get(self.metadata_url, headers=self.headers)
            if response.status_code == 200:
                token_data = response.json()
                token_data["expires_at"] = time.time() + token_data["expires_in"]
                write_file(token_data)
                return token_data["access_token"]
            else:
                logging.error(f"Ошибка {response.status_code}")
        except:
            logging.error("Ошибка во время создания токена")

    def get_token(self):
        old_token_data = read_file()
        if old_token_data == {}:
            return self.create_token()
        if old_token_data["expires_at"] < time.time():
            return self.create_token()
        return old_token_data["access_token"]

            
class GPT(GET_IAM):
    def __init__(self, system_content="Ты - дружелюбная нейросеть", max_tokens=100, temperature=0.6):
        GET_IAM.__init__(self)
        self.MAX_TOKENS = max_tokens
        self.TEMPERATURE = temperature
        self.system_content = system_content 
        self.HEADERS = {
            "Authorization" : f"Bearer {self.get_token()}", 
            "Content-Type" : "application/json"
                        }
        
    def count_tokens(self, prompt):
        data = {
           "modelUri": f"gpt://{self.FOLDER_ID}/yandexgpt/latest", 
           "maxTokens": self.MAX_TOKENS,
           "text": prompt 
        }
        response = requests.post("https://llm.api.cloud.yandex.net/foundationModels/v1/tokenize", json=data, headers=self.HEADERS)
        error, text_error = self.error_resp(response)
        if not error:
            return False, text_error
        sum_tokens = len(response.json()["tokens"])
        if sum_tokens >= self.MAX_TOKENS:
            return False, "Текст слишком большой."
        return True, sum_tokens

    @staticmethod
    def error_resp(response):
        if response.status_code < 200 or response.status_code >= 300:
            logging.warning(response.status_code)
            return False, f"ошибка {response.status_code}."
        try:
            full_response = response.json()
        except:
            logging.warning("Пустой json")
            return False, "Возникла ошибка, повторите позже."
        if "error" in full_response:
            logging.warning(full_response)
            return False, "Возникла ошибка, повторите позже."
        return True, None

    def make_prompt(self, user_request, system_content):
        data = {
        "modelUri" : f"gpt://{self.FOLDER_ID}/yandexgpt-lite",
        "completionOptions" : {
            "stream" : False,
            "temperature" : self.TEMPERATURE,
            "maxTokens" : self.MAX_TOKENS
        },
        "messages" : [
            {"role" : "user", "text" : user_request},
            {"role" : "assistant", "text" : system_content},
            {"role" : "system", "text" : self.system_content}
            ]
        }
        return data

    def send_request(self, user_request, assistant_content):
        len_tokens, len_check = self.count_tokens(user_request)
        if not len_tokens:
            return len_check, 0
        data = self.make_prompt(user_request, assistant_content) 
        response = requests.post("https://llm.api.cloud.yandex.net/foundationModels/v1/completion", headers=self.HEADERS, json=data)
        error, text_error = self.error_resp(response)
        if not error:
            return text_error, 0
        result = response.json()["result"]["alternatives"][0]["message"]["text"]
        if result == "":
            return "Объяснение закончено.", len_check
        return result, len_check
            
    

            

