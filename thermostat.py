import dataCollector
import json
import relayInterface as relays

debug = False
turnOffTolerance = 0.1 # Tolerance range for setpoint and temp to be considered 'equal'

def runThermostat(temp=None, setpoint=None, tol=None):
    with open('static/settings.json') as file:
        # Load in current settings (if they are not provided)
        settings = json.load(file)

        if(setpoint==None):
            setpoint = settings['thermostat']['setpoint']
        if(tol==None):
            tol = settings['thermostat']['tolerance']

        systemHasHeat = settings['hvac']['components']['heat']
        systemHasAC = settings['hvac']['components']['ac']

    # Get current temp
    if(temp==None):
        temp = float(dataCollector.getCurrentState()['temp'])

    # Get current system status
    heatIsOn = relays.get_state(relays.RELAY_HEAT)
    acIsOn = relays.get_state(relays.RELAY_AC)

    if(debug):
        print("------- THERMO PARAMS ------")
        print("Current temp: %d" % temp)
        print("Setpoint: %d" % setpoint)
        print("Tolerance: %d" % tol)
        print("------- RELAY STATES -------")
        print("Heat: %d" % relays.get_state(relays.RELAY_HEAT))
        print("Fan: %d" % relays.get_state(relays.RELAY_FAN))
        print("A/C: %d" % relays.get_state(relays.RELAY_AC))

    # See what we need to do
    # Is the system currently on? If so, wait till we get to the setpoint before turning off
    if((heatIsOn or acIsOn) and \
        temp >= (setpoint-turnOffTolerance) and \
        temp <= (setpoint+turnOffTolerance)): # Give a slight tolerance range since we will likely never be right on the money
        off()

    elif(temp > setpoint + tol and (acIsOn == 0) and systemHasAC): # Too hot, cool
        cool()
    
    elif(temp < setpoint - tol and (heatIsOn == 0) and systemHasHeat): # Too cold, heat
        heat()

    else:
        if(debug): print("No changes needed")

def heat():
    relays.set_state(relays.RELAY_AC, "off")
    relays.set_state(relays.RELAY_HEAT, "on")
    if(debug): print("Heat turned on")   

def cool():
    relays.set_state(relays.RELAY_HEAT, "off")
    relays.set_state(relays.RELAY_AC, "on")
    if(debug): print("AC turned on")

def off():
    relays.set_state(relays.RELAY_HEAT, "off")
    relays.set_state(relays.RELAY_AC, "off")
    if(debug): print("HVAC turned off")

# if __name__ == '__main__':
  #  while True:
  #      runThermostat()
  #      sleep(60)
