import dataCollector
import json
import relayInterface as relays
from time import sleep

def runThermostat(debug=True):
    with open('static/settings.json') as file:
        # Load in current settings
        settings = json.load(file)
        setpoint = settings['thermostat']['setpoint']
        tol = settings['thermostat']['tolerance']

        # Load in current temperature
        temp = dataCollector.getCurrentState()['temp']

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
        if(temp > setpoint + tol and relays.get_state(relays.RELAY_AC) == 0): # Too hot, cool
            relays.set_state(relays.RELAY_HEAT, "off")
            relays.set_state(relays.RELAY_AC, "on")
            if(debug): print("AC turned on")
        
        elif(temp < setpoint - tol and relays.get_state(relays.RELAY_HEAT) == 0): # Too cold, heat
            relays.set_state(relays.RELAY_AC, "off")
            relays.set_state(relays.RELAY_HEAT, "on")
            if(debug): print("Heat turned on")
        
        elif(temp < setpoint + tol and temp > setpoint - tol and (\
                relays.get_state(relays.RELAY_HEAT) == 1 or \
                relays.get_state(relays.RELAY_AC) == 1)): # Juuuust right :)
            
            relays.set_state(relays.RELAY_HEAT, "off")
            relays.set_state(relays.RELAY_AC, "off")
            if(debug): print("HVAC turned off")
        else:
            if(debug): print("No changes needed")
    if(debug):
        print("Sleeping...")
        print("\n")


if __name__ == '__main__':
    while True:
        runThermostat()
        sleep(60)