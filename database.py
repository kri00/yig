import sqlite3
import logging
from config import LOG_PATH

class SQlite:

    def __init__(self, db_name="database.db"):
        logging.basicConfig(filename=LOG_PATH, level=logging.DEBUG, format="%(asctime)s %(message)s", filemode="w")
        self.db_name = db_name

    def create_table(self):
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                query_table = '''
                    CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER,
                    message TEXT,
                    role TEXT,
                    stt_blocks INTEGER,
                    tts_tokens INTEGER,
                    gpt_tokens INTEGER)
                '''
                cursor.execute(query_table)
        except Exception as e:
             logging.error(f"Error: {e}")
        
    def insert_data(self, values):
        self.create_table()
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                query = "INSERT INTO messages user_id, message, role, stt_blocks , tts_tokens , gpt_tokens VALUES (?, ?, ?, ?, ?, ?)"
                cursor.execute(query, (values))
                conn.commit()
        except Exception as e:
            logging.error(f"Error: {e}")

    def count_data(self, column, user_id):
        self.create_table()
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute(f'''SELECT SUM({column}) FROM messages WHERE user_id=?''', (user_id,))
                data = cursor.fetchone()
                if data and data[0]:
                    return data[0] 
                else:
                    return 0 
        except Exception as e:
            logging.error(f"Error: {e}")

    def count_users(self, user_id):
        self.create_table()
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute('''SELECT COUNT(DISTINCT user_id) FROM messages WHERE user_id <> ?''', (user_id,))
                count = cursor.fetchone()[0]
                if count is None: count = 0
                return count
        except Exception as e:
            logging.error(f"Error: {e}")

    def count_gpt_tokens(self, user_id):
        self.create_table()
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute('''SELECT gpt_tokens FROM messages WHERE user_id=? ORDER BY id DESC LIMIT 1''', (user_id,))
                data = cursor.fetchall()
                if data == []: data = [0]
                return data[0]
        except Exception as e:
            logging.error(e)

    def select_last_messages(self, user_id, n_last_messages=10):
        self.create_table()
        messages = " "
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute('''SELECT message FROM messages WHERE user_id=? ORDER BY id DESC LIMIT ?''', (user_id, n_last_messages,))   
                data = cursor.fetchall()
                if data and data[0]:
                    for message in data:
                        if  message[0] is not None:
                            messages += message[0]
            return messages
        except Exception as e:
            logging.error(e)
            return messages
                    
    
