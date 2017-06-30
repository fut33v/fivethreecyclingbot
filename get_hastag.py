# coding=utf-8

import json

import fivethreecyclingbot
from broadcast import broadcast_message
from util import bot_util
import time

_TOKEN_VK_FILENAME = fivethreecyclingbot.DATA_DIRNAME + 'token_vk'
_TOKEN_VK = bot_util.read_one_string_file(_TOKEN_VK_FILENAME)
_LAST_ITEM_FILENAME = fivethreecyclingbot.DATA_DIRNAME + 'last_item'

_NEWSFEED_SEARCH_URL = "https://api.vk.com/method/newsfeed.search?q=%2353cycling&rev=1&v=5.63&access_token={t}".format(
    t=_TOKEN_VK)

_HASHTAGS = ["53cycling", "novgorodbike"]

def get_newsfeed_search_hashtag_url(hashtag):
    return "https://api.vk.com/method/newsfeed.search?q=%23{h}&rev=1&v=5.63&access_token={t}".format(
        t=_TOKEN_VK, h=hashtag)


def build_wall_url(owner_id, post_id):
    return "https://vk.com/wall{o}_{i}".format(o=owner_id, i=post_id)


def build_message(hashtag):
    url = get_newsfeed_search_hashtag_url(hashtag)
    response_text = bot_util.urlopen(url)
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
    last_item_filename = _LAST_ITEM_FILENAME + "_" + hashtag
    last_item_in_file = bot_util.read_one_string_file(last_item_filename)
    if not last_item_in_file or last_item_url != last_item_in_file:
        bot_util.write_one_string_file(last_item_filename, last_item_url)
        print "New post: " + last_item_url
        print last_item
        message = ""
        if 'attachments' in last_item:
            attachments = last_item['attachments']
            photo_url = None
            for attachment in attachments:
                if 'photo' in attachment:
                    photo = attachment['photo']
                    if 'photo_1280' in photo:
                        photo_url = photo['photo_1280']
                    break
            if photo_url:
                print photo_url
                message += photo_url + "\n\n"
        owner_id = last_item['owner_id']
        if 'text' in last_item:
            text = last_item['text']
            message += text + "\n\n"
        message += u"Пост: " + last_item_url + "\n"
        if owner_id > 0:
            message += u"Автор: https://vk.com/id" + str(owner_id)
        else:
            message += u"Автор: https://vk.com/club" + str(owner_id)
        return message
    else:
        print "There is no new posts for #" + hashtag
    return None


if __name__ == "__main__":
    while True:
        for h in _HASHTAGS:
            m = build_message(h)
            broadcast_message(m)
        time.sleep(30)
        print "tick"
