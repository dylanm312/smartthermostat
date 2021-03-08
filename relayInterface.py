from gpiozero import OutputDevice
from time import sleep

relay1 = OutputDevice(26) # physical pin 26
relay2 = OutputDevice(20) # physical pin 20
relay3 = OutputDevice(21) # physical pin 21

# Relay lookup
relays = {
    1: relay1,
    2: relay2,
    3: relay3,
}

RELAY_HEAT = 1
RELAY_FAN = 2
RELAY_AC = 3

def set_state(relay, state):
    targetRelay = relays[relay]
    if(state=="on"):
        targetRelay.on()
    elif(state=="off"):
        targetRelay.off()
    else:
        raise TypeError("Invalid state")

def get_state(relay):
    return relays[relay].value

# Functionality check
if __name__ == "__main__":
    for i in relays:
        print("Testing relay %s..." % i)

        set_state(i, "on")
        assert get_state(i) == 1
        sleep(0.5)

        set_state(i, "off")
        assert get_state(i) == 0
        sleep(0.5)
    
    print("Relay test completed successfully :)")