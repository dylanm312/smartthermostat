"""
Instructions from here (http://lechacal.com/wiki/index.php?title=Howto_setup_Raspbian_for_serial_read)

Step 1: Enter "sudo raspi-config" in terminal
Step 2: Navigate to Interface options, then P6 Serial, select no then yes
Step 3: Update RPi with "sudo apt-get update"
Step 4: Reboot RPi with "sudo reboot & exit"
Step 5: Run file
"""

import serial

def connectToSensor(port="/dev/ttyS0", baud=38400):
    serialConnection = serial.Serial(port, baud)
    return(serialConnection)

def getData(dataType="all"):
    with connectToSensor() as serialConnection:
        # Read one line from the serial buffer
        try:
            rawData = serialConnection.readline().decode(encoding='utf-8', errors='strict').split(" ")

            data = [None, None, None, None]
            # data[0] is some ID thing, useless to us
            data[0] = convertTo110(rawData[1])
            data[1] = convertTo110(rawData[2])
            data[2] = convertTo110(rawData[3])
            data[3] = convertToF(rawData[4])

            if(dataType=="power"):
                return float(data[0])
            elif(dataType=="temp"):
                return float(data[3])

            return(data)

        except KeyboardInterrupt:
            print("\nCtrl-C detected, exiting...")
            exit()

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
