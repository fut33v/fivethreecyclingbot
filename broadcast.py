# coding=utf-8

import fivethreecyclingbot
from util import bot_util

__author__ = 'fut33v'


def broadcast_message(message):
    t = bot_util.read_one_string_file(fivethreecyclingbot.TOKEN_FILENAME)
    bot = fivethreecyclingbot.FiveThreeCyclingBot(t, name="FiveThreeCyclingBot")
    lines = open(bot._chats_file, 'r').readlines()
    for l in lines:
        # l = int(l)
        bot.send_response(l, message, HTML=True)

if __name__ == "__main__":
    m = "test"
    broadcast_message(m)
