import os
import time
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ParseMode, InputMediaPhoto, InputMediaVideo, ChatActions
from aiogram.types.inline_keyboard import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types.message import MessageEntity
from aiogram.dispatcher.filters import Text
from aiogram.types.message import ContentType
from aiogram.dispatcher.filters import Filter

from core import process_message
from interfaces.base import AsyncBotInterface


WELCOME_MSG = """🎧  Just send me an url from any streaming service

🎸 I can work in groups as well"""


class TelegramAsyncInterface(AsyncBotInterface):
    API_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
    ADMINS_CHAT = os.environ.get('BOT_ADMINS_CHAT')
    EXAMPLE_FILE_URL = os.getenv('EXAMPLE_MEDIA')

    def __init__(self):
        self.bot = Bot(self.API_TOKEN)
        self.dispatcher = Dispatcher(self.bot)
        self._init_handlers()

    def _init_handlers(self):
        self.dispatcher.register_message_handler(self._handle_message, content_types=ContentType.TEXT)
        self.dispatcher.register_callback_query_handler(self._handle_mismatch_button, lambda c: c.data == 'bad_response')

    @staticmethod
    def get_keyboard(message):
        if not TelegramAsyncInterface.ADMINS_CHAT:
            return

        message_id = message.message_id
        feedback_button = InlineKeyboardButton(text="report mismatch",
                                               callback_data='bad_response'.format(message_id))
        buttons = [[feedback_button]]
        return InlineKeyboardMarkup(inline_keyboard=buttons)

    async def _handle_message(self, message):
        text = message.text
        start = time.time()
        response = await process_message(text)
        end = time.time()

        print('Time elapsed: ', end - start)
        if response:
            response_keyboard = self.get_keyboard(message)
            await message.reply(
                response,
                reply=True,
                disable_web_page_preview=True,
                reply_markup=response_keyboard,
                parse_mode=ParseMode.MARKDOWN
            )

    async def _handle_mismatch_button(self, callback_query):
        if not TelegramAsyncInterface.ADMINS_CHAT:
            return
        await self.bot.answer_callback_query(callback_query.id, show_alert=True)
        await self.bot.forward_message(
            chat_id=self.ADMINS_CHAT,
            from_chat_id=callback_query.from_user.id,
            message_id=callback_query.message.message_id
        )
