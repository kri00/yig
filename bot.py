import telebot
from creds import TOKEN
from validators import send_gpt, send_stt, send_tts, check_limits
from database import SQlite

bot = telebot.TeleBot(TOKEN)
sql = SQlite()

@bot.message_handler(commands=["start"])
def start(message):
    user_id = message.from_user.id
    bot.send_message(user_id, "Привет! Это чат-бот для общения на тему книг, звучит удивительно, но нейросети справляются. Ты можешь отправлять сообщения как текстом, так и голосовым сообщением.")
    bot.send_message(user_id, "Ты можешь проверить функционал по командам /stt и /tts.\nПрисылай сообщение в виде текста или аудио, а я отвечу тем же)")
   
@bot.message_handler(commands=["help"])
def help(message):
    user_id = message.from_user.id
    bot.send_message(user_id, "Ты можешь проверить функционал по командам /stt и /tts.\nПрисылай сообщение в виде текста или аудио, а я отвечу тем же)")

@bot.message_handler(commands=["debug"])
def debug(message):
    with open(LOG_PATH, "rb") as f:
        bot.send_document(user_id, f)

#проверка функций stt и tts.
@bot.message_handler(commands=["stt"])
def check_stt(message):
    user_id = message.from_user.id
    bot.send_message(user_id, "Пришли голосовое сообщение.")
    bot.register_next_step_handler(message, check)

@bot.message_handler(commands=["tts"])
def check_tts(message):
    user_id = message.from_user.id
    bot.send_message(user_id, "Пришли текст.")
    bot.register_next_step_handler(message, check)

def check(message):
    user_id = message.from_user.id
    if message.text:
        voice, tokens_tts = send_tts(message.text, user_id)
        bot.send_voice(user_id, voice)
    elif message.voice:
        #сохраняем голосовое сообщение для дальнейшей обработки.
        file_id = message.voice.file_id 
        file_info = bot.get_file(file_id) 
        file = bot.download_file(file_info.file_path)
        text, blocks = send_stt(file, message.voice.duration, user_id)
        bot.send_message(user_id, text)

#функция для обработки текста.
@bot.message_handler(content_types=["text"])
def send_message(message):
    user_id = message.from_user.id
    if not message.text:
        return
    #проверка на лимиты токенов.
    if not check_limits("num_users", user_id):
        bot.send_message(user_id, "Очередь, попробуйте позже.")
        return
    #отправляем промпт.
    answer, tokens_gpt = send_gpt(message.text, user_id)
    bot.send_message(user_id, answer)
    #сохраняем данные.
    sql.insert_data([user_id, message.text, "user", 0, 0, 0])
    sql.insert_data([user_id, answer, "assistant", 0, 0, tokens_gpt])

#функция для обработки аудио.
@bot.message_handler(content_types=["voice"])    
def send_voice(message):
    user_id = message.from_user.id
    if not message.voice:
        return
    #проверка на лимиты токенов.
    if not check_limits("num_users", user_id):
        bot.send_message(user_id, "Очередь, выполните запрос позже.")
        return
    #сохраняем голосовое сообщение(гс) для дальнейшей обработки.
    file_id = message.voice.file_id 
    file_info = bot.get_file(file_id) 
    file = bot.download_file(file_info.file_path)
    #отправляем промпт.
    text, blocks = send_stt(file, message.voice.duration, user_id)
    #сохраняем данные.
    sql.insert_data([user_id, text, "user", blocks, 0, 0])
    #проверяем, если гс не превратилось в текст и/или возникла ошибка
    #не отправляем запрос гпт и не прибавляем токены гпт.
    if blocks == 0:
        tokens_gpt = count_gpt_tokens(self, user_id)
    else:
        text, tokens_gpt = send_gpt(text, user_id)
    #отправляем запрос на превращение текста в гс.
    voice, tokens_tts = send_tts(text, user_id)
    #сохраняем данные.
    sql.insert_data([user_id, text, "assistant", 0, tokens_tts, tokens_gpt])
    try:
        bot.send_voice(user_id, voice)
    except:
        bot.send_message(user_id, voice)


if __name__ == '__main__':
    bot.infinity_polling()  
