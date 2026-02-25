import serial
import sys
import struct
import matplotlib.pyplot as plt
import time

count = 0
x = [0]
y = [0]
us = [0]
current_rpm = 0
set_rpm = 1000
Kp = 0.1
Ki = 0.001
# Kp = 0.005960000
# Ki = 0.028408163
# Ki = 0


error = 0
ierror = 0
past_error = 0
current_time = time.time()
past_time = time.time()
start_time = time.time()


def graph_results():
    fig, ax1 = plt.subplots()

# First signal on left axis
    ax1.plot(x, y, color='tab:blue', label='RPM')
    ax1.set_xlabel("Time (s)")
    ax1.set_ylabel("Motor Speed (RPM)", color='tab:blue')
    ax1.tick_params(axis='y', labelcolor='tab:blue')

# Second signal on right axis
    ax2 = ax1.twinx()
    ax2.plot(x, us, color='tab:red', label='SET VOLTAGE')
    ax2.set_ylabel("Control Signal 2 (V)", color='tab:red')
    ax2.tick_params(axis='y', labelcolor='tab:red')

    plt.title("Control Motor")
    plt.show()


def on_close():
    value_to_send = 0
    little_endian_bytes = value_to_send.to_bytes(length=1, byteorder='little')

    ser.write(little_endian_bytes)

    graph_results()

    ser.close()
    plt.close('all')
    print("Cleanup complete")
    exit()


if sys.platform.startswith('win'):
    ser = serial.Serial('COM3', 9600, timeout=None)
else:
    ser = serial.Serial('/dev/ttyACM0', 9600, timeout=None)

time.sleep(2)  # Wait for Arduino reset
ser.reset_input_buffer()

print("Starting data collection...")

while time.time() - start_time < 5:
    current_time = time.time()

    error = set_rpm - current_rpm
    dt = current_time - past_time
    ierror += error * dt

    u = Kp * error + Ki * ierror
    past_time = current_time

    print("u ", u)

    if u > 5:
        u = 5
    if u < 0:
        u = 0

    us.append(u)

    print("maxed u ", u)

    value_to_send = int(u * 255/5)

    print("send value ", value_to_send)

    # value_to_send = 75
    little_endian_bytes = value_to_send.to_bytes(
        length=1, byteorder='little')
    ser.write(little_endian_bytes)

    data = ser.read(4)

    if len(data) == 4:
        value = struct.unpack('<f', data)[0]
        print(value)
        y.append(value)
        x.append(x[-1] + 1)

        current_rpm = value

    else:
        print(f"Warning: got {len(data)} bytes instead of 4")
on_close()
