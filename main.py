import os
import json
import random
import vk_api
import mysql.connector
from datetime import datetime
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

import config
# import commands
from utils import debuger

vk_session = vk_api.VkApi(token=config.vk)
lp = VkBotLongPoll(vk_session, 204672845)
vk = vk_session.get_api()

try:
    os.makedirs("logs")
    print("Directory 'logs' created")
except FileExistsError:
    pass
now = datetime.now()
fileOpen = os.open("logs/" + str(now.strftime("%H.%M.%S_%d.%m.%Y")) + ".txt", os.O_RDWR | os.O_CREAT)
usersFile = os.open("users.json", os.O_RDWR | os.O_CREAT)
db = mysql.connector.connect(user=config.db_user, password=config.db_password, host=config.db_host, database=config.db)
os.write(usersFile, str.encode("[]"))

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
        os.write(fileOpen, str.encode("["+datetime.now().strftime("%H:%M:%S")+"] (CONSOLE): " + commands_list[a] + " is not a command. Skip.\n"))
        print(commands_list[a] + " is not a command. Skip.")
        a += 1
    else:
        os.write(fileOpen, str.encode("["+datetime.now().strftime("%H:%M:%S")+"] (CONSOLE): Command " + commands_list[a] + " loaded.\n"))
        print("Command " + commands_list[a] + " loaded.")
        a += 1

for event in lp.listen():
    if event.type == VkBotEventType.MESSAGE_NEW:
        sender = event.message.from_id
        if event.from_chat:
            debuger.debug("new message from chat", event.message['text'])
        if event.from_user:
            debuger.debug("new message from user (id" + str(int(sender)) + ")", event.message['text'])
        db_cursor = db.cursor(dictionary=True)
        db_cursor.execute("SELECT * FROM users WHERE user_id='%s'" % (int(sender)))
        row = db_cursor.fetchall()
        if int(db_cursor.rowcount) == -1:
            print("NEW USER CREATED (https://vk.com/id"+str(int(sender)) + ")")
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            db_cursor.execute(
                "INSERT INTO users (user_id, reg_date) VALUES ('%s', '%s')" % (int(sender), now)
            )
            db.commit()
        if event.message['text'] == '.команды':
            if event.from_chat:
                vk.messages.send(
                    random_id=random.randint(0, 10000),
                    message='Все команды, которые доступны в боте: ',
                    chat_id=event.chat_id
                )
            if event.from_user:
                vk.messages.send(
                    random_id=random.randint(0, 10000),
                    message='Все команды, которые доступны в боте: ',
                    user_id=sender
                )
        if event.message['text'] == '.профиль':
            generated_message = 'Профиль id'+str(int(sender))+': \n' + str(row[0]['reg_date'])
            if event.from_chat:
                vk.messages.send(
                    random_id=random.randint(0, 10000),
                    message=generated_message,
                    chat_id=event.chat_id
                )
            if event.from_user:
                vk.messages.send(
                    random_id=random.randint(0, 10000),
                    message=generated_message,
                    user_id=sender
                )
os.close(fileOpen)
os.close(usersFile)
db.close()
