"""
Instructions from here (http://lechacal.com/wiki/index.php?title=Howto_setup_Raspbian_for_serial_read)

Step 1: Enter "sudo raspi-config" in terminal
Step 2: Navigate to Interface options, then P6 Serial, select no then yes
Step 3: Update RPi with "sudo apt-get update"
Step 4: Reboot RPi with "sudo reboot & exit"
Step 5: Run file
"""

import serial

# Params
debug = False

def connectToSensor(port="/dev/ttyS0", baud=38400):
    serialConnection = serial.Serial(port, baud)
    return(serialConnection)

def getData():
    with connectToSensor() as serialConnection:
        # Read one line from the serial buffer
        try:
            rawData = serialConnection.readline().decode(encoding='utf-8', errors='strict')[:-2].split(",") # Need to drop /r/n after each line
            
            if(debug):
                print("*** TEMPSENSOR LEN ***: " + str(len(rawData)))
                for i in rawData:
                    print("*** TEMPSENSOR ***: " + i)
            
            data = convertToF(rawData[4])
            return(data)

        except KeyboardInterrupt:
            print("\nCtrl-C detected, exiting...")
            exit()

def getRawData():
    with connectToSensor() as conn:
        data = conn.readline().decode(encoding='utf-8', errors='strict')[:-2].split(",")
        print(data)

# Helper functions
def convertTo110(watts220):
    return float(watts220)/2

def convertToF(degreesC):
    return float(degreesC) * 9/5 + 32

if __name__ == "__main__":
    connection = connectToSensor('/dev/ttyS0', 38400)
    i = 0
    print("Curr. 1 (W) | Curr. 2 (W) | Curr. 3 (W) | Temp. (F)")
    while True:
        data = getData()
        print("%.2f W     | %.2f W      | %.2f W      | %.2f F" % (data[0], data[1], data[2], data[3]))
