import json
openConfig = open("timer.json","r")
configRead = openConfig.read()
# print(config)
def convertToInt(stringIn):
    stringIn = stringIn.replace(":","")
    intOut = int(stringIn)
    return intOut
configParsed = json.loads(configRead)
total = convertToInt(configParsed["total"])

print(total)


