import os
import random
import vk_api
from datetime import time, datetime
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

import config
import commands
from utils import debuger

vk_session = vk_api.VkApi(token=config.vk)
longpoll = VkBotLongPoll(vk_session, 204672845)
vk = vk_session.get_api()

try:
    os.makedirs("logs")
    print("Directory 'logs' created")
except FileExistsError:
    pass
now = datetime.now()
currentDir = os.getcwd()
os.chdir('logs')
f = open(str(now.strftime("%H.%M.%S_%d.%m.%Y")) + ".txt", "w")

os.chdir(currentDir)
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
    os.chdir('logs')
    f = open(str(now.strftime("%H.%M.%S_%d.%m.%Y")) + ".txt", "w")
    line = file1.readline()
    if not line:
        break
    f.write("["+datetime.now().strftime("%H:%M:%S")+"] Command " + commands_list[a] + " loaded!\n")
    f.close()
    os.chdir(currentDir)
    print("Command " + commands_list[a] + " loaded.")
    a += 1

for event in longpoll.listen():
    if event.type == VkBotEventType.MESSAGE_NEW:
        debuger.debug("message_new", event.message['text'])
        if event.message['text'] == '.команды':
            if event.from_chat:
                total = []
                while (t != commands_total):
                    line = file1.readline()
                    if not line:
                        break
                    total.append(line.split(None, 1)[0])
                vk.messages.send(
                    random_id=random.randint(0, 10000),
                    message='Все команды, которые доступны в боте: ',
                    chat_id=event.chat_id
                )
f.close()