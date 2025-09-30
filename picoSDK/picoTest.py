from ctypes import byref, c_int16, c_int32, c_byte
from time import sleep

from picosdk.ps2000 import ps2000
from picosdk.functions import assert_pico2000_ok, adc2mV
from picosdk.PicoDeviceEnums import picoEnum

import numpy as np
import matplotlib.pyplot as plt

# Constants
SAMPLES = 2000
OVERSAMPLING = 1
UART_BAUD = 9600
V_THRESHOLD = 2.5 



# Timebase 

def get_timebase(device, wanted_time_interval):
    current_timebase = 1
    old_time_interval = None
    time_interval = c_int32(0)
    time_units = c_int16()
    max_samples = c_int32()

    while ps2000.ps2000_get_timebase(
        device.handle,
        current_timebase,
        SAMPLES,
        byref(time_interval),
        byref(time_units),
        OVERSAMPLING,
        byref(max_samples)
    ) == 0 or time_interval.value < wanted_time_interval:

        current_timebase += 1
        old_time_interval = time_interval.value

        if current_timebase.bit_length() > 16:
            raise Exception('No appropriate timebase found')

    return current_timebase - 1, old_time_interval

# Open device
with ps2000.open_unit() as device:
    print("Device info:", device.info)

    # Channel A setup (5V logic)
    res = ps2000.ps2000_set_channel(
        device.handle,
        picoEnum.PICO_CHANNEL['PICO_CHANNEL_A'],
        True,
        picoEnum.PICO_COUPLING['PICO_DC'],
        ps2000.PS2000_VOLTAGE_RANGE['PS2000_5V']
    )
    assert_pico2000_ok(res)



    #  Trigger
    # ps2000_set_trigger(handle, source, threshold, direction, delay, autoTrigger_ms)
    res = ps2000.ps2000_set_trigger(
        device.handle,
        0,      # channel A
        2500,   # threshold in mV (≈ 2.5 V)
        0,      # 0 = falling edge
        1,      # delay in samples
        0       # auto-trigger disabled
    )
    assert_pico2000_ok(res)

    # Choose timebase: ~10 samples per UART bit (~10 µs/sample)
    timebase, interval = get_timebase(device, 5_000)  # 10 µs = 10,000 ns
    print(f"Timebase {timebase}, sample interval ~{interval} ns")

    collection_time = c_int32()
    res = ps2000.ps2000_run_block(
        device.handle,
        SAMPLES,
        timebase,
        OVERSAMPLING,
        byref(collection_time)
    )
    assert_pico2000_ok(res)

    while ps2000.ps2000_ready(device.handle) == 0:
        sleep(0.01)

    times = (c_int32 * SAMPLES)()
    buffer_a = (c_int16 * SAMPLES)()
    overflow = c_byte(0)

    res = ps2000.ps2000_get_times_and_values(
        device.handle,
        byref(times),
        byref(buffer_a),
        None,
        None,
        None,
        byref(overflow),
        2,
        SAMPLES
    )
    assert_pico2000_ok(res)

    ps2000.ps2000_stop(device.handle)

    # Convert to volts
    channel_a_mv = adc2mV(buffer_a, ps2000.PS2000_VOLTAGE_RANGE['PS2000_5V'], c_int16(32767))
    channel_a_v = np.array(channel_a_mv) / 1000.0


# Plot 
plt.figure()
plt.plot(np.array(times) * 1e-6, channel_a_v)
plt.xlabel("Time (ms)")
plt.ylabel("Voltage (V)")
plt.title("UART TX Capture")
plt.grid(True)
plt.show()


# UART decoding
sample_interval_s = interval * 1e-9  # convert ns → s
samples_per_bit = int(1 / UART_BAUD / sample_interval_s)
logic = (channel_a_v > V_THRESHOLD).astype(int)

decoded_bytes = []
i = 0
while i < len(logic) - samples_per_bit * 10:
    # Look for start bit (high -> low)
    if logic[i] == 1 and logic[i + 1] == 0:
        # Sample each bit in the middle of the bit interval
        byte = 0
        for bit in range(8):
            sample_idx = i + int((1.5 + bit) * samples_per_bit)
            if sample_idx < len(logic):
                byte |= logic[sample_idx] << bit
        decoded_bytes.append(byte)
        # Skip to next potential start bit
        i += samples_per_bit * 10
    else:
        i += 1

print("Decoded bytes:", decoded_bytes)
print("Decoded ASCII:", ''.join([chr(b) for b in decoded_bytes if 32 <= b <= 126]))
