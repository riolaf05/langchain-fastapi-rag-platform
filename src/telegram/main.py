
import os
import telepot

TELEGRAM_CHAT_ID=os.getenv('TELEGRAM_CHAT_ID')
TELEGRAM_GROUP_ID=os.getenv('TELEGRAM_GROUP_ID')

def on_chat_message(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    if content_type == 'text':
        
        res = "ciao"
        # response = bot.sendPhoto(TELEGRAM_GROUP_ID, f)

        bot.sendMessage(chat_id, res)

bot = telepot.Bot(TELEGRAM_CHAT_ID)
bot.message_loop(on_chat_message)

print('Listening ...')

import time
while 1:
    time.sleep(10)