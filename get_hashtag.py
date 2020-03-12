# coding=utf-8

import json
import fivethreecyclingbot
from broadcast import broadcast_message
from util import bot_util
import time
import os


_TOKEN_VK_FILENAME = fivethreecyclingbot.DATA_DIRNAME + 'token_vk'
_TOKEN_VK = bot_util.read_one_string_file(_TOKEN_VK_FILENAME)
_LAST_ITEM_FILENAME = fivethreecyclingbot.DATA_DIRNAME + 'last_item'
_ALL_POSTS_FILENAME = fivethreecyclingbot.DATA_DIRNAME + 'posts'
_BANNED_FILENAME = fivethreecyclingbot.DATA_DIRNAME + 'banned'


_NEWSFEED_SEARCH_URL = "https://api.vk.com/method/newsfeed.search?q=%2353cycling&rev=1&v=5.63&access_token={t}".format(
    t=_TOKEN_VK)

_BANNED = []
if os.path.exists(_BANNED_FILENAME):
    _BANNED = bot_util.read_lines(_BANNED_FILENAME)
    _BANNED = [string.rstrip() for string in _BANNED]
    _BANNED = [string for string in _BANNED if string]
    print _BANNED
    _BANNED = map(int, _BANNED)


_HASHTAGS = ["53cycling", "novgorodbike"]
_53CYCLING_ID = -71413407
_53CYCLING_DOMAIN = "53cycling"


def get_newsfeed_search_hashtag_url(hashtag):
    return "https://api.vk.com/method/newsfeed.search?q=%23{h}&rev=1&v=5.63&access_token={t}".format(
        t=_TOKEN_VK, h=hashtag)


def get_wall_get_url(domain):
    return "https://api.vk.com/method/wall.get?domain={d}&v=5.63&access_token={t}".format(
        t=_TOKEN_VK, d=domain)


def build_wall_url(owner_id, post_id):
    return "https://vk.com/wall{o}_{i}".format(o=owner_id, i=post_id)


def build_users_get_url(_user_id):
    return "https://api.vk.com/method/users.get?user_ids={u}&fields=city&v=5.63".format(u=_user_id)


def get_user_info(_user_id):
    u = build_users_get_url(_user_id)
    response_text = bot_util.urlopen(u)
    if response_text:
        response_json = json.loads(response_text)
        if 'response' in response_json:
            response = response_json['response']
            if len(response) == 0:
                return None
            _user_info = response[0]
            first_name = ""
            last_name = ""
            city = ""
            if "first_name" in _user_info:
                first_name = _user_info["first_name"]
            if "last_name" in _user_info:
                last_name = _user_info["last_name"]
            if "city" in _user_info:
                if "title" in _user_info["city"]:
                    city = _user_info["city"]["title"]
            _user_info = {'first_name': first_name, 'last_name': last_name, 'city': city}
            return _user_info
    return None


def build_message(_hashtag):
    url = get_newsfeed_search_hashtag_url(_hashtag)
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
    if last_item['owner_id'] in _BANNED:
        return None

    print last_item['owner_id']
    print last_item

    last_item_url = build_wall_url(last_item['owner_id'], last_item['id'])
    last_item_filename = _LAST_ITEM_FILENAME + "_" + _hashtag
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
        if not bot_util.check_file_for_string(_ALL_POSTS_FILENAME, last_item_url + "\n"):
            return None
        else:
            bot_util.append_string_to_file(_ALL_POSTS_FILENAME, last_item_url + "\n")
        message += u"<b>Пост:</b> " + last_item_url + "\n"
        if owner_id > 0:
            user_info = get_user_info(owner_id)
            first_name = user_info['first_name']
            last_name = user_info['last_name']
            message += u"<b>Автор:</b> <a href=\"https://vk.com/id" + str(
                owner_id) + u"\">" + first_name + u" " + last_name + u"</a>"
        else:
            message += u"<b>Автор:</b> https://vk.com/club" + str(-owner_id)
        return message
    else:
        print "There is no new posts for #" + _hashtag
    return None


def sort_by_date(i):
    if 'date' not in i:
        return 0
    return i['date']


def build_message_cycling_wall():
    url = get_wall_get_url(_53CYCLING_DOMAIN)
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
    items.sort(key=sort_by_date, reverse=True)
    last_item = items[0]
    last_item_url = build_wall_url(last_item['owner_id'], last_item['id'])
    last_item_filename = _LAST_ITEM_FILENAME + "_" + _53CYCLING_DOMAIN + "_wall"
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
        if not bot_util.check_file_for_string(_ALL_POSTS_FILENAME, last_item_url + "\n"):
            return None
        else:
            bot_util.append_string_to_file(_ALL_POSTS_FILENAME, last_item_url + "\n")
        message += u"<b>Пост:</b> " + last_item_url + "\n"
        if owner_id > 0:
            user_info = get_user_info(owner_id)
            first_name = user_info['first_name']
            last_name = user_info['last_name']
            message += u"<b>Автор:</b> <a href=\"https://vk.com/id" + str(
                owner_id) + u"\">" + first_name + u" " + last_name + u"</a>"
        else:
            message += u"<b>Автор:</b> https://vk.com/club" + str(-owner_id)
        return message
    else:
        print "There is no new posts in community"
    return None


if __name__ == "__main__":
    while True:
        print "tick"
        for h in _HASHTAGS:
            m = build_message(h)
            if m is not None:
                broadcast_message(m)

            m = build_message_cycling_wall()
            if m is not None:
                broadcast_message(m)

            broadcast_message(m)
        time.sleep(300)
