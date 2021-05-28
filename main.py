import json
import os
import time
import random
import vk_api
import requests
import mysql.connector
from PIL import Image, ImageDraw
from datetime import datetime
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

import config
import permissions

vk_session = vk_api.VkApi(token=config.vk, api_version='5.144')
lp = VkBotLongPoll(vk_session, 204672845)
vk = vk_session.get_api()

try:
    os.makedirs("logs")
    print("Directory 'logs' created")
except FileExistsError:
    pass
now = datetime.now()
fileOpen = os.open("logs/" + str(now.strftime("%d.%m.%Y_%H.%M.%S")) + ".txt", os.O_RDWR | os.O_CREAT)

db = mysql.connector.connect(user=config.db_user, password=config.db_password, host=config.db_host, database=config.db)
db_cursor = db.cursor(dictionary=True)
db_cursor.execute("SELECT * FROM users")
row = db_cursor.fetchall()

os.write(fileOpen, str.encode("[" + datetime.now().strftime("%H:%M:%S") + "] (STARTER): Bot started.\n[" + datetime.now().strftime("%H:%M:%S") + "] (STARTER): Commands are loading now, please wait...\n"))
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
        os.write(fileOpen, str.encode("["+datetime.now().strftime("%H:%M:%S")+"] (CONSOLE): Command " + commands_list[a] + " loaded.\n"))
        print("Command " + commands_list[a] + " loaded.")
        a += 1
    if commands_total == a:
        time.sleep(0.7)
        os.write(fileOpen, str.encode(
            "[" + datetime.now().strftime("%H:%M:%S") + "] (STARTER): All commands loaded, BOT work."))
        print("All commands loaded, BOT work.")
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
                            file_path = os.getcwd() + "/images/id"+str(event.message.from_id)+".png"
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
os.close(fileOpen)
db.close()
