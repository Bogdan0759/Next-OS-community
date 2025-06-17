from src.telegrambotlib import Bot, MessageHandler
import time

TOKEN = 'ВАШ_ТОКЕН'
bot = Bot(TOKEN)

def echo_handler(message, bot):
    chat_id = message['chat']['id']
    text = message.get('text', '')
    bot.send_message(chat_id, f'Вы написали: {text}')

handler = MessageHandler(echo_handler)

if __name__ == '__main__':
    print('Бот запущен...')
    last_update_id = None
    while True:
        updates = bot.get_updates(offset=last_update_id)
        for update in updates:
            if 'message' in update:
                handler.handle(update['message'], bot)
                last_update_id = update['update_id'] + 1
        time.sleep(1)
