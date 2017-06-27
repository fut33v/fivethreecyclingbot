# coding=utf-8
import re

from util import bot_util
from telegram_bot.telegram_bot import TelegramBot
import os

__author__ = 'fut33v'

DATA_DIRNAME = "data/"
TOKEN_FILENAME = DATA_DIRNAME + "token"
ALBUMS_FILENAME = DATA_DIRNAME + 'albums'
ADMIN_FILENAME = DATA_DIRNAME + 'admin'

admins = None
if os.path.exists(ADMIN_FILENAME):
    with open(ADMIN_FILENAME) as admins_file:
        lines = admins_file.readlines()
        if lines:
            admins = list()
            for line in lines:
                admins.append(line[:-1])
            admins = set(admins)


REGEXP_ALBUM = re.compile("http[s]?://vk.com/album(-?\d*_\d*)")


class FiveThreeCyclingBot(TelegramBot):
    def __init__(self, token, name):
        TelegramBot.__init__(self, token, name)

    def _process_message(self, user_id, chat_id, text):
        if text == '/start' or text == '/start@FiveThreeCyclingBot':
            response = """
Присылаю новые посты по хештегу #53cycling
            """
        else:
            response = ""
        if response:
            success = self.send_response(chat_id, response=response)
            return success
        return False

if __name__ == "__main__":
    t = bot_util.read_one_string_file(TOKEN_FILENAME)
    bot = FiveThreeCyclingBot(t, name="fivethreecyclingbot")
    bot.start_poll()
