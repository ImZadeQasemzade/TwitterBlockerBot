# This Python file uses the following encoding: utf-8

from flask import Flask, request, Response
from telegram_bot_functions import *


app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        message = request.get_json()

        chat_id, txt = parser(message)

        if txt == "/start":
            try:
                if chat_id in users.keys():
                    users.pop(chat_id)
                with open('./settings/update.txt') as f:
                    lines = f.readlines()
                que = csv_to_list('./settings/que.csv')
                if 'on' in lines[0]:
                    tel_send_message(chat_id, "بات در حال بروز رسانی می باشد. لطفا بعدا تلاش کنید.")
                    return Response('ok', status=200)
                if len(users) >= int(lines[1][7:]):
                    tel_send_message(chat_id,
                                     "به دلیل محدودیت های سرور تعداد مشخصی همزمان میتونن از بات استفاده کنند. محدودیت استفاده از بات تکمیل شده است. شما در لیست قرار گرفته اید. به محض رسیدن نوبتتان، به شما اطلاع رسانی خواهد شد.")
                    if chat_id not in que:
                        add_csv_id(chat_id, './settings/que.csv')
                    return Response('ok', status=200)
                elif len(que) != 0:
                    tel_send_message(que[0], "ظرفیت باز شده است. لطفا زودتر از بات استفاده کنید.")
                    remove_csv_id(que[0], './settings/que.csv')

                text = txt_to_text('./settings/start.txt')
                tel_send_message(chat_id, text)
                users[chat_id] = {}
                users[chat_id]["bots"], users[chat_id]["showing_name"], users[chat_id]["running"], users[chat_id]["first_time"], users[chat_id]["method"] = {}, True, False, True, ""
                for bot in bots_token:
                    oauth2_user_handler = tweepy.OAuth2UserHandler(client_id=bots_token[bot]["CLIENT_ID"], redirect_uri="https://CyberArmyBlocker.ngrok.io", scope=["block.write", "offline.access", "users.read", "tweet.read", "mute.write"], client_secret=bots_token[bot]["CLIENT_SECRET"])
                    users[chat_id]['bots'][bot] = {'oauth': oauth2_user_handler, 'state': "", 'url': "", 'client': ""}
                for bot in users[chat_id]["bots"]:
                    users[chat_id]['bots'][bot]['state'] = request_token(chat_id, bot)
            except:
                return Response('ok', status=200)

        elif txt == "/stop":
            try:
                if chat_id in users.keys() and users[chat_id]["running"] == True:
                    users[chat_id]["running"] = False
                    tel_send_message(chat_id, "فرآیند بزودی استاپ می شود. کمی صبر کنید!")
                else:
                    tel_send_message(chat_id, "فرآیند استاپ شده است.")
                    try:
                        users.pop(chat_id)
                    except:
                        return Response('ok', status=200)
            except:
                return Response('ok', status=200)

        elif txt == "/help":
            try:
                text = txt_to_text('./settings/help1.txt')
                tel_send_message(chat_id, text)
                text = txt_to_text('./settings/help2.txt')
                tel_send_message(chat_id, text)
            except:
                return Response('ok', status=200)

        elif chat_id in users.keys():

            count_signed_bot = 0
            for bot_count in users[chat_id]["bots"]:
                if users[chat_id]["bots"][bot_count]['url'] != "":
                    count_signed_bot += 1

            if txt == "/block_and_mute" and users[chat_id]["first_time"] == True and count_signed_bot == len(users[chat_id]["bots"]):
                try:
                    users[chat_id]["method"] = "block_and_mute"
                    tel_send_inline_button(chat_id, 'اسامی بلاک شده ها نشان داده شود؟ این ویژگی را هر لحظه میتوانید از menu تغییر دهید.', "yes_or_no")
                except:
                    return Response('ok', status=200)

            elif txt == "/block" and users[chat_id]["first_time"] == True and count_signed_bot == len(users[chat_id]["bots"]):
                try:
                    users[chat_id]["method"] = "block"
                    tel_send_inline_button(chat_id, 'اسامی بلاک شده ها نشان داده شود؟ این ویژگی را هر لحظه میتوانید از menu تغییر دهید.', "yes_or_no")
                except:
                    return Response('ok', status=200)

            elif txt == "/yes" and users[chat_id]["first_time"] == True and count_signed_bot == len(users[chat_id]["bots"]):
                try:
                    users[chat_id]["showing_name"], users[chat_id]["first_time"] = True, False
                    text = txt_to_text('./settings/description.txt')
                    tel_send_message(chat_id, text)
                    lists_description = ''
                    entries = os.listdir('./lists/')
                    for entry in entries:
                        if entry[-3:] == 'txt':
                            text = txt_to_text('./lists/' + entry)
                            lists_description += text + '\n\n\n'
                    tel_send_inline_button(chat_id, lists_description, "list")
                except:
                    return Response('ok', status=200)

            elif txt == "/yes" and users[chat_id]["first_time"] == False:
                try:
                    users[chat_id]["showing_name"] = True
                    tel_send_message(chat_id, "اسم ها نمایش داده خواهند شد. این کار با کمی تاخیر انجام می شود.")
                except:
                    return Response('ok', status=200)

            elif txt == "/no" and users[chat_id]["first_time"] == True and count_signed_bot == len(users[chat_id]["bots"]):
                try:
                    users[chat_id]["showing_name"], users[chat_id]["first_time"] = False, False
                    text = txt_to_text('./settings/description.txt')
                    tel_send_message(chat_id, text)
                    lists_description = ''
                    entries = os.listdir('./lists/')
                    for entry in entries:
                        if entry[-3:] == 'txt':
                            text = txt_to_text('./lists/' + entry)
                            lists_description += text + '\n\n\n'
                    tel_send_inline_button(chat_id, lists_description, "list")
                except:
                    return Response('ok', status=200)

            elif txt == "/no" and users[chat_id]["first_time"] == False:
                try:
                    users[chat_id]["showing_name"] = False
                    tel_send_message(chat_id, "اسم ها نمایش داده نخواهند شد. این کار با کمی تاخیر انجام می شود.")
                except:
                    return Response('ok', status=200)

            elif txt[:9] == "Blocklist" and users[chat_id]["running"] == False:
                try:
                    id_list = csv_to_list('./lists/' + txt[5:] + '.csv')
                    users[chat_id]["running"] = True
                    block(id_list, chat_id)
                except:
                    tel_send_message(chat_id, 'خطایی پیش آمده.')
                    users.pop(chat_id)
                    return Response('ok', status=200)

            elif txt[:11] == "Unblocklist" and users[chat_id]["running"] == False:
                try:
                    id_list = csv_to_list('./lists/' + txt[7:] + '.csv')
                    users[chat_id]["running"] = True
                    unblock(id_list, chat_id)
                except:
                    tel_send_message(chat_id, 'خطایی پیش آمده.')
                    users.pop(chat_id)
                    return Response('ok', status=200)

            elif txt == "BlockAll" and users[chat_id]["running"] == False:
                try:
                    entries = os.listdir('./lists/')
                    id_list = []
                    for entry in entries:
                        if entry[-3:] == 'csv':
                            id_list += csv_to_list('./lists/' + entry)
                    tel_send_message(chat_id, f'شما در حال بلاک کردن همه ی لیست ها هستید.')
                    users[chat_id]["running"] = True
                    block(id_list, chat_id)
                except:
                    tel_send_message(chat_id, 'خطایی پیش آمده.')
                    users.pop(chat_id)
                    return Response('ok', status=200)

            elif txt == "UnblockAll" and users[chat_id]["running"] == False:
                try:
                    entries = os.listdir('./lists/')
                    id_list = []
                    for entry in entries:
                        if entry[-3:] == 'csv':
                            id_list += csv_to_list('./lists/' + entry)
                    tel_send_message(chat_id, f'شما در حال آنبلاک کردن همه ی لیست ها هستید.')
                    users[chat_id]["running"] = True
                    unblock(id_list, chat_id)
                except:
                    tel_send_message(chat_id, 'خطایی پیش آمده.')
                    users.pop(chat_id)
                    return Response('ok', status=200)

            elif txt == "UnblockAll" or txt == "BlockAll" or txt[:11] == "Unblocklist" or txt[:9] == "Blocklist":
                return Response('ok', status=200)

        elif txt != "":
            tel_send_message(chat_id, 'دستور وارد شده نامعتبر است.')
            return Response('ok', status=200)

        return Response('ok', status=200)

    elif request.method == 'GET':
        try:
            state = request.url.replace("&", " ")
            state = state.replace("?", " ")
            state = state.replace("=", " ")
            state = state.split(" ")[2]
        except:
            return Response("ok", status=200)

        for chat_id in users.keys():
            for bot in users[chat_id]["bots"]:
                if users[chat_id]["bots"][bot]["state"] == state:
                    users[chat_id]["bots"][bot]["url"] = request.url[:4]+"s"+request.url[4:]
                    access_token = users[chat_id]['bots'][bot]['oauth'].fetch_token(users[chat_id]['bots'][bot]['url'])
                    users[chat_id]["bots"][bot]["client"] = tweepy.Client(access_token['access_token'], wait_on_rate_limit=True)
                    count = 0
                    for bot_count in users[chat_id]["bots"]:
                        if users[chat_id]["bots"][bot_count]["url"] != "":
                            count += 1
                    if count == len(users[chat_id]["bots"]):
                        tel_send_inline_button(chat_id, 'هدف اصلی ما ندیدن و انتشار پیدا نکردن توییت سایبری هاست.\n\nدو تا راه وجود داره، بلاک و میوت. حالا شما دوس دارید اکانت ها فقط بلاک بشن یا نصف بلاک نصف میوت؟ اگه نصف بلاک بشن نصف میوت، سرعت این انجام این پروسه دو برابر میشه.', "block_and_mute")
                    else:
                        tel_send_message(chat_id, f'یه بات انجام شد. مونده {len(users[chat_id]["bots"]) - count} بات ه دیگه.')
                    return '<meta http-equiv="refresh" content="0; URL=https://t.me/CyberArmyBlockerBot" />'
        return Response("ok", status=200)


if __name__ == '__main__':

    app.run(debug=False)
