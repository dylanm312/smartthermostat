"""
The main script for the smart thermostat.

Running this script directly does two things:
1. Launches the thermostat background task in a separate thread, and
2. Launches the Flask webapp
"""

import json
import threading
from flask import Flask, render_template
from flask_bootstrap import Bootstrap
import data_collector
import thermostat
import relay_interface as relays

# Initial setup
app = Flask(__name__)
Bootstrap(app)

# Params
HOURS_AGO = 2
TEMP_DISPLAY_PRECISION = 1

@app.route('/')
def index():
    """Loads the root page of the webapp."""
    template_data = {
        'relay1state': relays.get_state(1),
        'relay2state': relays.get_state(2),
        'relay3state': relays.get_state(3),
        'settings': data_collector.get_settings(),
        'current': data_collector.get_current_state(TEMP_DISPLAY_PRECISION),
        'hoursAgo': HOURS_AGO,
        'precision': TEMP_DISPLAY_PRECISION,
    }
    return render_template('index.html', data=template_data)

@app.route('/relay<relay_num>/on')
def relay_on(relay_num):
    """Turn a relay on."""
    relays.set_state(int(relay_num), "on")
    return "Relay %s turned ON" % relay_num

@app.route('/relay<relay_num>/off')
def relay_off(relay_num):
    """Turn a relay off."""
    relays.set_state(int(relay_num), "off")
    return "Relay %s turned OFF" % relay_num

@app.route('/relay<relay_num>/getState')
def relay_state(relay_num):
    """Get current state of a relay."""
    return "Relay %s state: %s" % (relay_num, relays.get_state(int(relay_num)))

@app.route('/getCurrentState/<precision>')
def get_current_state(precision):
    """Get current system state (temp and relays)."""
    return data_collector.get_current_state(int(precision))

@app.route('/collectData')
def collect_data():
    """Collect a new data point and store it."""
    return data_collector.collect_data()

@app.route('/setTemp/<temp>')
def set_temp(temp):
    """Set temperature setpoint."""
    temp = float(temp)

    # Read in current settings
    with open('static/settings.json', mode='r') as file:
        settings = json.load(file)

    # Change the setpoint
    settings['thermostat']['setpoint'] = temp

    # Write settings back
    with open('static/settings.json', mode='w') as file:
        file.write(json.dumps(settings, indent=4)) # indent setting makes it pretty

    # Recalculate thermostat actions
    thermostat.run_thermostat(temp=temp)

    # Success! :)
    return "Temperature setpoint set to: %d" % temp

@app.route('/setTol/<tol>')
def set_tol(tol):
    """Set tolerance."""
    tol = float(tol)

    # Read in current settings
    with open('static/settings.json', mode='r') as file:
        settings = json.load(file)

    # Change the setpoint
    settings['thermostat']['tolerance'] = tol

    # Write settings back
    with open('static/settings.json', mode='w') as file:
        file.write(json.dumps(settings, indent=4)) # indent setting makes it pretty

    # Recalculate thermostat actions
    thermostat.run_thermostat(tol=tol)

    # Success! :)
    return "Temperature tolerance set to plus or minus %d degrees F." % tol

@app.route('/getJSON/<hours_ago>')
def get_json(hours_ago):
    """Return JSON system status data from the past x hours."""
    return data_collector.get_json(hours_ago)

if __name__ == '__main__':
    dataThread = threading.Thread(target=data_collector.run)
    dataThread.start()

    app.run(debug=True, host='0.0.0.0')
