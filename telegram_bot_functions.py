import requests
from tokens import *
import os
import csv
import tweepy

global users
users = {}

def parser(message):
    txt = ""
    chat_id = ""
    if 'message' in message.keys():
        chat_id, txt = message['message']['chat']['id'], message['message']['text']
        print(str(chat_id) + ": " + str(txt))
    elif 'callback_query' in message.keys():
        chat_id, txt = message['callback_query']['from']['id'], message['callback_query']['data']
        print(str(chat_id) + ": " + str(txt))
    return chat_id, txt


def txt_to_text(directory):
    with open(directory, encoding="utf-8") as f:
        lines = f.readlines()
    text = ''
    for line in lines:
        text += line
    return text


def csv_to_list(directory):
    id_list = []
    with open(directory, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            if len(row) != 0:
                id_list.append(int(row[0]))
    return id_list


def add_csv_id(chat_id, directory):
    with open(directory, 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([chat_id])


def remove_csv_id(chat_id, directory):
    id_list = []
    with open(directory, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            id_list.append(int(row[0]))
    id_list.remove(chat_id)
    with open(directory, 'w', newline="") as file:
        writer = csv.writer(file)
        for id in id_list:
            writer.writerow([id])


def tel_send_message(chat_id, text):
    url = f'https://api.telegram.org/bot{TelegramToken}/sendMessage'
    payload = {'chat_id': chat_id, 'text': text}
    r = requests.post(url, json=payload)
    return r


def tel_send_inline_button(chat_id, text, type):
    url = f'https://api.telegram.org/bot{TelegramToken}/sendMessage'
    if type == "list":
        entries = os.listdir('./lists/')
        inline_keyboard = []
        for entry in entries:
            if entry[-3:] == 'csv':
                inline_keyboard.append([{"text": 'Block (mute) ' + entry[:-4], "callback_data": 'Block' + entry[:-4]}, {"text": 'Unblock (unmute) ' + entry[:-4], "callback_data": 'Unblock' + entry[:-4]}])
        inline_keyboard.append([{"text": "بلاک (میوت) همه", "callback_data": "BlockAll"}, {"text": "آنبلاک (آنمیوت) همه", "callback_data": "UnblockAll"}])
        payload = {
            'chat_id': chat_id,
            'text': text,
            'reply_markup': {
                "inline_keyboard": inline_keyboard
            }
        }
        r = requests.post(url, json=payload)
    elif type == "yes_or_no":
        payload = {
            'chat_id': chat_id,
            'text': text,
            'reply_markup': {
                "inline_keyboard": [[
                    {
                        "text": "بله",
                        "callback_data": "/yes"
                    },
                    {
                        "text": "خیر",
                        "callback_data": "/no"
                    }]
                ]
            }
        }
        r = requests.post(url, json=payload)
    elif type == "block_and_mute":
        payload = {
            'chat_id': chat_id,
            'text': text,
            'reply_markup': {
                "inline_keyboard": [[
                    {
                        "text": "بلاک و میوت",
                        "callback_data": "/block_and_mute"
                    },
                    {
                        "text": "بلاک",
                        "callback_data": "/block"
                    }]
                ]
            }
        }
        r = requests.post(url, json=payload)
    return r


def request_token(chat_id, bot):
    try:
        authorization_url = users[chat_id]['bots'][bot]['oauth'].get_authorization_url()
        state = authorization_url
        state = state.replace("&", " ")
        state = state.replace("?", " ")
        state = state.replace("=", " ")
        state = state.split(" ")[10]
    except:
        tel_send_message(chat_id, "خطایی پیش آمده لطفن دوباره تلاش کنید.")
        return ""

    tel_send_message(chat_id, f"لینک {bot}:\n\n%s" % authorization_url)
    return state


def block(block_id_list, chat_id):
    tel_send_message(chat_id, f"شما در حال بلاک کردن یک لیست {len(block_id_list)} نفره هستید.\n\nدر هر 15 دقیقه 100 نفر بلاک و یا 200 نفر بلاک و میوت میشوند. بعدش بات کمی صبر میکنه تا 15 دقیقه تموم بشه و دوباره همین فرآیند تکرار میشه.\n\nهر 10000 نفر که بلاک شد، بهتون خبر میدیم.")
    count = 0
    for block_id in block_id_list:
        if count % 50 == 0:
            bot = "bot"+str(int(count/50) % len(users[chat_id]['bots'])+1)
        if count % 700 == 0:
            for bot_name in users[chat_id]["bots"]:
                token_data = users[chat_id]["bots"][bot_name]["oauth"].refresh_token('https://api.twitter.com/2/oauth2/token')
                access_token = token_data['access_token']
                users[chat_id]["bots"][bot_name]["client"] = tweepy.Client(access_token, wait_on_rate_limit=True)
        if users[chat_id]["running"] == False:
            tel_send_message(chat_id, f"فرآیند استاپ شد!")
            users.pop(chat_id)
            return
        if users[chat_id]["method"] == "block":
            try:
                users[chat_id]["bots"][bot]["client"].block(block_id, user_auth=False)
            except BaseException as e:
                print(".........................................")
                print(f"{chat_id} - {bot} : count={count}, id={block_id}, error={e}")
        else:
            if count % 2 == 0:
                try:
                    users[chat_id]["bots"][bot]["client"].block(block_id, user_auth=False)
                except BaseException as e:
                    print(".........................................")
                    print(f"{chat_id} - {bot} : count={count}, id={block_id}, error={e}")
            else:
                try:
                    users[chat_id]["bots"][bot]["client"].mute(block_id, user_auth=False)
                except BaseException as e:
                    print(".........................................")
                    print(f"{chat_id} - {bot} : count={count}, id={block_id}, error={e}")
        # blocked names
        if users[chat_id]["showing_name"] == True:
            try:
                blocked_name = users[chat_id]['bots'][bot]["client"].get_user(id=block_id)[0]["username"]
                tel_send_message(chat_id, f"یوزر {blocked_name} کِ کِ شد!")
            except BaseException as e:
                print(f"{chat_id} - {bot} : count={count}, id={block_id}, error={e}")
        count += 1
        if count % 10000 == 0:
            tel_send_message(chat_id, f"تا الان{count} نفر بلاک (و یا میوت) شدن!")
    tel_send_message(chat_id, f"لیست تمام شد!")
    users.pop(chat_id)


def unblock(block_id_list, chat_id):
    tel_send_message(chat_id, f"شما در حال آنبلاک و آنمیوت کردن یک لیست {len(block_id_list)} نفره هستید.\n\nدر هر 15 دقیقه 100 نفر آنبلاک و آنمیوت میشوند. بعدش بات کمی صبر میکنه تا 15 دقیقه تموم بشه و دوباره همین فرآیند تکرار میشه.\n\nهر 10000 نفر که آنبلاک و آنمیوت شد، بهتون خبر میدیم.")
    count = 0
    for block_id in block_id_list:
        if count % 50 == 0:
            bot = "bot"+str(int(count/50) % len(users[chat_id]['bots'])+1)
        if count % 700 == 0:
            for bot_name in users[chat_id]["bots"]:
                token_data = users[chat_id]["bots"][bot_name]["oauth"].refresh_token('https://api.twitter.com/2/oauth2/token')
                access_token = token_data['access_token']
                users[chat_id]["bots"][bot_name]["client"] = tweepy.Client(access_token, wait_on_rate_limit=True)
        if users[chat_id]["running"] == False:
            tel_send_message(chat_id, f"فرآیند استاپ شد!")
            users.pop(chat_id)
            return
        try:
            users[chat_id]["bots"][bot]["client"].unblock(block_id, user_auth=False)
        except BaseException as e:
            print(".........................................")
            print(f"{chat_id} - {bot} : count={count}, id={block_id}, error={e}")
        try:
            users[chat_id]["bots"][bot]["client"].unmute(block_id, user_auth=False)
        except BaseException as e:
            print(".........................................")
            print(f"{chat_id} - {bot} : count={count}, id={block_id}, error={e}")
        # blocked names
        if users[chat_id]["showing_name"] == True:
            try:
                blocked_name = users[chat_id]['bots'][bot]["client"].get_user(id=block_id)[0]["username"]
                tel_send_message(chat_id, f"یوزر {blocked_name} آن کِ کِ شد!")
            except BaseException as e:
                print(f"{chat_id} - {bot} : count={count}, id={block_id}, error={e}")
        count += 1
        if count % 10000 == 0:
            tel_send_message(chat_id, f"تا الان{count} نفر آنبلاک (و یا آنمیوت) شدن!")
    tel_send_message(chat_id, f"لیست تمام شد!")
    users.pop(chat_id)
