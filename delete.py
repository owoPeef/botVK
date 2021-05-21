import os
import glob

while True:
    find = 0
    want = input("What do you want to do?\n")

    if want == "delete logs":
        files = glob.glob(os.getcwd() + '/logs/*')
        for f in files:
            os.remove(f)
        print("All logs was deleted\n")
        find = 1

    if want == "delete unimportant files":
        files = glob.glob(os.getcwd() + "/*.*")
        for f in files:
            if not f.endswith('users.json') and not f.endswith('delete.py') and not f.endswith('commands.py') and not f.endswith('config.py') and not f.endswith('main.py'):
                os.remove(f)
        print("All files was deleted\n")
        find = 1

    if find == 0:
        print('\nCommand "' + str(want) + '" not found!\n')
