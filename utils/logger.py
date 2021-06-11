import os
import random
from datetime import datetime


def folder_log_create():
    try:
        os.makedirs(os.getcwd() + "\\logs")
        debugger("logger", "folder_log_create")
        return print('Directory "logs" created')
    except FileExistsError:
        pass


def folder_temp_create():
    try:
        os.makedirs(os.getcwd() + "\\temp")
        debugger("logger", "folder_temp_create")
        return print('Directory "temp" created')
    except FileExistsError:
        pass


def log_file():
    return os.open(os.getcwd() + "\\logs\\" + str(datetime.now().strftime("%m.%d.%Y_%H.%M.%S")) + ".txt", os.O_RDWR | os.O_CREAT)


def logger(message):
    os.write(log_file(), str.encode(message))


def log_close():
    pass


def debug_message(message):
    return print("[%s] [DEBUG] %s" % (datetime.now().strftime("%Y/%m/%d %H:%M:%S"), message))


random = random.randint(0, 999)


def debugger_args(file_name, function_name, args):
    debug_message("[%s:%s.%s] Called! Args=(%s)" % (file_name, function_name, random, args))


def debugger(file_name, function_name):
    debug_message("[%s:%s.%s] Called!" % (file_name, function_name, random))

