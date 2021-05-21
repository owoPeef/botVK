import os
import glob

while True:
    want = input("What do you want to do?\n")

    if want == "delete logs":
        files = glob.glob(os.getcwd() + '/logs/*')
        for f in files:
            os.remove(f)
        print("All logs was deleted\n")

    if want != "delete logs" and want != "":
        print('\nCommand "' + str(want) + '" not found!\n')

    if want != "delete logs" and want == "":
        exit()