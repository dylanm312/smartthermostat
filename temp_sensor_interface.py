"""
Connect to and return data from temperature sensor.
"""

import serial

# Params
DEBUG = False

def connect_to_sensor(port="/dev/ttyS0", baud=38400):
    """Return a serial connection to the temperature sensor."""
    serial_connection = serial.Serial(port, baud)
    return serial_connection

def get_data():
    """Return a new data point from the temp sensor."""
    with connect_to_sensor() as serial_connection:
        # Read one line from the serial buffer
        try:
            raw_data = serial_connection.readline()\
                                       .decode(encoding='utf-8', errors='strict')[:-2]\
                                       .split(",") # Need to drop /r/n after each line

            if DEBUG:
                print("*** TEMPSENSOR LEN ***: " + str(len(raw_data)))
                for val in raw_data:
                    print("*** TEMPSENSOR ***: " + val)

            temp = convert_to_f(raw_data[4])
            return temp

        except KeyboardInterrupt:
            print("\nCtrl-C detected, exiting...")
            exit()

def get_raw_data():
    """Return array of sensor data, without unit conversions."""
    with connect_to_sensor() as conn:
        raw_data = conn.readline().decode(encoding='utf-8', errors='strict')[:-2].split(",")
        print(raw_data)

def convert_to_f(degrees_c):
    """Return degrees Fahrenheit."""
    return float(degrees_c) * 9/5 + 32

if __name__ == "__main__":
    connection = connect_to_sensor('/dev/ttyS0', 38400)
    i = 0
    print("Curr. 1 (W) | Curr. 2 (W) | Curr. 3 (W) | Temp. (F)")
    while True:
        data = get_data()
        print("%.2f W     | %.2f W      | %.2f W      | %.2f F" % \
             (data[0],      data[1],      data[2],      data[3]))
