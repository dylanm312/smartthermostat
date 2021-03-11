import tempSensorInterface as tempSensor
import csv
import datetime
import relayInterface as relays
import time
import json
import thermostat

fileName = 'data.csv'

# Set to False if temp sensor is disconnected to avoid spinning 
# forever as we wait for the serial stream to come in
tempSensorConnected = True

# Set to true to initialize data file. THIS WILL ERASE ALL RECORDED DATA!! USE WITH CAUTION!!
shouldInitFile = False

debug = False

def initFile():
    # Open CSV for data, or create if not exist. Set up CSV writer.
    with open(fileName, mode='w') as file:
        data_writer = csv.writer(file, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL)
        # Set CSV column headings
        data_writer.writerow(["Timestamp", "Temperature (F)", "Heat Relay", "Fan Relay", "A/C Relay"])

def collectData():
    # Get current timestamp
    now = datetime.datetime.now()

    # Collect relay states
    heatRelay = relays.get_state(relays.RELAY_HEAT)
    fanRelay = relays.get_state(relays.RELAY_FAN)
    acRelay = relays.get_state(relays.RELAY_AC)

    # Collect temp sensor data (if it decides to work)
    if(tempSensorConnected):
        # Pull in data
        try:
            temp = tempSensor.getData()
        except:
            print("Temp sensor issue, skipping...")
            return {
                "temp": None,
                "heatRelay": heatRelay,
                "fanRelay": fanRelay,
                "acRelay": acRelay,
            }
    else:
        temp = 70

    # Write it
    with open(fileName, mode='a') as file:
        data_writer = csv.writer(file, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL)
        data_writer.writerow([now, temp, heatRelay, fanRelay, acRelay])
        # data_writer.writerow([now, heatRelay, fanRelay, acRelay])
        # print ("%s\t%.2f\t\t%d\t%d\t%d" % (now.strftime("%c"), temp, heatRelay, fanRelay, acRelay))

    # Run thermostat with new data
    thermostat.runThermostat(temp=temp)

    if(debug):
        print("Temp\t|Heat\t|Fan\t|AC")
        print("%s\t|%s\t|%s\t|%s" % (temp, heatRelay, fanRelay, acRelay))

    # Return it
    return {
        "temp": temp,
        "heatRelay": heatRelay,
        "fanRelay": fanRelay,
        "acRelay": acRelay,
    }

def getCurrentState(precision=1):
    tmp = []
    with open(fileName, mode='r') as file:
        data_reader = csv.reader(file, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for row in data_reader:
            tmp.append(row)
    
    # Sometimes sensor feeds a blank string instead of a temp. Get the second to last state instead in that case
    try:
        temp = float(tmp[-1][1])
    except ValueError:
        temp = float(tmp[-2][1])

    # Round to appropriate decimal place
    temp = float(round(temp, int(precision)))

    heatRelay = relays.get_state(relays.RELAY_HEAT)
    fanRelay = relays.get_state(relays.RELAY_FAN)
    acRelay = relays.get_state(relays.RELAY_AC)

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

def run():
    if(shouldInitFile): initFile()
    while True:
        collectData()
        time.sleep(60)

if __name__ == '__main__':
    run()
