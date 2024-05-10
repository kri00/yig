from yandex_gpt import GPT
from speechkit import STT, TTS
from database import SQlite

sql = SQlite()
stt = STT()
gpt = GPT(system_content="Ты книгоман, обсуждаешь к людьми книги. Не говори о себе. Ты женского пола.")
tts = TTS()
limits = {"gpt_tokens" : 2000, "tts_tokens" : 2000, "stt_blocks" : 12, "num_users" : 3}

def check_limits(name, user_id):
    #считаем токены и проверяем на лимит. 
    if name == "gpt_tokens":
        count = sql.count_gpt_tokens(user_id)
    elif name == "num_users":
        count = sql.count_users(user_id)
    else:
        count = sql.count_data(name, user_id)
    if count >= limits[name]:
        return False
    return True

#делаем проверку, отправляем запрос и возвращаем ответ с количеством токенов.
def send_gpt(text, user_id):
    if not check_limits("gpt_tokens", user_id):
        return "Вы превысили лимит."
    answer, tokens = gpt.send_request(text, assistant_content=sql.select_last_messages(user_id))
    tokens += sql.count_gpt_tokens(user_id)
    return answer, tokens

def send_tts(text, user_id):
    if not check_limits("tts_tokens", user_id):
        return "Вы превысили лимит."
    answer, tokens = tts.send_request(text)
    return answer, tokens

def send_stt(file, duration, user_id):
    if not check_limits("stt_blocks", user_id):
        return "Вы превысили лимит."
    answer, blocks = stt.send_request(file, duration)
    if answer == "":
        return "Пустое аудиосообщение.", blocks
    return answer, blocks
