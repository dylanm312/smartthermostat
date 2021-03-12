"""
Make decisions about thermostat functions.

Looks at the current temperature, relay states,
setpoint, and tolerance, and decides whether to
turn on heat, turn on AC, leave system as-is,
or turn everything off.
"""
import json
import data_collector
import relay_interface as relays

DEBUG = False
TURN_OFF_TOLERANCE = 0.1 # Tolerance range for setpoint and temp to be considered 'equal'

def run_thermostat(temp=None, setpoint=None, tol=None):
    """Make thermostat decisions."""
    with open('static/settings.json') as file:
        # Load in current settings (if they are not provided)
        settings = json.load(file)

        if setpoint is None:
            setpoint = settings['thermostat']['setpoint']
        if tol is None:
            tol = settings['thermostat']['tolerance']

        system_has_heat = settings['hvac']['components']['heat']
        system_has_ac = settings['hvac']['components']['ac']

    # Get current temp
    if temp is None:
        temp = float(data_collector.get_current_state()['temp'])

    # Get current system status
    heat_is_on = relays.get_state(relays.RELAY_HEAT)
    ac_is_on = relays.get_state(relays.RELAY_AC)

    if DEBUG:
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
    if((heat_is_on or ac_is_on) and \
        temp >= (setpoint-TURN_OFF_TOLERANCE) and \
        temp <= (setpoint+TURN_OFF_TOLERANCE)): # Give a slight tolerance range
                                                # since we will likely never be right on the money
        off()

    elif(temp > setpoint + tol and (ac_is_on == 0) and system_has_ac): # Too hot, cool
        cool()

    elif(temp < setpoint - tol and (heat_is_on == 0) and system_has_heat): # Too cold, heat
        heat()

    else:
        if DEBUG:
            print("No changes needed")

def heat():
    """Set system to heat."""
    relays.set_state(relays.RELAY_AC, "off")
    relays.set_state(relays.RELAY_HEAT, "on")
    if DEBUG:
        print("Heat turned on")

def cool():
    """Set system to cool."""
    relays.set_state(relays.RELAY_HEAT, "off")
    relays.set_state(relays.RELAY_AC, "on")
    if DEBUG:
        print("AC turned on")

def off():
    """Turn system off."""
    relays.set_state(relays.RELAY_HEAT, "off")
    relays.set_state(relays.RELAY_AC, "off")
    if DEBUG:
        print("HVAC turned off")

# if __name__ == '__main__':
  #  while True:
  #      run_thermostat()
  #      sleep(60)
