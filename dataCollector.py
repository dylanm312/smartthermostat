import tempSensorInterface as tempSensor
import csv
import datetime
import relayInterface
import time
import json

fileName = 'data.csv'

# Set to False if temp sensor is disconnected to avoid spinning 
# forever as we wait for the serial stream to come in
tempSensorConnected = True

# Set to true to initialize data file. THIS WILL ERASE ALL RECORDED DATA!! USE WITH CAUTION!!
shouldInitFile = False

def initFile():
    # Open CSV for data, or create if not exist. Set up CSV writer.
    with open(fileName, mode='w') as file:
        data_writer = csv.writer(file, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL)
        # Set CSV column headings
        data_writer.writerow(["Timestamp", "Temperature (F)", "Heat Relay", "Fan Relay", "A/C Relay"])

def collectData():
    # Do the thing
    now = datetime.datetime.now()

    if(tempSensorConnected):
        # Pull in data
        temp = tempSensor.getData("temp")
    else:
        temp = 70

    heatRelay = relayInterface.get_state(1)
    fanRelay = relayInterface.get_state(2)
    acRelay = relayInterface.get_state(3)

    # Write it
    with open(fileName, mode='a') as file:
        data_writer = csv.writer(file, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL)
        data_writer.writerow([now, temp, heatRelay, fanRelay, acRelay])
        # data_writer.writerow([now, heatRelay, fanRelay, acRelay])
        # print ("%s\t%.2f\t\t%d\t%d\t%d" % (now.strftime("%c"), temp, heatRelay, fanRelay, acRelay))

    # Return it
    return {
        "temp": temp,
        "heatRelay": heatRelay,
        "fanRelay": fanRelay,
        "acRelay": acRelay,
    }

def getCurrentState(tempAsInt=False):
    tmp = []
    with open(fileName, mode='r') as file:
        data_reader = csv.reader(file, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for row in data_reader:
            tmp.append(row)
    
    if(tempAsInt):
        temp = int(round(float(tmp[-1][1])))
    else:
        temp = float(tmp[-1][1])

    heatRelay = relayInterface.get_state(1)
    fanRelay = relayInterface.get_state(2)
    acRelay = relayInterface.get_state(3)

    # Return it
    return {
        "temp": temp,
        "heatRelay": heatRelay,
        "fanRelay": fanRelay,
        "acRelay": acRelay,
    }

def getSettings():
    with open('static/settings.json', mode='r') as file:
        settings = json.load(file)
        return {
            'setpoint': settings['thermostat']['setpoint'],
            'tolerance': settings['thermostat']['tolerance'],
        }

def getJSON(hoursAgo=8):
    hoursAgo = int(hoursAgo)

    # Returns last x hours of JSON-formatted data
    data = []
    tmp = []
    now = datetime.datetime.now()
    with open(fileName, mode='r') as file:
        data_reader = csv.reader(file, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL)
        headings = data_reader.__next__()
        
        # Pull in data
        for row in data_reader:
            tmp.append(row)

        # Find oldest data point less than x hours ago
        index = None
        for row in tmp:
            timestamp = datetime.datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S.%f")
            timeToCompare = now - datetime.timedelta(hours=hoursAgo)
            if(timestamp > timeToCompare):
                index = tmp.index(row)
                break
        
        # Take all the good data points and send them back
        for row in tmp[index:]:            
            data.append({
                headings[0]: row[0],
                headings[1]: row[1],
                headings[2]: row[2],
                headings[3]: row[3],
                headings[4]: row[4],
            })
    return json.dumps(data)

if __name__ == '__main__':
    if(shouldInitFile): initFile()
    while True:
        print(collectData())
        time.sleep(60)