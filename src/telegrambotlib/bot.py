import requests
import logging
import time
from typing import Callable, Dict, Any, Optional, List, Union
from flask import Flask, request, jsonify
import threading
import sqlite3
from abc import ABC, abstractmethod
from apscheduler.schedulers.background import BackgroundScheduler
import functools

# === Кастомные исключения ===
class TelegramAPIError(Exception):
    def __init__(self, description: str, error_code: Optional[int] = None, response: Optional[dict] = None):
        self.description = description
        self.error_code = error_code
        self.response = response
        msg = f"Telegram API error {error_code}: {description}" if error_code else f"Telegram API error: {description}"
        super().__init__(msg)

# === Логирование ===
class BotLogger:
    def __init__(self, level=logging.INFO, enabled=True):
        self.enabled = enabled
        self.logger = logging.getLogger("TelegramBot")
        handler = logging.StreamHandler()
        formatter = logging.Formatter('[%(levelname)s] %(asctime)s %(message)s')
        handler.setFormatter(formatter)
        if not self.logger.handlers:
            self.logger.addHandler(handler)
        self.logger.setLevel(level)

    def log(self, level, msg):
        if self.enabled:
            self.logger.log(level, msg)

class Bot:
    def __init__(self, token: str, logger: Optional[BotLogger] = None, timeout: int = 10, max_retries: int = 3, backoff: float = 1.5):
        self.token = token
        self.api_url = f"https://api.telegram.org/bot{token}/"
        self.logger = logger or BotLogger()
        self.timeout = timeout
        self.max_retries = max_retries
        self.backoff = backoff

    def _request(self, method: str, http_method: str = "POST", **kwargs) -> Any:
        url = self.api_url + method
        for attempt in range(1, self.max_retries + 1):
            try:
                self.logger.log(logging.DEBUG, f"Request {http_method} {url} {kwargs}")
                if http_method == "POST":
                    resp = requests.post(url, timeout=self.timeout, **kwargs)
                else:
                    resp = requests.get(url, timeout=self.timeout, **kwargs)
                self.logger.log(logging.DEBUG, f"Response: {resp.status_code} {resp.text}")
                return self._check_response(resp)
            except (requests.RequestException, TelegramAPIError) as e:
                self.logger.log(logging.ERROR, f"Attempt {attempt}: {e}")
                if attempt == self.max_retries:
                    raise
                time.sleep(self.backoff ** attempt)

    def _check_response(self, response: requests.Response) -> Any:
        data = response.json()
        if not data.get("ok"):
            raise TelegramAPIError(data.get("description", "Unknown error"), data.get("error_code"), data)
        return data["result"]

    def get_updates(self, offset: Optional[int] = None, timeout: int = 30) -> list:
        params = {"timeout": timeout, "offset": offset}
        return self._request("getUpdates", http_method="GET", params=params)

    def send_message(self, chat_id: int, text: str) -> dict:
        data = {"chat_id": chat_id, "text": text}
        return self._request("sendMessage", data=data)

    def answer_callback_query(self, callback_query_id: str, text: Optional[str] = None, show_alert: bool = False) -> dict:
        data = {"callback_query_id": callback_query_id, "show_alert": show_alert}
        if text:
            data["text"] = text
        return self._request("answerCallbackQuery", data=data)

    def _send_file(self, method: str, chat_id: int, file_field: str, file: Union[str, Any], caption: Optional[str] = None) -> dict:
        files = {file_field: file} if hasattr(file, 'read') else None
        data = {"chat_id": chat_id}
        if caption:
            data["caption"] = caption
        if files:
            return self._request(method, data=data, files=files)
        else:
            data[file_field] = file
            return self._request(method, data=data)

    def send_photo(self, chat_id: int, photo: Union[str, Any], caption: Optional[str] = None) -> dict:
        return self._send_file("sendPhoto", chat_id, "photo", photo, caption)

    def send_document(self, chat_id: int, document: Union[str, Any], caption: Optional[str] = None) -> dict:
        return self._send_file("sendDocument", chat_id, "document", document, caption)

    def send_message_with_keyboard(self, chat_id: int, text: str, keyboard: list) -> dict:
        reply_markup = {"keyboard": keyboard, "resize_keyboard": True}
        data = {"chat_id": chat_id, "text": text, "reply_markup": reply_markup}
        return self._request("sendMessage", json=data)

    def send_inline_keyboard(self, chat_id: int, text: str, inline_keyboard: list) -> dict:
        reply_markup = {"inline_keyboard": inline_keyboard}
        data = {"chat_id": chat_id, "text": text, "reply_markup": reply_markup}
        return self._request("sendMessage", json=data)

    def run_polling(self, handler: Callable[[dict, 'Bot'], None]):
        offset = None
        while True:
            updates = self.get_updates(offset=offset)
            for update in updates:
                handler(update, self)
                offset = update["update_id"] + 1

    def answer_inline_query(self, inline_query_id: str, results: list, cache_time: int = 300, is_personal: bool = False) -> dict:
        data = {"inline_query_id": inline_query_id, "results": results, "cache_time": cache_time, "is_personal": is_personal}
        return self._request("answerInlineQuery", data=data)

    def send_audio(self, chat_id: int, audio: Union[str, Any], caption: Optional[str] = None) -> dict:
        return self._send_file("sendAudio", chat_id, "audio", audio, caption)

    def send_video(self, chat_id: int, video: Union[str, Any], caption: Optional[str] = None) -> dict:
        return self._send_file("sendVideo", chat_id, "video", video, caption)

    def send_voice(self, chat_id: int, voice: Union[str, Any], caption: Optional[str] = None) -> dict:
        return self._send_file("sendVoice", chat_id, "voice", voice, caption)

# === Webhook Server ===
class WebhookServer:
    def __init__(self, bot: Bot, dispatcher: 'Dispatcher', host: str = '0.0.0.0', port: int = 8443, ssl_context=None):
        self.bot = bot
        self.dispatcher = dispatcher
        self.host = host
        self.port = port
        self.ssl_context = ssl_context
        self.app = Flask(__name__)
        self.app.add_url_rule('/', 'webhook', self.handle_update, methods=['POST'])

    def handle_update(self):
        update = request.get_json()
        self.dispatcher.process_update(update, self.bot)
        return jsonify({'ok': True})

    def run(self):
        threading.Thread(target=self.app.run, kwargs={
            'host': self.host,
            'port': self.port,
            'ssl_context': self.ssl_context,
            'debug': False
        }, daemon=True).start()

    def set_webhook(self, url: str, certificate: Optional[str] = None):
        data = {"url": url}
        files = {"certificate": open(certificate, "rb")} if certificate else None
        return self.bot._request("setWebhook", data=data, files=files)

# === Storage Abstraction ===
class Storage(ABC):
    @abstractmethod
    def get(self, key: str) -> Any:
        pass
    @abstractmethod
    def set(self, key: str, value: Any):
        pass
    @abstractmethod
    def delete(self, key: str):
        pass

class SimpleMemoryStorage(Storage):
    def __init__(self):
        self.data = {}
    def get(self, key: str) -> Any:
        return self.data.get(key)
    def set(self, key: str, value: Any):
        self.data[key] = value
    def delete(self, key: str):
        if key in self.data:
            del self.data[key]

class SQLiteStorage(Storage):
    def __init__(self, db_path: str = 'botdata.db'):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.execute('CREATE TABLE IF NOT EXISTS kv (key TEXT PRIMARY KEY, value TEXT)')
    def get(self, key: str) -> Any:
        cur = self.conn.execute('SELECT value FROM kv WHERE key=?', (key,))
        row = cur.fetchone()
        return row[0] if row else None
    def set(self, key: str, value: Any):
        self.conn.execute('REPLACE INTO kv (key, value) VALUES (?, ?)', (key, value))
        self.conn.commit()
    def delete(self, key: str):
        self.conn.execute('DELETE FROM kv WHERE key=?', (key,))
        self.conn.commit()

# === Inline Query Support ===
class InlineQueryResult:
    @staticmethod
    def article(id: str, title: str, message_text: str, **kwargs) -> dict:
        return {"type": "article", "id": id, "title": title, "input_message_content": {"message_text": message_text}, **kwargs}
    @staticmethod
    def photo(id: str, photo_url: str, thumb_url: str, **kwargs) -> dict:
        return {"type": "photo", "id": id, "photo_url": photo_url, "thumb_url": thumb_url, **kwargs}

class Dispatcher:
    def __init__(self):
        self.handlers: Dict[str, Callable[[dict, Bot], None]] = {}
        self.callback_handlers: Dict[str, Callable[[dict, Bot], None]] = {}
        self.edited_handlers: List[Callable[[dict, Bot], None]] = []
        self.channel_post_handlers: List[Callable[[dict, Bot], None]] = []
        self.inline_query_handlers: List[Callable[[dict, Bot], None]] = []

    def command(self, cmd: str):
        def decorator(func: Callable[[dict, Bot], None]):
            self.handlers[f"/{cmd}"] = func
            return func
        return decorator

    def callback(self, data: str):
        def decorator(func: Callable[[dict, Bot], None]):
            self.callback_handlers[data] = func
            return func
        return decorator

    def on_edited_message(self, func: Callable[[dict, Bot], None]):
        self.edited_handlers.append(func)
        return func

    def on_channel_post(self, func: Callable[[dict, Bot], None]):
        self.channel_post_handlers.append(func)
        return func

    def on_inline_query(self, func: Callable[[dict, Bot], None]):
        self.inline_query_handlers.append(func)
        return func

    def process_update(self, update: dict, bot: Bot):
        if "message" in update:
            message = update["message"]
            text = message.get("text", "")
            if text:
                cmd = text.split()[0]
                if cmd in self.handlers:
                    self.handlers[cmd](message, bot)
        elif "callback_query" in update:
            data = update["callback_query"]["data"]
            if data in self.callback_handlers:
                self.callback_handlers[data](update["callback_query"], bot)
                # Подтверждение callback
                bot.answer_callback_query(update["callback_query"]["id"])
        elif "edited_message" in update:
            for func in self.edited_handlers:
                func(update["edited_message"], bot)
        elif "channel_post" in update:
            for func in self.channel_post_handlers:
                func(update["channel_post"], bot)
        elif "inline_query" in update:
            for func in self.inline_query_handlers:
                func(update["inline_query"], bot)

    @staticmethod
    def make_keyboard(buttons: List[Union[List[str], str]]) -> list:
        if buttons and isinstance(buttons[0], list):
            return [[{"text": text} for text in row] for row in buttons]
        else:
            return [[{"text": text} for text in buttons]]

    @staticmethod
    def make_inline_keyboard(buttons: List[List[Dict[str, Any]]]) -> list:
        return buttons

# === Заготовка для асинхронного клиента ===
class AsyncBot:
    """Заготовка для асинхронного Telegram-бота на aiohttp/httpx."""
    pass

# === Планировщик задач ===
class BotScheduler:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()
    def add_job(self, func, trigger, **kwargs):
        self.scheduler.add_job(func, trigger, **kwargs)
    def shutdown(self):
        self.scheduler.shutdown()

# === Утилиты для фильтров и лимитов ===
def is_group(message):
    return message.get('chat', {}).get('type') in ['group', 'supergroup']

def admin_only(admin_ids):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(message, bot, *args, **kwargs):
            if message['from']['id'] not in admin_ids:
                bot.send_message(message['chat']['id'], "Только для админов!")
                return
            return func(message, bot, *args, **kwargs)
        return wrapper
    return decorator

def rate_limit(seconds: int):
    user_last_call = {}
    def decorator(func):
        @functools.wraps(func)
        def wrapper(message, bot, *args, **kwargs):
            user_id = message['from']['id']
            now = time.time()
            last = user_last_call.get(user_id, 0)
            if now - last < seconds:
                return
            user_last_call[user_id] = now
            return func(message, bot, *args, **kwargs)
        return wrapper
    return decorator

def parse_args(func):
    @functools.wraps(func)
    def wrapper(message, bot, *args, **kwargs):
        parts = message.get('text', '').split(maxsplit=1)
        if len(parts) > 1:
            return func(message, bot, parts[1], *args, **kwargs)
        else:
            return func(message, bot, '', *args, **kwargs)
    return wrapper

def make_paginated_keyboard(items, page, page_size=5):
    start = page * page_size
    end = start + page_size
    buttons = [[{"text": item, "callback_data": f"item_{i}"}] for i, item in enumerate(items[start:end], start)]
    nav_buttons = []
    if page > 0:
        nav_buttons.append({"text": "⬅️ Назад", "callback_data": f"page_{page-1}"})
    if end < len(items):
        nav_buttons.append({"text": "➡️ Вперед", "callback_data": f"page_{page+1}"})
    if nav_buttons:
        buttons.append(nav_buttons)
    return buttons

# === Расширенный Dispatcher ===
class AdvancedDispatcher(Dispatcher):
    def __init__(self):
        super().__init__()
        self.any_message_handlers: List[Callable[[dict, Bot], None]] = []
        self.callback_prefix_handlers: Dict[str, Callable[[dict, Bot], None]] = {}
        self.stats_storage: Optional[Storage] = None

    def command(self, cmd: str, *, filters=None):
        def decorator(func):
            @functools.wraps(func)
            def wrapper(message, bot, *args, **kwargs):
                if filters:
                    for f in filters:
                        if not f(message):
                            return
                return func(message, bot, *args, **kwargs)
            self.handlers[f"/{cmd}"] = wrapper
            return wrapper
        return decorator

    def callback(self, data: str, prefix=False):
        def decorator(func):
            if prefix:
                self.callback_prefix_handlers[data] = func
            else:
                self.callback_handlers[data] = func
            return func
        return decorator

    def on_any_message(self, func: Callable[[dict, Bot], None]):
        self.any_message_handlers.append(func)
        return func

    def process_update(self, update: dict, bot: Bot):
        if "message" in update:
            message = update["message"]
            for func in self.any_message_handlers:
                func(message, bot)
            text = message.get("text", "")
            if text:
                cmd = text.split()[0]
                if cmd in self.handlers:
                    self.handlers[cmd](message, bot)
        elif "callback_query" in update:
            data = update["callback_query"]["data"]
            if data in self.callback_handlers:
                self.callback_handlers[data](update["callback_query"], bot)
                bot.answer_callback_query(update["callback_query"]["id"])
            else:
                for prefix, func in self.callback_prefix_handlers.items():
                    if data.startswith(prefix):
                        func(update["callback_query"], bot)
                        bot.answer_callback_query(update["callback_query"]["id"])
                        break
        elif "edited_message" in update:
            for func in self.edited_handlers:
                func(update["edited_message"], bot)
        elif "channel_post" in update:
            for func in self.channel_post_handlers:
                func(update["channel_post"], bot)
        elif "inline_query" in update:
            for func in self.inline_query_handlers:
                func(update["inline_query"], bot)

    def set_stats_storage(self, storage: Storage):
        self.stats_storage = storage

# === Inline редактирование сообщений ===
def edit_message_text(bot, chat_id, message_id, text, keyboard=None):
    data = {
        "chat_id": chat_id,
        "message_id": message_id,
        "text": text,
        "parse_mode": "HTML"
    }
    if keyboard:
        data["reply_markup"] = keyboard
    return bot._request("editMessageText", data=data)

# === Пример использования новых возможностей ===
"""
# Команда с аргументами
@dp.command("echo")
@parse_args
def echo_handler(message, bot, args):
    if args:
        bot.send_message(message['chat']['id'], args)
    else:
        bot.send_message(message['chat']['id'], "Нет аргументов!")

# Команда только для групп
@dp.command("grouponly", filters=[is_group])
def group_only_handler(message, bot):
    bot.send_message(message['chat']['id'], "Ты в группе, круто!")

# Rate limit
@dp.command("slow")
@rate_limit(10)
def slow_command(message, bot):
    bot.send_message(message['chat']['id'], "Ты не спамь!")

# Callback с префиксом
@dp.callback("vote_", prefix=True)
def vote_handler(callback_query, bot):
    data = callback_query['data']
    vote_id, choice = data.split('_')[1:]
    bot.answer_callback_query(callback_query['id'], f"Голос {choice} учтен!")

# Глобальный хендлер
@dp.on_any_message
def log_all(message, bot):
    print("Сообщение от", message['from'].get('username'), ":", message.get('text', ''))

# Пагинация
keyboard = make_paginated_keyboard([f"Item {i}" for i in range(20)], page=0)

# Команда только для админов
@dp.command("admincmd")
@admin_only([12345678, 87654321])
def admin_command(message, bot):
    bot.send_message(message['chat']['id'], "Ты админ!")

# Статистика
@dp.on_any_message
def count_messages(message, bot):
    count = int(dp.stats_storage.get('msg_count') or 0) + 1
    dp.stats_storage.set('msg_count', str(count))

@dp.command("stats")
def stats(message, bot):
    count = dp.stats_storage.get('msg_count') or "0"
    bot.send_message(message['chat']['id'], f"Всего сообщений: {count}")

# Inline редактирование
edit_message_text(bot, chat_id, message_id, "Новое сообщение", keyboard)

# /start с параметрами
@dp.command("start")
@parse_args
def start_handler(message, bot, param):
    if param:
        bot.send_message(message['chat']['id'], f"Ты пришёл с параметром: {param}")
    else:
        bot.send_message(message['chat']['id'], "Привет! Это старт.")
"""
