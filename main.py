import json
import os
import time
import random
import vk_api
import requests
import mysql.connector
from utils import logger
from datetime import datetime
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

import config
import permissions

vk_session = vk_api.VkApi(token=config.vk, api_version='5.144')
lp = VkBotLongPoll(vk_session, 204672845)
vk = vk_session.get_api()

logger.folder_log_create()
logger.folder_temp_create()

db = ""
try:
    db = mysql.connector.connect(user=config.db_user, password=config.db_password, host=config.db_host, database=config.db)
    print("[MySQL] Connection success")
except mysql.connector.InterfaceError:
    print("[MySQL] Error connection")
    time.sleep(2)
    exit()
db_cursor = db.cursor(dictionary=True)
db_cursor.execute("SELECT * FROM users")
row = db_cursor.fetchall()

print("["+datetime.now().strftime("%H:%M:%S")+"] Bot started.\nCommands are loading now, please wait...")
time.sleep(3)

commands_total = len(open("commands.py").readlines())
file1 = open('commands.py', 'r')
commands_list = []
t = 0
with open('commands.py', 'r') as f:
    for line in f:
        commands_list.append(line.split(None, 1)[0])
        t += 1

a = 0
while commands_total != a:
    line = file1.readline()
    if not line:
        break
    if not line.find("#"):
        a += 1
    else:
        file = logger.log_file()
        logger.logger(logger.debugger_args("main", "commands_total", "command=" + commands_list[a]))
        print("Command " + commands_list[a] + " loaded.")
        a += 1
    if commands_total == a:
        time.sleep(0.7)
        file = logger.log_file()
        logger.logger(logger.debugger_args("main", "total", ""))
        os.write(file, str.encode(
            "[%s] (STARTER): All commands loaded (%s)" % (str(datetime.now().strftime("%H:%M:%S")), str(a))))
        print("All commands loaded (%s)" % (str(a)))
    time.sleep(0.3)

for event in lp.listen():
    if event.type == VkBotEventType.MESSAGE_NEW:
        sender = event.message.from_id
        if event.from_chat:
            os.write(fileOpen, str.encode('\n[' + datetime.now().strftime("%H:%M:%S") + '] (VK): new message from chat (sender: id' + str(int(sender)) + '). Text: "' + event.message['text'] + '"'))
        if event.from_user:
            os.write(fileOpen, str.encode('\n[' + datetime.now().strftime("%H:%M:%S") + '] (VK): new message from user (id' + str(int(sender)) + '). Text: "' + event.message['text'] + '"'))
        db_cursor.execute("SELECT * FROM users WHERE user_id='%s'" % (int(sender)))
        row = db_cursor.fetchall()
        if int(db_cursor.rowcount) == 0:
            os.write(fileOpen, str.encode("[" + datetime.now().strftime("%H:%M:%S") + "] (VK): NEW USER CREATED (https://vk.com/id"+str(int(sender)) + ")\n"))
            print("NEW USER CREATED (https://vk.com/id"+str(int(sender)) + ")")
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            db_cursor.execute(
                "INSERT INTO users (user_id, reg_date) VALUES ('%s', '%s')" % (int(sender), now)
            )
            db.commit()
        if event.from_chat:
            chat_id = event.chat_id + 2000000000
            db_cursor.execute("SELECT * FROM chats WHERE user_id='%s' AND chat_id='%s'" % (int(sender), (int(chat_id))))
            row2 = db_cursor.fetchone()
            if int(db_cursor.rowcount) == 0 or int(db_cursor.rowcount) == -1:
                if int(db_cursor.rowcount) == -1:
                    symbols = int(len(event.message['text']))
                    db_cursor.execute("INSERT INTO chats (chat_id, user_id, messages, symbols) VALUES ('%s', '%s', '%s', '%s')" % (int(chat_id), int(sender), int(1), int(symbols)))
                    db.commit()
            else:
                db_cursor.execute("SELECT * FROM chats WHERE user_id='%s' AND chat_id='%s'" % (int(sender), (int(chat_id))))
                row3 = db_cursor.fetchone()
                total = int(row3['messages']) + 1
                symbols = int(row3['symbols']) + int(len(event.message['text']))
                db_cursor.execute(
                    "UPDATE chats SET messages='%s', symbols='%s' WHERE chat_id='%s' AND user_id='%s'" % (int(total), int(symbols), int(chat_id), int(sender))
                )
                db.commit()

        try:
            if event.message['action']['type'] == "chat_invite_user":
                user_added = vk.users.get(
                    user_ids=event.message['action']['member_id']
                )
                message = "Приветствую тебя, [id" + str(user_added[0]['id']) + "|" + str(
                    user_added[0]['first_name']) + " " + str(user_added[0]['last_name']) + "]"
                vk.messages.send(
                    chat_id=event.chat_id,
                    random_id=random.random(),
                    message=message
                )
        except KeyError:
            pass

        if event.message['text'] == '.команды':
            message = 'Все команды, которые доступны в боте: '
            if event.from_chat:
                vk.messages.send(
                    random_id=random.randint(0, 10000),
                    message=message,
                    chat_id=event.chat_id
                )
            if event.from_user:
                vk.messages.send(
                    random_id=random.randint(0, 10000),
                    message=message,
                    user_id=sender
                )
        if event.message['text'] == '.профиль':
            db_cursor.execute("SELECT * FROM users WHERE user_id='%s'" % (int(sender)))
            row = db_cursor.fetchall()
            user_info = vk.users.get(
                user_ids=sender,
                fields="sex",
                name_case="nom"
            )
            if int(user_info[0]['sex']) == 2:
                user_info = vk.users.get(
                    user_ids=sender,
                    fields="sex",
                    name_case="gen"
                )
                message_sex = str(user_info[0]['last_name']) + " " + str(user_info[0]['first_name'])
            else:
                user_info = vk.users.get(
                    user_ids=sender,
                    fields="sex",
                    name_case="gen"
                )
                message_sex = str(user_info[0]['first_name']) + " " + str(user_info[0]['last_name'])
            message = "Профиль " + message_sex + ":\n" + str(row[0]['reg_date'])
            if event.from_chat:
                vk.messages.send(
                    random_id=random.randint(0, 10000),
                    message=message,
                    chat_id=event.chat_id
                )
            if event.from_user:
                vk.messages.send(
                    random_id=random.randint(0, 10000),
                    message=message,
                    user_id=sender
                )
        if event.message['text'] == '.онлайн':
            chat_users = vk.messages.getConversationMembers(
                peer_id=2000000000 + int(event.chat_id),
                count=100,
                fields="online"
            )
            a = 0
            online = 0
            users_online = []
            while a != chat_users['count'] - len(chat_users['groups']):
                if chat_users['profiles'][a]['online'] == 1:
                    online += 1
                    users_online.append(str(online) + ". [id" + str(chat_users['profiles'][a]['id']) + "|" + str(
                        chat_users['profiles'][a]['first_name']) + " " + str(
                        chat_users['profiles'][a]['last_name']) + "] -- online\n")
                a += 1
            d = 0
            message_users = ""
            while d != len(users_online):
                message_users += users_online[d]
                d += 1
            if online != 0:
                message = "Пользователи онлайн:\n" + message_users
            else:
                message = "Пользователей онлайн:\n0"
            if event.from_chat:
                vk.messages.send(
                    random_id=random.randint(0, 10000),
                    message=message,
                    chat_id=event.chat_id
                )
        if str(event.message['text']).startswith('.статистика'):
            ids = str(event.message['text']).split()
            if event.from_chat:
                if len(ids) == 2:
                    db_cursor.execute("SELECT * FROM chats WHERE chat_id='%s' AND user_id='%s'" % (
                    2000000000 + int(event.chat_id), int(ids[1])))
                    stats = db_cursor.fetchone()
                    if db_cursor.rowcount == 1:
                        message = "Статистика пользователя: \nMSGs: " + str(
                            stats['messages']) + " \nSymbols: " + str(
                            stats['symbols'])
                        vk.messages.send(
                            random_id=random.randint(0, 10000),
                            message=message,
                            chat_id=event.chat_id
                        )
                    else:
                        message = "User don't registered."
                        vk.messages.send(
                            random_id=random.randint(0, 10000),
                            message=message,
                            chat_id=event.chat_id
                        )
                else:
                    db_cursor.execute("SELECT * FROM chats WHERE chat_id='%s' AND user_id='%s'" % (
                    2000000000 + int(event.chat_id), int(sender)))
                    stats = db_cursor.fetchone()
                    message = "Статистика пользователя: \nMSGs: " + str(stats['messages']) + " \nSymbols: " + str(
                        stats['symbols'])
                    vk.messages.send(
                        random_id=random.randint(0, 10000),
                        message=message,
                        chat_id=event.chat_id
                    )
        if str(event.message['text']).startswith('.рандом'):
            rand_numbers = str(event.message['text']).split(' ')
            random_total = random.randint(int(rand_numbers[1]), int(rand_numbers[2]))
            if event.from_chat:
                message = "Выпало число " + str(random_total)
                vk.messages.send(
                    random_id=random.randint(0, 10000),
                    message=message,
                    chat_id=event.chat_id
                )
            if event.from_user:
                message = "Выпало число " + str(random_total)
                vk.messages.send(
                    random_id=random.randint(0, 10000),
                    message=message,
                    user_id=sender
                )
        if str(event.message['text']) == '.курс':
            rates = requests.get('https://currate.ru/api/?get=rates&pairs=USDRUB,EURRUB&key=' + config.rates_api)
            message = "Курс валют:\n1$ = " + str(round(float(rates.json()['data']['USDRUB']))) + "₽\n1€ = " + str(
                round(float(rates.json()['data']['EURRUB']))) + "₽"
            if event.from_chat:
                vk.messages.send(
                    random_id=random.randint(0, 10000),
                    message=message,
                    chat_id=event.chat_id
                )
            if event.from_user:
                vk.messages.send(
                    random_id=random.randint(0, 10000),
                    message=message,
                    user_id=sender
                )
        if str(event.message['text']).startswith('.переименовать'):
            if event.from_chat:
                b = 0
                c = 0
                user = vk.messages.getConversationMembers(peer_id=event.chat_id + 2000000000)
                user_perms = False
                while len(user['items']) != c:
                    if user['items'][c]['member_id'] == int(event.message.from_id):
                        if len(user['items'][c]) >= 4:
                            permission = "is_" + permissions.rename
                            try:
                                user_perms = user['items'][c][permission]
                            except KeyError:
                                user_perms = False
                        else:
                            user_perms = False
                        b += 1
                    c += 1
                if not user_perms:
                    message = "У вас нет прав на выполнение данной команды!"
                else:
                    slicer = str(event.message['text']).split()
                    title = []
                    a = 1
                    while len(slicer) != a:
                        title.append(slicer[a])
                        a += 1
                    end_title = " ".join(map(str, title))
                    vk.messages.editChat(
                        chat_id=event.chat_id,
                        title=end_title
                    )
                    message = 'Беседа была успешно переименована в "'+str(end_title)+'".'
                vk.messages.send(
                    random_id=random.randint(0, 10000),
                    message=message,
                    chat_id=event.chat_id
                )
        if event.message['text'] == ".аватар":
            if event.from_chat:
                b = 0
                c = 0
                user = vk.messages.getConversationMembers(peer_id=event.chat_id + 2000000000)
                user_perms = False
                message = ""
                while len(user['items']) != c:
                    if user['items'][c]['member_id'] == int(event.message.from_id):
                        if len(user['items'][c]) >= 4:
                            permission = "is_" + permissions.avatar
                            try:
                                user_perms = user['items'][c][permission]
                            except KeyError:
                                user_perms = False
                        else:
                            user_perms = False
                        b += 1
                    c += 1
                if not user_perms:
                    message = "У вас нет прав на выполнение данной команды!"
                else:
                    try:
                        if str(event.message['attachments'][0]['type']) == 'photo':
                            file_path = os.getcwd() + "/temp/id"+str(event.message.from_id)+".png"
                            try:
                                photo_url = event.message['attachments'][0]['photo']['sizes'][4]['url']
                                photo = requests.get(photo_url, allow_redirects=True)
                                upload = open(file_path, 'wb').write(photo.content)
                                file_open = open(file_path, 'rb')
                                image = {'photo': ('img.png', file_open)}
                                upload_server = vk.photos.getChatUploadServer(chat_id=event.chat_id)
                                photo_upload_response = requests.post(upload_server['upload_url'], files=image)
                                photo_upload_result = json.loads(photo_upload_response.text)['response']
                                vk.messages.setChatPhoto(file=photo_upload_result)
                                message = "Аватарка беседы была изменена."
                            except vk_api.ApiError:
                                message = "[ERROR] VkApi: photo min size 200x200, 0.25 < aspect < 3"
                            finally:
                                file_open.close()
                                os.remove(file_path)
                    except IndexError:
                        message = "Прикрепите фото, которое вы хотите поставить на аватарку беседы."
                vk.messages.send(
                    random_id=random.randint(0, 10000),
                    message=message,
                    chat_id=event.chat_id
                )
        if str(event.message['text']).startswith(".брак запрос"):
            if event.from_chat:
                text_split = str(event.message['text']).split()
                message = ""
                founded = 0
                if len(text_split) == 2:
                    message = "Укажите айди человека"
                if len(text_split) == 3:
                    founded = 0
                    work = 0
                    strip = ""
                    if str(text_split[2]).startswith("id"):
                        strip = str(text_split[2])[2:]
                        work = 1
                    if str(text_split[2]).startswith("https://vk.com/id") or str(text_split[2]).startswith("http://vk.com/id"):
                        if str(text_split[2]).startswith("https://vk.com/id"):
                            strip = str(text_split[2])[17:]
                        if str(text_split[2]).startswith("http://vk.com/id"):
                            strip = str(text_split[2])[16:]
                        work = 1
                    if str(text_split[2]).startswith(('0', '1', '2', '3', '4', '5', '6', '7', '8', '9')):
                        strip = str(text_split[2])
                        work = 1
                    if work == 1:
                        if int(strip) == event.message.from_id:
                            message = "На себе пожениться нельзя."
                            founded = 1
                        else:
                            user = vk.users.get(
                                user_ids=int(strip),
                                name_case="nom"
                            )
                            message_user = vk.users.get(
                                user_ids=int(event.message.from_id),
                                name_case="ins"
                            )
                            chat = vk.messages.getConversationMembers(peer_id=2000000000 + event.chat_id)
                            a = 0
                            user_found = 0
                            while len(chat['items']) != a:
                                if chat['items'][a]['member_id'] == int(strip):
                                    user_found = 1
                                a += 1
                            founded = 1
                            if user_found == 1:
                                db_cursor.execute("SELECT * FROM marriages WHERE first_uid='%s' OR second_uid='%s' AND chat_id='%s'" % (int(strip), int(strip), int(event.chat_id)))
                                row = db_cursor.fetchall()
                                db.commit()
                                if int(db_cursor.rowcount) == 0:
                                    nowDatetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                    db_cursor.execute("INSERT INTO requests (request_date, type, to_id, from_id, chat_id) VALUES ('%s', '%s', '%s', '%s', '%s')" % (nowDatetime, "marriage", int(strip), int(event.message.from_id), int(event.chat_id)))
                                    db.commit()
                                    message = "[id"+str(user[0]['id'])+"|"+str(user[0]['first_name'])+" "+str(user[0]['last_name'])+"], чтобы вступить в брак с [id"+str(message_user[0]['id'])+"|"+str(message_user[0]['first_name'])+" "+str(message_user[0]['last_name'])+"] напишите «.брак принять id"+str(message_user[0]['id'])+"»"
                                    founded = 1
                                else:
                                    message = "Пользователь уже состоит в браке!"
                                    founded = 1
                            else:
                                message = "Пользователя с айди "+str(strip)+" нет в беседе"
                    if founded == 0:
                        message = "Значение " + str(text_split[2]) + " не является айди пользователя."
                if len(text_split) > 3:
                    message = "Указано " + str(len(text_split)) + " значений, должно быть 1."
                vk.messages.send(
                    chat_id=event.chat_id,
                    random_id=random.random(),
                    message=message
                )
        if str(event.message['text']).startswith(".брак принять"):
            if event.from_chat:
                text_split = str(event.message['text']).split()
                message = ""
                founded = 0
                work = 0
                if len(text_split) == 2:
                    message = "Укажите айди человека"
                if len(text_split) == 3:
                    strip = ""
                    if str(text_split[2]).startswith("id"):
                        strip = str(text_split[2])[2:]
                        work = 1
                    if str(text_split[2]).startswith("http://vk.com/id"):
                        strip = str(text_split[2])[16:]
                        work = 1
                    if str(text_split[2]).startswith("https://vk.com/id"):
                        strip = str(text_split[2])[17:]
                        work = 1
                    if str(text_split[2]).startswith(('0', '1', '2', '3', '4', '5', '6', '7', '8', '9')):
                        strip = str(text_split[2])
                        work = 1
                    if work == 1:
                        db_cursor.execute(
                            "SELECT * FROM requests WHERE type='marriage' AND to_id='%s' AND from_id='%s' AND chat_id='%s'" % (
                                int(event.message.from_id), int(strip), int(event.chat_id)))
                        marriage_request = db_cursor.fetchall()
                        db.commit()
                        if int(db_cursor.rowcount) == 1:
                            db_cursor.execute(
                                "SELECT * FROM marriages WHERE first_uid='%s' OR second_uid='%s' AND chat_id='%s'" % (
                                    int(event.message.from_id), int(event.message.from_id), int(event.chat_id)))
                            db_cursor.fetchall()
                            db.commit()
                            if int(db_cursor.rowcount) == 1:
                                message = "Вы уже состоите в браке, чтобы принять другой брак вам нужно выйти из текущего"
                            else:
                                nowDatetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                db_cursor.execute(
                                    "INSERT INTO marriages (marriage_date, first_uid, second_uid, chat_id) VALUES ('%s', '%s', '%s', '%s')" % (
                                        nowDatetime, int(marriage_request[0]['from_id']),
                                        int(marriage_request[0]['to_id']), int(event.chat_id)))
                                db.commit()
                                db_cursor.execute("DELETE FROM requests WHERE from_id='%s' AND to_id='%s'" % (
                                    int(strip), int(event.message.from_id)))
                                db.commit()
                                db_cursor.execute(
                                    "SELECT * FROM marriages WHERE first_uid='%s' AND second_uid='%s' AND chat_id='%s'" % (
                                        int(marriage_request[0]['from_id']), int(marriage_request[0]['to_id']),
                                        int(event.chat_id)))
                                marriageNumber = db_cursor.fetchall()[0]['marriage_id']
                                db.commit()
                                message = "Был зарегистрирован новый брак (#" + str(marriageNumber) + ")"
                        else:
                            message = "Пользователь под айди " + str(
                                strip) + " не отправлял вам запрос на вступление в брак"
                        founded = 1
                    if founded == 0:
                        message = "Значение " + str(text_split[1]) + " не является айди пользователя."
                if len(text_split) > 3:
                    message = "Указано " + str(len(text_split) - 1) + " значения, должно быть 1."
                vk.messages.send(
                    chat_id=event.chat_id,
                    random_id=random.random(),
                    message=message
                )
        if str(event.message['text']) == ".брак развод":
            if event.from_chat:
                message = ""
                db_cursor.execute(
                    "SELECT * FROM marriages WHERE first_uid='%s' OR second_uid='%s' AND chat_id='%s'" % (
                        int(event.message.from_id), int(event.message.from_id), int(event.chat_id)))
                marriage = db_cursor.fetchall()
                db.commit()
                if db_cursor.rowcount == 1:
                    db_cursor.execute("DELETE FROM marriages WHERE first_uid='%s' OR second_uid='%s' AND chat_id='%s'" % (
                        int(event.message.from_id), int(event.message.from_id), int(event.chat_id)))
                    db.commit()
                    user_get = []
                    if event.message.from_id == marriage[0]['first_uid']:
                        user_get = vk.users.get(
                            user_ids=marriage[0]['second_uid'],
                            name_case="ins"
                        )
                    if event.message.from_id == marriage[0]['second_uid']:
                        user_get = vk.users.get(
                            user_ids=marriage[0]['first_uid'],
                            name_case="ins"
                        )
                    message = "Вы развелись с " + str(user_get[0]['first_name']) + " " + str(user_get[0]['last_name'])
                else:
                    message = "Вы не состоите в браке."
                vk.messages.send(
                    chat_id=event.chat_id,
                    random_id=random.random(),
                    message=message
                )
        if str(event.message['text']) == ".брак список":
            if event.from_chat:
                message = ""
                text_split = str(event.message['text']).split()
                db_cursor.execute(
                    "SELECT * FROM marriages WHERE chat_id='%s'" % (int(event.chat_id))
                )
                result = db_cursor.fetchall()
                db.commit()
                if db_cursor.rowcount == 0:
                    message = "В беседе нет браков"
                if db_cursor.rowcount != 0:
                    a = 0
                    text = ""
                    while a != db_cursor.rowcount:
                        first_date = datetime.strptime(str(result[a]['marriage_date']), "%Y-%m-%d %H:%M:%S")
                        second_date = datetime.strptime(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "%Y-%m-%d %H:%M:%S")
                        date_btw = abs((first_date - second_date).days)
                        users = vk.users.get(
                            user_ids=str(result[a]['first_uid']) + ", " + str(result[a]['second_uid'])
                        )
                        text += str(a+1) + ". " + str(users[0]['first_name']) + " " + str(users[0]['last_name']) + " и " + str(users[1]['first_name']) + " " + str(users[1]['last_name'] + " (" + str(date_btw) + " д.)" + "\n")
                        a += 1
                    message = str(text) + "\nВсего браков: " + str(a)
                vk.messages.send(
                    chat_id=event.chat_id,
                    random_id=random.random(),
                    message=message
                )
        if event.message['text'] == ".кейс":
            if event.from_chat:
                rand = random.randint(1, 100)
                prize = ""
                if rand < 25:
                    prize = "Хуйня"
                if 25 < rand <= 50:
                    prize = "Норм"
                if 50 < rand <= 75:
                    prize = "Средне"
                if 75 < rand <= 100:
                    prize = "Ахуенно"
                vk.messages.send(
                    message="Вам выпало %s (%s)" % (str(prize), str(rand)),
                    random_id=random.random(),
                    chat_id=event.chat_id
                )
        if str(event.message['text']).startswith(".удалить"):
            if event.from_chat:
                message = ""
                text_message = str(event.message['text']).split()
                if len(text_message) == 1:
                    try:
                        if event.message['reply_message']:
                            try:
                                vk.messages.delete(delete_for_all=True, peer_id=event.chat_id + 2000000000, conversation_message_ids=event.message['reply_message']['conversation_message_id'])
                                message = "Message " + str(event.message['reply_message']['id']) + " was deleted (" + str(event.message['reply_message']['conversation_message_id']) + ")"
                            except vk_api.ApiError as exception:
                                message = "ERROR: " + str(exception)
                    except KeyError:
                        message = "Укажите айди сообщения"
                else:
                    if len(text_message) <= 3:
                        message = "Можно указать только одно айди!"
                    if len(text_message) == 2:
                        try:
                            vk.messages.delete(
                                message_ids=text_message[1],
                                delete_for_all=True,
                                peer_id=event.chat_id + 2000000000
                            )
                            message = "Message " + str(text_message[1]) + " was deleted"
                        except vk_api.ApiError as exception:
                            message = "ERROR: " + str(exception)
                vk.messages.send(
                    message=message,
                    chat_id=event.chat_id,
                    random_id=random.random()
                )
        if event.message['text'] == ".информация":
            if event.from_chat:
                message = ""
                try:
                    if event.message['reply_message']:
                        try:
                            user_get = vk.users.get(
                                user_ids=event.message['reply_message']['from_id']
                            )
                            unix_to_normal = datetime.fromtimestamp(int(event.message['reply_message']['date'])).strftime('%d.%m.%Y %H:%M:%S')
                            message = str("Дата отправки: %s\nОтправитель: [id%s|%s %s]\nТекст сообщения: <<%s>>\nID сообщения всего: %s\nID сообщения в беседе: %s" % (str(unix_to_normal), str(user_get[0]['id']), str(user_get[0]['first_name']), str(user_get[0]['last_name']), str(event.message['reply_message']['text']), str(event.message['reply_message']['id']), str(event.message['reply_message']['conversation_message_id'])))
                        except vk_api.ApiError as exception:
                            message = "ERROR: " + str(exception)
                except KeyError:
                    message = "Перешлите сообщение, информацию которого вы хотите получить"
                vk.messages.send(
                    message=message,
                    random_id=random.random(),
                    chat_id=event.chat_id
                )
os.close(fileOpen)
db.close()
