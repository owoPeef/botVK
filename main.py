from random import random
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.longpoll import VkLongPoll, VkEventType

import config

vk_session = vk_api.VkApi(token=config.vk)
longpoll = VkBotLongPoll(vk_session, 204672845)
vk = vk_session.get_api()

for event in longpoll.listen():
    if event.type == VkBotEventType.MESSAGE_NEW:
        if event.message == 'Привет':
            if event.from_user:
                vk.messages.send(
                    user_id=event.object['from_id'],
                    message='Привет!',
                    random_id=random.randint(0, 10000)
                )

            if event.from_chat:
                vk.messages.send(
                    random_id=random.randint(0, 10000),
                    message='Привет!',
                    chat_id=event.object['peer_id']
                )

