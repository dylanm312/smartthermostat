"""
Collect data from temperature sensor and relays.

Also read and write to/from data csv
"""
import csv
import json
import time
import datetime
from flask import jsonify
import thermostat
import temp_sensor_interface as temp_sensor
import relay_interface as relays

FILE_NAME = 'static/data.csv'

# Set to False if temp sensor is disconnected to avoid spinning
# forever as we wait for the serial stream to come in
TEMP_SENSOR_CONNECTED = True

# Set to true to initialize data file. THIS WILL ERASE ALL RECORDED DATA!! USE WITH CAUTION!!
SHOULD_INIT_FILE = False

DEBUG = False

def init_file():
    """Initialize the data file, clearing existing data and setting up headings."""
    # Open CSV for data, or create if not exist. Set up CSV writer.
    with open(FILE_NAME, mode='w') as file:
        data_writer = csv.writer(file, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL)
        # Set CSV column headings
        data_writer.writerow( \
            ["Timestamp", "Temperature (F)", "Heat Relay", "Fan Relay", "A/C Relay"] \
        )

def collect_data():
    """Collect a new data point, store it, and return it."""
    # Get current timestamp
    now = datetime.datetime.now()

    # Collect relay states
    heat_relay = relays.get_state(relays.RELAY_HEAT)
    fan_relay = relays.get_state(relays.RELAY_FAN)
    ac_relay = relays.get_state(relays.RELAY_AC)

    # Collect temp sensor data (if it decides to work)
    if TEMP_SENSOR_CONNECTED:
        # Pull in data
        try:
            temp = temp_sensor.get_data()
        except (ValueError, TypeError, IndexError):
            print("Temp sensor issue, skipping...")
            return {
                "temp": None,
                "heatRelay": heat_relay,
                "fanRelay": fan_relay,
                "acRelay": ac_relay,
            }
    else:
        temp = 70

    # Write it
    with open(FILE_NAME, mode='a') as file:
        data_writer = csv.writer(file, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL)
        data_writer.writerow([now, temp, heat_relay, fan_relay, ac_relay])

    # Run thermostat with new data
    thermostat.run_thermostat(temp=temp)

    if DEBUG:
        print("Temp\t|Heat\t|Fan\t|AC")
        print("%s\t|%s\t|%s\t|%s" % (temp, heat_relay, fan_relay, ac_relay))

    # Return it
    return {
        "temp": temp,
        "heat_relay": heat_relay,
        "fan_relay": fan_relay,
        "ac_relay": ac_relay,
    }

def get_current_state(precision=1):
    """
    Return the current system state.

    Precision: number of decimal places for temperature value to return
    """
    tmp = []
    with open(FILE_NAME, mode='r') as file:
        data_reader = csv.reader(file, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for row in data_reader:
            tmp.append(row)

    # Sometimes sensor feeds a blank string instead of a temp.
    # Get the second to last state instead in that case
    try:
        temp = float(tmp[-1][1])
    except ValueError:
        temp = float(tmp[-2][1])

    # Round to appropriate decimal place
    temp = float(round(temp, int(precision)))

    heat_relay = relays.get_state(relays.RELAY_HEAT)
    fan_relay = relays.get_state(relays.RELAY_FAN)
    ac_relay = relays.get_state(relays.RELAY_AC)

    # Return it
    return {
        "temp": temp,
        "heat_relay": heat_relay,
        "fan_relay": fan_relay,
        "ac_relay": ac_relay,
    }

def get_settings():
    """Return settings from settings.json."""
    with open('static/settings.json', mode='r') as file:
        settings = json.load(file)
        return {
            'setpoint': settings['thermostat']['setpoint'],
            'tolerance': settings['thermostat']['tolerance'],
        }

def get_json(hours_ago=8):
    """Return json system data from data.csv."""
    hours_ago = int(hours_ago)

    # Returns last x hours of JSON-formatted data
    data = []
    tmp = []
    now = datetime.datetime.now()
    with open(FILE_NAME, mode='r') as file:
        data_reader = csv.reader(file, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL)
        headings = data_reader.__next__()

        # Pull in data
        for row in data_reader:
            tmp.append(row)

        # Find oldest data point less than x hours ago
        index = None
        for row in tmp:
            timestamp = datetime.datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S.%f")
            time_to_compare = now - datetime.timedelta(hours=hours_ago)
            if timestamp > time_to_compare:
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
    return jsonify(data)

def run():
    """Collect a new data point every minute."""
    if SHOULD_INIT_FILE:
        init_file()
    while True:
        collect_data()
        time.sleep(60)

if __name__ == '__main__':
    run()
