import json
import os
import random
import mysql.connector
import requests
import vk_api
import config
import permissions
from datetime import datetime
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

db = mysql.connector.connect(user=config.db_user, password=config.db_password, host=config.db_host, database=config.db)
db_cursor = db.cursor(dictionary=True)

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
                        file_open = ""
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
