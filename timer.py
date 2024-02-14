import datetime
import json

openConfig = open("timer.json","r")
configRead = openConfig.read()

def convertToInt(stringIn):
    stringIn = stringIn.replace(":","")
    intOut = int(stringIn)
    return intOut

configParsed = json.loads(configRead)

total = convertToInt(configParsed["total"])
usedTarget = convertToInt(configParsed["used"])

used = 0
fps = 1

def get_time_as_int():
    now = datetime.datetime.now()
    date_string = now.strftime("%H%M")
    date_int = int(date_string)
    return date_int

first = get_time_as_int()

while get_time_as_int() - first < 6:
    if input() == "a":
        used = used + 1
    if used == usedTarget * 60 * fps:
        print("telefon algılandı!")
        break