import requests
from typing import Callable, Dict, Any, Optional, List, Union

class Bot:
    def __init__(self, token: str):
        self.token = token
        self.api_url = f"https://api.telegram.org/bot{token}/"

    def _check_response(self, response: requests.Response) -> Any:
        data = response.json()
        if not data.get("ok"):
            raise Exception(f"Telegram API error: {data}")
        return data["result"]

    def get_updates(self, offset: Optional[int] = None, timeout: int = 30) -> list:
        params = {"timeout": timeout, "offset": offset}
        resp = requests.get(self.api_url + "getUpdates", params=params)
        return self._check_response(resp)

    def send_message(self, chat_id: int, text: str) -> dict:
        data = {"chat_id": chat_id, "text": text}
        resp = requests.post(self.api_url + "sendMessage", data=data)
        return self._check_response(resp)

    def _send_file(self, method: str, chat_id: int, file_field: str, file: Union[str, Any], caption: Optional[str] = None) -> dict:
        url = self.api_url + method
        files = {file_field: file} if hasattr(file, 'read') else None
        data = {"chat_id": chat_id}
        if caption:
            data["caption"] = caption
        if files:
            resp = requests.post(url, data=data, files=files)
        else:
            data[file_field] = file
            resp = requests.post(url, data=data)
        return self._check_response(resp)

    def send_photo(self, chat_id: int, photo: Union[str, Any], caption: Optional[str] = None) -> dict:
        return self._send_file("sendPhoto", chat_id, "photo", photo, caption)

    def send_document(self, chat_id: int, document: Union[str, Any], caption: Optional[str] = None) -> dict:
        return self._send_file("sendDocument", chat_id, "document", document, caption)

    def send_message_with_keyboard(self, chat_id: int, text: str, keyboard: list) -> dict:
        url = self.api_url + "sendMessage"
        reply_markup = {"keyboard": keyboard, "resize_keyboard": True}
        data = {"chat_id": chat_id, "text": text, "reply_markup": reply_markup}
        resp = requests.post(url, json=data)
        return self._check_response(resp)

    def send_inline_keyboard(self, chat_id: int, text: str, inline_keyboard: list) -> dict:
        url = self.api_url + "sendMessage"
        reply_markup = {"inline_keyboard": inline_keyboard}
        data = {"chat_id": chat_id, "text": text, "reply_markup": reply_markup}
        resp = requests.post(url, json=data)
        return self._check_response(resp)

    def run_polling(self, handler: Callable[[dict, 'Bot'], None]):
        offset = None
        while True:
            updates = self.get_updates(offset=offset)
            for update in updates:
                handler(update, self)
                offset = update["update_id"] + 1

class Dispatcher:
    def __init__(self):
        self.handlers: Dict[str, Callable[[dict, Bot], None]] = {}
        self.callback_handlers: Dict[str, Callable[[dict, Bot], None]] = {}

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

    @staticmethod
    def make_keyboard(buttons: List[Union[List[str], str]]) -> list:
        if buttons and isinstance(buttons[0], list):
            return [[{"text": text} for text in row] for row in buttons]
        else:
            return [[{"text": text} for text in buttons]]

class MessageHandler:
    def __init__(self, callback: Callable[[dict, Bot], None]):
        self.callback = callback

    def handle(self, message: dict, bot: Bot):
        self.callback(message, bot)
