import glob
import json
import os
import random

import requests
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import config
import permissions

vk_session = vk_api.VkApi(token=config.vk, api_version='5.144')
lp = VkBotLongPoll(vk_session, 204672845)
vk = vk_session.get_api()

for event in lp.listen():
    if event.type == VkBotEventType.MESSAGE_NEW:
        if str(event.message['text']).startswith('.переименовать'):
            user = vk.messages.getConversationMembers(
                peer_id=event.chat_id+2000000000
            )
            b = 0
            c = 0
            user_perms = False
            while len(user['items']) != c:
                if user['items'][c]['member_id'] == int(event.message.from_id):
                    print(str(user['items'][c]))
                    if len(user['items'][c]) >= 4:
                        permission = "is_" + permissions.rename
                        try:
                            user_perms = user['items'][c][permission]
                            print("have")
                        except KeyError:
                            user_perms = False
                            print("Except KeyError: don't have")
                    else:
                        user_perms = False
                        print("don't have")
                    b += 1
                c += 1
            if not user_perms:
                message = "You don't have permissions!"
            else:
                slicer = str(event.message['text']).split()
                title = []
                a = 1
                while len(slicer) != a:
                    title.append(slicer[a])
                    a += 1
                vk.messages.editChat(
                    chat_id=event.chat_id,
                    title=" ".join(map(str, title))
                )
                message = "Success"
            vk.messages.send(
                random_id=random.randint(0, 10000),
                message=message,
                chat_id=event.chat_id
            )
        if event.message['text'] == ".аватар":
            if event.from_chat:
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
                            vk.messages.send(
                                chat_id=event.chat_id,
                                random_id=random.random(),
                                message='success'
                            )
                        except vk_api.ApiError:
                            vk.messages.send(
                                chat_id=event.chat_id,
                                random_id=random.random(),
                                message='[ERROR] VkApi: photo min size 200x200, 0.25 < aspect < 3'
                            )
                        finally:
                            file_open.close()
                            os.remove(file_path)
                except IndexError:
                    vk.messages.send(
                        chat_id=event.chat_id,
                        random_id=random.random(),
                        message='photo not found'
                    )
