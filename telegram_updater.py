import logging

# from interfaces.telegram import TelegramUpdaterInterface
from aiogram import executor

from interfaces.telegram import TelegramAsyncInterface

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)
interface = TelegramAsyncInterface()


def main():
    executor.start_polling(interface.dispatcher, skip_updates=True)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        exit()
