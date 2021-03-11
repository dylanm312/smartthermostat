from flask import Flask, render_template
from flask_bootstrap import Bootstrap
import relayInterface as relays
import dataCollector
import thermostat
import json
import threading

# Initial setup
app = Flask(__name__)
Bootstrap(app)

# Params
hoursAgo = 2

@app.route('/')
def index():
	jsonData = dataCollector.getJSON(hoursAgo)

	template_data = {
		'relay1state': relays.get_state(1),
		'relay2state': relays.get_state(2),
		'relay3state': relays.get_state(3),
		'settings': dataCollector.getSettings(),
		'current': dataCollector.getCurrentState(tempAsInt=True),
		'hoursAgo': hoursAgo,
	}
	return render_template('index.html', data=template_data)

@app.route('/relay<relayNum>/on')
def relayOn(relayNum):
	relays.set_state(int(relayNum), "on")
	return "Relay %s turned ON" % relayNum

@app.route('/relay<relayNum>/off')
def relayOff(relayNum):
	relays.set_state(int(relayNum), "off")
	return "Relay %s turned OFF" % relayNum

@app.route('/relay<relayNum>/getState')
def relayState(relayNum):
	return "Relay %s state: %s" % (relayNum, relays.get_state(int(relayNum)))

@app.route('/getCurrentState/<tempAsInt>')
def getCurrentState(tempAsInt):
	return dataCollector.getCurrentState(bool(tempAsInt))

@app.route('/collectData')
def collectData():
	return dataCollector.collectData()

@app.route('/setTemp/<temp>')
def setTemp(temp):
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
	thermostat.runThermostat()

	# Success! :)
	return "Temperature setpoint set to: %d" % temp

@app.route('/setTol/<tol>')
def setTol(tol):
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
	thermostat.runThermostat()

	# Success! :)
	return "Temperature tolerance set to plus or minus %d degrees F." % tol

@app.route('/getJSON/<hoursAgo>')
def getJSON(hoursAgo):
	return dataCollector.getJSON(hoursAgo)

def run():
	app.run(debug=True, host='0.0.0.0')

if __name__ == '__main__':
	dataThread = threading.Thread(target=dataCollector.run)
	dataThread.start()
	
	run()
