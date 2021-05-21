import os
import sys
import json
import random
import vk_api
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
        debuger.debug("new message", event.message['text'])
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
                    user_id=event.message.from_id
                )
os.close(fileOpen)
os.close(usersFile)
