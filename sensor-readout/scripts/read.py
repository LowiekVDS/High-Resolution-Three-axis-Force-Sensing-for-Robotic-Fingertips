import serial

mlx90393_lsb_lookup = [
    # HALLCONF = 0xC (default)
    [
        # GAIN_SEL = 0, 5x gain
        [[0.751, 1.210], [1.502, 2.420], [3.004, 4.840], [6.009, 9.680]],
        # GAIN_SEL = 1, 4x gain
        [[0.601, 0.968], [1.202, 1.936], [2.403, 3.872], [4.840, 7.744]],
        # GAIN_SEL = 2, 3x gain
        [[0.451, 0.726], [0.901, 1.452], [1.803, 2.904], [3.605, 5.808]],
        # GAIN_SEL = 3, 2.5x gain
        [[0.376, 0.605], [0.751, 1.210], [1.502, 2.420], [3.004, 4.840]],
        # GAIN_SEL = 4, 2x gain
        [[0.300, 0.484], [0.601, 0.968], [1.202, 1.936], [2.403, 3.872]],
        # GAIN_SEL = 5, 1.667x gain
        [[0.250, 0.403], [0.501, 0.807], [1.001, 1.613], [2.003, 3.227]],
        # GAIN_SEL = 6, 1.333x gain
        [[0.200, 0.323], [0.401, 0.645], [0.801, 1.291], [1.602, 2.581]],
        # GAIN_SEL = 7, 1x gain
        [[0.150, 0.242], [0.300, 0.484], [0.601, 0.968], [1.202, 1.936]]
    ],
    # HALLCONF = 0x0
    [
        # GAIN_SEL = 0, 5x gain
        [[0.787, 1.267], [1.573, 2.534], [3.146, 5.068], [6.292, 10.137]],
        # GAIN_SEL = 1, 4x gain
        [[0.629, 1.014], [1.258, 2.027], [2.517, 4.055], [5.034, 8.109]],
        # GAIN_SEL = 2, 3x gain
        [[0.472, 0.760], [0.944, 1.521], [1.888, 3.041], [3.775, 6.082]],
        # GAIN_SEL = 3, 2.5x gain
        [[0.393, 0.634], [0.787, 1.267], [1.573, 2.534], [3.146, 5.068]],
        # GAIN_SEL = 4, 2x gain
        [[0.315, 0.507], [0.629, 1.014], [1.258, 2.027], [2.517, 4.055]],
        # GAIN_SEL = 5, 1.667x gain
        [[0.262, 0.422], [0.524, 0.845], [1.049, 1.689], [2.097, 3.379]],
        # GAIN_SEL = 6, 1.333x gain
        [[0.210, 0.338], [0.419, 0.676], [0.839, 1.352], [1.678, 2.703]],
        # GAIN_SEL = 7, 1x gain
        [[0.157, 0.253], [0.315, 0.507], [0.629, 1.014], [1.258, 2.027]]
    ]
]

gain = 3
res = 3

# Define the serial port name and baud rate
ser = serial.Serial('/dev/ttyACM1', 115200)  # Replace 'COM1' with the name of your serial port

import csv
import time

t0 = time.time()

with open('data.csv', 'w', newline='') as csvfile:
    csv_writer = csv.writer(csvfile)
    csv_writer.writerow(["t", "X0", "Y0", "Z0", "X1", "Y1", "Z1", "X2", "Y2", "Z2", "X3", "Y3", "Z3"])  # Header row

    while True:
        data = ser.read(1)  # Read one byte at a time
        if data == b'\xAA':  # Check for the 0xAA byte pattern
            # Read additional bytes for parsing
            # For example, if you want to read the next 4 bytes as an integer:
            data_bytes = ser.read(6 * 4)
            
            row = [time.time()]

            print(f"Rate: {1/(time.time() - t0)}Hz")

            t0 = time.time()

            for i in range(4):
                x = (data_bytes[i * 3 * 2] << 8) + data_bytes[i * 3 * 2 + 1] - 16384
                y = (data_bytes[i * 3 * 2 + 2] << 8) + data_bytes[i * 3 * 2 + 3] - 16384
                z = (data_bytes[i * 3 * 2 + 4] << 8) + data_bytes[i * 3 * 2 + 5] - 16384

                x *= mlx90393_lsb_lookup[0][gain][res][0]
                y *= mlx90393_lsb_lookup[0][gain][res][0]
                z *= mlx90393_lsb_lookup[0][gain][res][1]

                row += [x, y, z]

                print(f"Sensor {i}, x: {x} uT, y: {y} uT, z: {z} uT")

            csv_writer.writerow(row)

ser.close()
