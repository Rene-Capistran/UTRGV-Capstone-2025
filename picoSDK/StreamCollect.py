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

# convert ADC to mV
def adc_to_mv(values, range_, bitness=16):
    v_ranges = [10, 20, 50, 100, 200, 500, 1_000, 2_000, 5_000, 10_000, 20_000]

    return [(x * v_ranges[range_]) / (2**(bitness - 1) - 1) for x in values]


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
        if model.lower() == 'a':
            model = '5B' 
    elif platform.lower() == 'c':
        platform = 'ESP'
        model = input("A) 32\n0) Not listed\n> ")
        if model.lower() == 'a':
            model = '32' 
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
        capture_time = 100_000_000       
    elif data_size.lower() == 'b':
        data_size = 'Medium'
        capture_time = 300_000_000
    elif data_size.lower() == 'c':
        data_size = 'Large'
        capture_time = 1_000_000_000
    else:
        print("Invalid input")
        validation_loop = True

validation_loop = True
while validation_loop:
    validation_loop = False
    decode_out = input("Decode bytes?\nY) Yes\nN) No\n> ")
    if decode_out.lower() == 'y': 
        decode_out = True
    elif decode_out.lower() == 'n':
        decode_out = False
    else:
        print("Invalid input")
        validation_loop = True

voltage_threshold = 5
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

    mv_values = adc_to_mv(adc_values, ps2000.PS2000_VOLTAGE_RANGE['PS2000_5V'])
    # convert mV to V
    volts = np.array(mv_values) / 1000.0  

    fig, ax = plt.subplots()

    ax.set_xlabel('time/ms')
    ax.set_ylabel('voltage/mV')
    ax.plot(np.linspace(0, (end_time - start_time) * 1e-6, len(volts)), volts)

    plt.show()



# Decoding bytes

if decode_out:
    print("\nDecoding bytes...")
    # Convert waveform to logic levels
    logic_levels = [1 if v > voltage_threshold else 0 for v in volts]

    # Calculate sample period (in seconds)
    sample_period = (end_time - start_time) * 1e-9 / len(volts)  # total time / number of samples

    # Calculate samples per bit
    samples_per_bit = int(1 / (BAUD * sample_period))

    # Find start bits (falling edge: 1 -> 0)
    bits_per_byte = 10  # 1 start, 8 data, 1 stop
    frame_length = bits_per_byte * samples_per_bit

    # Filter
    volts_filtered = signal.medfilt(volts, kernel_size=5)

    # Hysteresis threshold
    high_threshold = 3
    low_threshold = 2
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


# Create time array in seconds or ms
time_array_ns = np.linspace(0, (end_time - start_time), len(volts))  


# Data Collection

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
    for t, v in zip(time_array_ns, volts):
        writer.writerow([t, v])

print(f"\nData saved to {dir}voltages_{data_size}_{CSV_num}.csv")