from picosdk.ps2000 import ps2000
from matplotlib import pyplot as plt
from ctypes import c_int16, c_int32, byref
from time import sleep
import numpy as np
import csv
import os
import json

BAUD = 9600

# Initialise PicoScope
handle = ps2000.ps2000_open_unit()   # returns a scope handle (int)
if handle <= 0:
    raise RuntimeError("Failed to open scope")

# Dynamic device handling
validation_loop = True
while validation_loop:
    platform = input("Device platform type\nA) Arduino\nB) Raspberry Pi\nC) ESP\n0) Not listed\n> ")
    if platform.lower() in ['a', 'b', 'c', '0']:
        validation_loop = False
    else:
        print("Invalid input")


validation_loop = True
while validation_loop:
    validation_loop = False
    if platform.lower() == 'a':
        platform = 'Arduino'
        model = input("Device model\nA) Nano\nB) UNO\n0) Not listed\n> ")
        if model.lower() not in ['a', 'b', '0']:
            print("Invalid input")
            validation_loop = True
        elif model.lower() == 'a':
            model = 'Nano'
        elif model.lower() == 'b':
            model = 'UNO'
    elif platform.lower() == 'b':
        platform = 'RPi'
        model = input("A) 5B\n0) Not listed\n> ")
    elif platform.lower() == 'c':
        platform = 'ESP'
        model = input("A) 32\n0) Not listed\n> ")
    elif platform == '0':
        pass
    else:
        print("Invalid input")
        validation_loop = True

validation_loop = True
while validation_loop:
    validation_loop = False
    data_size = input("Data size\nA) Small\nB) Medium\nc) Large\n> ")
    if data_size.lower() == 'a':
        data_size = 'Small'
    elif data_size.lower() == 'b':
        data_size = 'Medium'
    elif data_size.lower() == 'c':
        data_size = 'Large'
    else:
        print("Invalid input")
        validation_loop = True
    

# Channel
# handle, channel (0: A, 1: B), enabled/disabled, DC, range (1 to 10, 8 = 5v)
channel = 0
enabled = True
Dc = True
volt_range = 8
ps2000.ps2000_set_channel(handle, channel, enabled, Dc, volt_range)



# timebase
# handle, timebase, sample_number, *time_interval, *time_units, oversample, *max_samples
timebase        = c_int16(11) 
samples_num     = c_int32(3968) # max is 3968
time_interval   = c_int32(0)
time_units      = c_int16(0)
oversample      = c_int16(1)
max_samples     = c_int32(0)
time_satus = ps2000.ps2000_get_timebase(handle, timebase, samples_num, byref(time_interval), byref(time_units), oversample, byref(max_samples))

print(time_interval.value, " ", time_units.value, " ", max_samples.value)

# trigger
# handle, source(channel), threshold, direction (falling = 1), delay, delayed_trigger (guarantee trigger after delay)
threshold = int(2.5 * 32767 / 5) # 2.5V threshold
direction = 1
delay = int(0.002/time_interval.value)  # 2ms min idle time before trigger
delayed_trigger = 0 # 0 = indefinite
ps2000.ps2000_set_trigger(handle, channel, threshold, direction, delay, delayed_trigger)
# While loop to capture entire waveform in chunks

# Run the block capture
# handle, sample_number, timebase, oversample, *time_indisposed (pointer to time taken to collect data)
time_indisposed = byref(c_int32(0))
ps2000.ps2000_run_block(handle, samples_num, timebase, oversample, time_indisposed)

# Wait for picoScope to be ready
ready_check = ps2000.ps2000_ready(handle)
while not ready_check:
    ready_check = ps2000.ps2000_ready(handle)
    sleep(0.001)


# Allocate buffer arrays
times = (c_int32 * samples_num.value)()
buffer_a = (c_int16 * samples_num.value)()
buffer_b = (c_int16 * samples_num.value)()
buffer_c = (c_int16 * samples_num.value)()
buffer_d = (c_int16 * samples_num.value)()
overflow = (c_int16 * samples_num.value)()

values = ps2000.ps2000_get_times_and_values(
    handle,
    byref(times),
    byref(buffer_a),
    byref(buffer_b),
    byref(buffer_c),
    byref(buffer_d),
    byref(overflow),
    time_units,
    c_int32(samples_num.value)
)

if values <= 0:
    raise RuntimeError(f"ps2000_get_times_and_values failed with value: {values}")


voltage = 5
channel_a_volts = [x * voltage / 32767 for x in buffer_a]

ps2000.ps2000_close_unit(handle)

time_list = list(times)
channel_a_list = list(channel_a_volts)


voltage_threshold = 2.5
logic_levels = [1 if v > voltage_threshold else 0 for v in channel_a_volts]
sample_period = time_interval.value * 1e-9
samples_per_bit = int(1 / (BAUD * sample_period))
print(f"Samples per bit: {samples_per_bit}")
decoded_bytes = []



# UART decoding
frame_length = int(10 * samples_per_bit)  # 1 start + 8 data + 1 stop

min_idle_samples = int(0.7 * samples_per_bit)  

start_bits = []

i = 0
while i < len(logic_levels):
    # Only detect start bit if previous min_idle_samples are high
    if (
        i > min_idle_samples
        and all(logic_levels[i - min_idle_samples : i])  # Idle before falling edge
        and logic_levels[i - 1] == 1
        and logic_levels[i] == 0
    ):
        start_bits.append(i)
        bits = []
        for bit in range(1, 10):
            sample_idx = int(i + (bit - 0.5) * samples_per_bit)
            if sample_idx < len(logic_levels):
                bits.append(logic_levels[sample_idx])
        if len(bits) >= 9:
            data_bits = bits[1:9]
            byte = 0
            for j, b in enumerate(data_bits):
                byte |= (b << j)
            decoded_bytes.append(byte)
        i += frame_length
    else:
        i += 1

print("Decoded UART bytes:", decoded_bytes)

for byte in decoded_bytes:
    if 32 <= byte <= 126:
        print(chr(byte), end='')
    else:
        print('.', end='')


# Plot
plt.plot(time_list, channel_a_list)

plt.xlabel("Time (ns)")     
plt.ylabel("Amplitude (V)")
plt.grid(True)

start_bit_times = [time_list[idx] for idx in start_bits]
start_bit_volts = [channel_a_list[idx] for idx in start_bits]
plt.scatter(start_bit_times, start_bit_volts, color='red', label='Start Bits')

plt.legend()
plt.show()


# Data extraction

dir = F"./Data/{platform}/{model}/"

CSV_num = 0
with open('./Data/metadata.json', 'r+') as f:
    data = json.load(f)
    CSV_num = data[platform][model][f'Captures_{data_size}'] + 1
    data[platform][model][f'Captures_{data_size}'] = CSV_num
    f.seek(0)
    json.dump(data, f, indent=4)
    f.truncate()
with open(dir + f'votlages_{data_size}_{CSV_num}.csv', "w", newline='') as f:
    writer = csv.writer(f)
    writer.writerow(["Time (ns)", "Voltage (V)"])
    for t, v in zip(time_list, channel_a_volts):
        writer.writerow([t, v])
print(f"\nData saved to {dir}voltages_{data_size}_{CSV_num}.csv")
