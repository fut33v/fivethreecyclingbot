# coding=utf-8

import json

import fivethreecyclingbot
from broadcast import broadcast_message
from util import bot_util
import time

_HASH_FILENAME = fivethreecyclingbot.DATA_DIRNAME + 'hash'
_TOKEN_VK_FILENAME = fivethreecyclingbot.DATA_DIRNAME + 'token_vk'
_TOKEN_VK = bot_util.read_one_string_file(_TOKEN_VK_FILENAME)
_LAST_ITEM_FILENAME = fivethreecyclingbot.DATA_DIRNAME + 'last_item'

_NEWSFEED_SEARCH_URL = "https://api.vk.com/method/newsfeed.search?q=%2353cycling&rev=1&v=5.63&access_token={t}".format(
    t=_TOKEN_VK)


def build_wall_url(owner_id, post_id):
    return "https://vk.com/wall{o}_{i}".format(o=owner_id, i=post_id)


def build_message():
    response_text = bot_util.urlopen(_NEWSFEED_SEARCH_URL)
    if not response_text:
        print "Failed to get data from VK"
        return None
    response_json = json.loads(response_text)
    if 'response' not in response_json:
        print "No 'response' in response"
        print response_json
        return None
    response = response_json['response']
    if 'items' not in response:
        print "No 'items' in 'response'"
        return None
    items = response['items']
    if len(items) == 0:
        print "Length of 'items' is zero"
        return None
    last_item = items[0]
    if 'owner_id' not in last_item and 'id' not in last_item:
        print "No 'owner_id' and 'id' in item"
        return None
    last_item_url = build_wall_url(last_item['owner_id'], last_item['id'])
    last_item_in_file = bot_util.read_one_string_file(_LAST_ITEM_FILENAME)
    if not last_item_in_file or last_item_url != last_item_in_file:
        bot_util.write_one_string_file(_LAST_ITEM_FILENAME, last_item_url)
        print "New post: " + last_item_url
        return last_item_url
    else:
        print "There is no new posts"
    return None


if __name__ == "__main__":
    while True:
        message = build_message()
        broadcast_message(message)
        time.sleep(30)
        print "tick"
