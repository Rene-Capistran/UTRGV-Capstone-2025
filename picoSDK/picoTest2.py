from picosdk.ps2000 import ps2000
from matplotlib import pyplot as plt
from ctypes import c_int16, c_int32, byref
from time import sleep

# Initialise PicoScope
handle = ps2000.ps2000_open_unit()   # returns a scope handle (int)
if handle <= 0:
    raise RuntimeError("Failed to open scope")

# Channel
# handle, channel (0: A, 1: B), enabled/disabled, DC, range (1 to 10, 8 = 5v)
channel = 0
enabled = True
Dc = True
range = 8
ps2000.ps2000_set_channel(handle, channel, enabled, Dc, range)

# trigger
# handle, source(channel), threshold, direction (falling = 1), delay, delayed_trigger (guarantee trigger after delay)
threshold = int(1.5 * 32767 / 5) # 1.5V threshold
direction = 1
delay = 10
delayed_trigger = 0 # 0 = indefinite
ps2000.ps2000_set_trigger(handle, channel, threshold, direction, delay, delayed_trigger)

# timebase
# handle, timebase, sample_number, *time_interval, *time_units, oversample, *max_samples
timebase        = c_int16(10) # should be around 10ms (10kns)
samples_num     = c_int32(2500) # max is 3968
time_interval   = c_int32(0)
time_units      = c_int16(0)
oversample      = c_int16(1)
max_samples     = c_int32(0)
time_satus = ps2000.ps2000_get_timebase(handle, timebase, samples_num, byref(time_interval), byref(time_units), oversample, byref(max_samples))

print(time_interval.value, " ", time_units.value, " ", max_samples.value)

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

# Plot
voltage = 5
channel_a_volts = [x * voltage / 32767 for x in buffer_a]

ps2000.ps2000_close_unit(handle)

time_list = list(times)
channel_a_list = list(channel_a_volts)

plt.plot(time_list, channel_a_list)
# Add labels to pyplot
plt.xlabel("Time (ns)")     
plt.ylabel("Amplitude (V)")
plt.grid(True)
plt.show()

current_point = 0
repeats = 0
point_arr = []
for point in channel_a_volts:
    print(point)
    if point > 1:
        point = 5
    else:
        point = 0

    if point == current_point or repeats <= 3:
        repeats += 1
    else:
        point_arr.append(point)

print(point_arr)