import os
import time
import json
import random
import requests
from PIL import Image, ImageDraw
import vk_api
import mysql.connector
from datetime import datetime
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

import config

vk_session = vk_api.VkApi(token=config.vk, api_version='5.144')
lp = VkBotLongPoll(vk_session, 204672845)
vk = vk_session.get_api()

try:
    os.makedirs("logs")
    print("Directory 'logs' created")
except FileExistsError:
    pass
now = datetime.now()
fileOpen = os.open("logs/" + str(now.strftime("%H.%M.%S_%d.%m.%Y")) + ".txt", os.O_RDWR | os.O_CREAT)
db = mysql.connector.connect(user=config.db_user, password=config.db_password, host=config.db_host, database=config.db)

usersJson = os.open("users.json", os.O_RDWR | os.O_CREAT)
users = json.load(open('users.json', 'r'))

db_cursor = db.cursor(dictionary=True)
db_cursor.execute("SELECT * FROM users")
row = db_cursor.fetchall()

b = 0
while b != len(row):
    users[int(row[b]['user_id'])] = str(row[b]['reg_date'])
    b += 1
json.dump(users, open('users.json', 'w'))

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
            "\n[" + datetime.now().strftime("%H:%M:%S") + "] (STARTER): All commands loaded, BOT work."))
        print("All commands loaded, BOT work.")
    time.sleep(0.3)

for event in lp.listen():
    if event.type == VkBotEventType.MESSAGE_NEW:
        sender = event.message.from_id
        print(event.message)
        if event.from_chat:
            os.write(fileOpen, str.encode("[" + datetime.now().strftime("%H:%M:%S") + "] (VK): new message from chat (sender: id" + str(int(sender)) + ") " + event.message['text'] + "\n"))
        if event.from_user:
            os.write(fileOpen, str.encode("[" + datetime.now().strftime("%H:%M:%S") + "] (VK): new message from user (id" + str(int(sender)) + ") " + event.message['text'] + "\n"))
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
        if str(event.message['text']).startswith('.сер'):
            print('Серый')
            try:
                if event.message['attachments'][0]:
                    if str(event.message['attachments'][0]['type']) == 'photo':
                        photo_url = event.message['attachments'][0]['photo']['sizes'][0]['url']
                        photo = requests.get(photo_url, allow_redirects=True)
                        folder = os.getcwd()
                        os.chdir(folder + '/images')
                        random_number = random.randint(0, 5000)
                        open('ID_' + str(sender) + '_randID' + str(random_number) + '.jpg', 'wb').write(photo.content)
                        image = Image.open('ID_' + str(sender) + '_randID' + str(random_number) + '.jpg')
                        draw = ImageDraw.Draw(image, "RGBA")
                        draw.rectangle([(0, 0), image.size], fill=(200, 200, 200, 200))
                        # #6F6F6F
                        image.save('ID' + str(sender) + '_randID' + str(random_number) + '_.png', 'PNG')
                        os.chdir(folder)
                        message = "Ваша фотография:"
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
                    else:
                        message = "Прикрепите фотографию"
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
            except IndexError:
                message = "Прикрепите фотографию"
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
os.close(fileOpen)
db.close()
