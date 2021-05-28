import random

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
