from ctypes import POINTER, c_int16, c_uint32
import matplotlib.pyplot as plt
import numpy as np
from picosdk.ps2000 import ps2000
from picosdk.functions import assert_pico2000_ok
from picosdk.PicoDeviceEnums import picoEnum
from picosdk.ctypes_wrapper import C_CALLBACK_FUNCTION_FACTORY
import time
import json
import csv
import scipy.signal as signal

BAUD = 9600

## Functions
# get overview buffers
CALLBACK = C_CALLBACK_FUNCTION_FACTORY(
    None,
    POINTER(POINTER(c_int16)),
    c_int16,
    c_uint32,
    c_int16,
    c_int16,
    c_uint32
)

adc_values = []


def get_overview_buffers(buffers, _overflow, _triggered_at, _triggered, _auto_stop, n_values):
    adc_values.extend(buffers[0][0:n_values])

callback = CALLBACK(get_overview_buffers)

# convert ADC to V
def adc_to_v(values, range_, bitness=16):
    v_ranges = [10, 20, 50, 100, 200, 500, 1_000, 2_000, 5_000, 10_000, 20_000]
    
    result = []
    for x in values:
        if x >= 0:
            v = ((x * v_ranges[range_]) / (2**(bitness - 1) - 1)) / 1000
        else:
            v = (x * v_ranges[range_]) / (2**(bitness - 1)) / 1000
        result.append(v)
    return result




# Dynamic device handling
voltage_threshold = 0
validation_loop = True

last_device = "./last.txt"
last_dev_data = ''
with open(last_device, 'r') as f:
    data = f.readline()
    last_dev_data = data.split(':')

    print(f"Last device\n {last_dev_data[0]}, {last_dev_data[1]}, {last_dev_data[2]}, {last_dev_data[3]}, {last_dev_data[4]}\n")

skipVal = False
while validation_loop:
    platform = input("Device platform type\nA) Arduino\nB) Raspberry Pi\nC) ESP\nZ) Last device\n0) Not listed\n> ")
    platform = platform.lower()
    if platform in ['a', 'b', 'c', 'z', '0']:
        validation_loop = False
        if platform == 'z':
            print('test')
            skipVal = True
            platform = last_dev_data[0]
            model = last_dev_data[1]
            device_voltage = float(last_dev_data[2])
            data_size = last_dev_data[3]
            BAUD = int(last_dev_data[4])
            label = last_dev_data[5]

    else:
        print("Invalid input")

if skipVal:
    validation_loop = False
else:
    validation_loop = True 
while validation_loop:
    validation_loop = False
    if platform == 'a':
        platform = 'Arduino'
        model = input("Device model\nA) Nano\nB) UNO\n0) Not listed\n> ")
        if model.lower() not in ['a', 'b', '0']:
            print("Invalid input")
            validation_loop = True
        elif model.lower() == 'a':
            model = 'Nano'
            device_voltage = 5
        elif model.lower() == 'b':
            model = 'UNO'
            device_voltage = 5

    elif platform == 'b':
        platform = 'RPi'
        model = input("A) 5B\n0) Not listed\n> ")
        if model.lower() not in ['a', '0']:
            print("Invalid input")
            validation_loop = True
        elif model.lower() == 'a':
            model = '5B'
            device_voltage = 3.3
    elif platform == 'c':
        platform = 'ESP'
        model = input("A) 32\n0) Not listed\n> ")
        if model.lower() not in ['a', '0']:
            print("Invalid input")
            validation_loop = True
        elif model.lower() == 'a':
            model = '32'
            device_voltage = 3.3
    elif platform == '0':
        pass
    else:
        print("Invalid input")
        validation_loop = True


if skipVal:
    print('test')
    print(data_size)
    validation_loop = False 
    if data_size == 'Small':
        capture_time = 250_000_000  
    if data_size == 'Medium':
        capture_time = 500_000_000  
    if data_size == 'Large':
        capture_time = 1_000_000_000  
else:
    validation_loop = True 

while validation_loop:
    validation_loop = False
    data_size = input("Data size\nA) Small\nB) Medium\nc) Large\n> ")
    if data_size.lower() == 'a':
        data_size = 'Small'
        capture_time = 250_000_000       
    elif data_size.lower() == 'b':
        data_size = 'Medium'
        capture_time = 500_000_000
    elif data_size.lower() == 'c':
        data_size = 'Large'
        capture_time = 1_000_000_000
    else:
        print("Invalid input")
        validation_loop = True

if skipVal:
    validation_loop = False   
else:
    validation_loop = True 
while validation_loop:
    validation_loop = False
    label = input("Device label (letter from A-L)\n> ")
    if label.lower() not in ['a','b','c','d','e','f','g','h','i','j','k','l']:
        print("Invalid input")
        validation_loop = True
    else:
        label = label.upper()

if skipVal:
    validation_loop = False  
else:
    validation_loop = True 
while validation_loop:
    validation_loop = False
    baud_input = input(f"Baud rate\nA) 9600\n B) 115200\n> ")
    if baud_input.lower() == 'a':
        BAUD = 9600
    elif baud_input.lower() == 'b':
        BAUD = 115200
    else:
        print("Invalid input")
        validation_loop = True


if device_voltage == 5:
    voltage_threshold = 2.5
    high_threshold = 3.5
    low_threshold = 1.5
elif device_voltage == 3.3:
    voltage_threshold = 3
    high_threshold = 2.7
    low_threshold = 1.5 
else:
    print("Unknown device voltage, using default threshold of 2.5V")
    voltage_threshold = 2.5


# Initialise PicoScope
with ps2000.open_unit() as device:
    print('Device info: {}'.format(device.info))

    res = ps2000.ps2000_set_channel(
        device.handle,
        picoEnum.PICO_CHANNEL['PICO_CHANNEL_A'],
        True,
        picoEnum.PICO_COUPLING['PICO_DC'],
        ps2000.PS2000_VOLTAGE_RANGE['PS2000_5V'],
    )
    assert_pico2000_ok(res)

    sample_interval = 1500
    time_units = 2
    max_samples = 100_000
    auto_stop = False
    samples_per_aggregate = 1
    overview_buffer_size = 50_000

    res = ps2000.ps2000_run_streaming_ns(
        device.handle,
        sample_interval,
        time_units,
        max_samples,
        auto_stop,
        samples_per_aggregate,
        overview_buffer_size
    )
    assert_pico2000_ok(res)

    start_time = time.time_ns()

    while time.time_ns() - start_time < capture_time:
        ps2000.ps2000_get_streaming_last_values(
            device.handle,
            callback
        )

    end_time = time.time_ns()

    ps2000.ps2000_stop(device.handle)

    # Gathering raw data for CSV
    sample_period_s = float(sample_interval) * 1e-9
    time_array_s = np.arange(len(adc_values), dtype=np.float64) * sample_period_s
    time_array_ms = time_array_s * 1e3

    range_index = ps2000.PS2000_VOLTAGE_RANGE['PS2000_5V']
    volts = np.array(adc_to_v(adc_values, range_index), dtype=np.float64)
    samples_per_bit = max(1, int(1.0 / (BAUD * sample_period_s)))

    fig, ax = plt.subplots()

    ax.set_xlabel('time/ms')
    ax.set_ylabel('voltage/V')
    ax.plot(np.linspace(0, (end_time - start_time) * 1e-6, len(volts)), volts)

    plt.show()



# Decoding bytes
print("\nDecoding bytes...")
logic_levels = []
for v in volts:
    if v > voltage_threshold:
        logic_levels.append(1)
    else:
        logic_levels.append(0)

sample_period = (end_time - start_time) * 1e-9 / len(volts)  

# Calculate samples per bit
samples_per_bit = int(1 / (BAUD * sample_period))

# Find start bits (falling edge: 1 -> 0)
bits_per_byte = 10  # 1 start, 8 data, 1 stop
frame_length = bits_per_byte * samples_per_bit

# Filter
volts_filtered = signal.medfilt(volts, kernel_size=5)

# Hysteresis thresholding
logic_levels = []
state = 1 if volts_filtered[0] > high_threshold else 0
for v in volts_filtered:
    if state == 0 and v > high_threshold:
        state = 1
    elif state == 1 and v < low_threshold:
        state = 0
    logic_levels.append(state)

# Start bit detection
min_idle_samples = int(0.7 * samples_per_bit)
decoded_bytes = []
i = min_idle_samples
byte_timings = []
while i < len(logic_levels):
    if (
        all(logic_levels[i - min_idle_samples : i])
        and logic_levels[i - 1] == 1
        and logic_levels[i] == 0
    ):
        bits = []
        for bit in range(1, bits_per_byte):
            sample_idx = int(i + (bit - 0.5) * samples_per_bit)
            if sample_idx < len(logic_levels):
                bits.append(logic_levels[sample_idx])
        if len(bits) >= 9:
            data_bits = bits[1:9]
            byte = 0
            for j, b in enumerate(data_bits):
                byte |= (b << j)
            decoded_bytes.append(byte)
            byte_timings.append(i * sample_period) # Time the byte was received
        i += frame_length
    else:
        i += 1

print("Decoded bytes:", decoded_bytes)

for byte in decoded_bytes:
    if 32 <= byte <= 126:
        print(chr(byte), end='')
    else:
        print('.', end='')



## Data Collection
# determine idle level using the first 5% of samples
idle_slice = max(1, int(0.05 * len(volts)))
idle_mean = np.mean(volts[:idle_slice])
idle_level = 1 if idle_mean > voltage_threshold else 0
active_level = 1 - idle_level  

logic = np.asarray(logic_levels, dtype=int)

# find indexes where signal is active (not idle)
active_idxs = np.where(logic == active_level)[0]

keep = np.zeros(len(volts), dtype=bool)
if active_idxs.size > 0:
    # build contiguous runs of active samples
    breaks = np.where(np.diff(active_idxs) > 1)[0]
    runs = []
    start = active_idxs[0]
    for b in breaks:
        end = active_idxs[b]
        runs.append((start, end))
        start = active_idxs[b + 1]
    runs.append((start, active_idxs[-1]))

    # margin: include some bits before/after each run (in samples)
    pre_margin = int(1.5 * samples_per_bit)
    post_margin = int(1.5 * samples_per_bit)

    for s, e in runs:
        a = max(0, s - pre_margin)
        b = min(len(volts), e + post_margin + 1)
        keep[a:b] = True

# Logic for keeping one contiguous block instead of all of them

else:
    # no active region found -> keep whole capture
    keep[:] = True

# extract kept samples and rebase time to start at 0 (ms)
kept_times = np.asarray(time_array_ms)[keep]
kept_volts = np.asarray(volts)[keep]

if kept_times.size == 0:
    kept_times = np.asarray(time_array_ms)
    kept_volts = np.asarray(volts)
else:
    kept_times = kept_times - kept_times[0]



# Save to CSV
dir = f"./Devices/{platform}/{model}/{BAUD}/{label}/"
CSV_num = 0

with open('./metadata.json', 'r+') as f:
    data = json.load(f)
    CSV_num = data[platform][model][str(BAUD)][label][f'Captures_{data_size}'] + 1
    data[platform][model][str(BAUD)][label][f'Captures_{data_size}'] = CSV_num
    f.seek(0)
    json.dump(data, f, indent=4)
    f.truncate()

with open(dir + f'voltages_{data_size}_{CSV_num}.csv', "w", newline='') as f:
    writer = csv.writer(f)
    writer.writerow(["Time (ms)", "Voltage (V)"])
    for t, v in zip(kept_times, kept_volts):
        writer.writerow([t, v])

print(f"\nData saved to {dir}voltages_{data_size}_{CSV_num}.csv")

with open(last_device, 'w') as f:
    lastDev = f"{platform}:{model}:{device_voltage}:{data_size}:{str(BAUD)}:{label}"
    f.write(lastDev)