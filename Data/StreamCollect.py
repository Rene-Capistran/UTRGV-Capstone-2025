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
import os

loop_count = 0
cap_count = ''
protocol = ''
multi_cap = input("Auto capture?\nA) no\nB) 15\nC) 50\nD) Custom\n> ")
if multi_cap.lower() == 'a':
    cap_count = 0
elif multi_cap.lower() == 'b':
    cap_count = 15
elif multi_cap.lower() == 'c':
    cap_count = 50
elif multi_cap.lower() == 'd':
    cap_count = int(input("Custom amount\n> "))

while True:
    loop_count += 1

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

    adc_values_a = []  # Channel A (SDA for I2C, TX/RX for UART)
    adc_values_b = []  # Channel B (SCL for I2C)

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

    last_run = "Data\\last.txt"
    last_dev_data = ''
    with open(last_run, 'r') as f:
        data = f.readline()
        last_dev_data = data.split(':')

        # Handle old format (without protocol) and new format (with protocol)
        if len(last_dev_data) >= 7:
            if len(last_dev_data) > 6:
                protocol_display = last_dev_data[6]
            else:
                protocol_display = 'UART'
            print(f"Last run\n {last_dev_data[0]} {last_dev_data[1]} ({last_dev_data[5]}), {protocol_display}, {last_dev_data[3]}:{last_dev_data[4]} {last_dev_data[2]}V\n")
        else:
            print(f"Last run\n {last_dev_data[0]} {last_dev_data[1]} ({last_dev_data[5]}),  {last_dev_data[3]}:{last_dev_data[4]} {last_dev_data[2]}V\n")

    skip_val = False

    # Auto capture handling
    if multi_cap and loop_count > 1 and loop_count <= cap_count:
        skip_val = True
        validation_loop = False

        # Using last device data
        platform = last_dev_data[0]
        model = last_dev_data[1]
        device_voltage = float(last_dev_data[2])
        data_size = last_dev_data[3]
        BAUD = int(last_dev_data[4])
        label = last_dev_data[5]
        protocol = last_dev_data[6] if len(last_dev_data) > 6 else 'UART'
    
    # Device platform selection
    while validation_loop:
        platform = input("Device platform type\nA) Arduino\nB) Raspberry Pi\nC) ESP\nZ) Last device\n0) Not listed\n> ")
        platform = platform.lower()
        if platform in ['a', 'b', 'c', 'z', '0']:
            validation_loop = False
            if platform == 'z':
                skip_val = True
                platform = last_dev_data[0]
                model = last_dev_data[1]
                device_voltage = float(last_dev_data[2])
                data_size = last_dev_data[3]
                BAUD = int(last_dev_data[4])
                label = last_dev_data[5]
                protocol = last_dev_data[6] if len(last_dev_data) > 6 else 'UART'

        else:
            print("Invalid input")
            validation_loop = True

    if skip_val:
        validation_loop = False
    else:
        validation_loop = True 

    # Device model selection
    while validation_loop:
        validation_loop = False
        if platform == 'a':
            platform = 'Arduino'
            model = input("Device model\nA) Nano\nB) Mega\n0) Not listed\n> ")
            if model.lower() not in ['a', 'b', '0']:
                print("Invalid input")
                validation_loop = True
            elif model.lower() == 'a':
                model = 'Nano'
                device_voltage = 5
            elif model.lower() == 'b':
                model = 'Mega'
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


    if skip_val:
        validation_loop = False 
        if data_size == 'Small':
            capture_time = 250_000_000  
        if data_size == 'Medium':
            capture_time = 500_000_000  
        if data_size == 'Large':
            capture_time = 1_000_000_000  
    else:
        validation_loop = True 
    # Data size selection
    while validation_loop:
        validation_loop = False
        data_size = input("Data size\nA) Small\nB) Medium\nc) Large\n> ")
        if data_size.lower() == 'a':
            data_size = 'Small'
            capture_time = 200_000_000       
        elif data_size.lower() == 'b':
            data_size = 'Medium'
            capture_time = 400_000_000
        elif data_size.lower() == 'c':
            data_size = 'Large'
            capture_time = 700_000_000
        else:
            print("Invalid input")
            validation_loop = True

    if skip_val:
        validation_loop = False   
    else:
        validation_loop = True 
    
    # Device label selection
    while validation_loop:
        validation_loop = False
        label = input("Device label (letter from A-L)\n> ")
        if label.lower() not in ['a','b','c','d','e','f','g','h','i','j','k','l']:
            print("Invalid input")
            validation_loop = True
        else:
            label = label.upper()

    if skip_val:
        validation_loop = False  
    else:
        validation_loop = True 
    # Protocol selection
    while validation_loop:
        validation_loop = False
        protocol_input = input(f"Communication Protocol\nA) UART\nB) I2C\n> ")
        if protocol_input.lower() == 'a':
            protocol = 'UART'
        elif protocol_input.lower() == 'b':
            protocol = 'I2C'
        else:
            print("Invalid input")
            validation_loop = True

    if skip_val:
        validation_loop = False  
    else:
        validation_loop = True 
    
    # Baud rate selection for UART
    if protocol == 'UART':
        while validation_loop:
            validation_loop = False
            baud_input = input(f"Baud rate\nA) 9600\nB) 115200\n> ")
            if baud_input.lower() == 'a':
                BAUD = 9600
            elif baud_input.lower() == 'b':
                BAUD = 115200
            else:
                print("Invalid input")
                validation_loop = True
    # If I2C, set baud to 100k
    else:
        BAUD = 100000  
    
    # Set voltage thresholds based on device voltage
    if device_voltage == 5:
        voltage_threshold = 2.5
        high_threshold = 3.5
        low_threshold = 1.5
    elif device_voltage == 3.3:
        voltage_threshold = 1.65
        high_threshold = 2.3
        low_threshold = 0.8
    else:
        print("Unknown device voltage")

    # Callback function to collect overview buffers
    def get_overview_buffers(buffers, _overflow, _triggered_at, _triggered, _auto_stop, n_values):
        adc_values_a.extend(buffers[0][0:n_values])
        if protocol == 'I2C':
            adc_values_b.extend(buffers[1][0:n_values])
    callback = CALLBACK(get_overview_buffers)

    # Initialise PicoScope
    with ps2000.open_unit() as device:
        print('Device info: {}'.format(device.info))
        # Channel A
        res = ps2000.ps2000_set_channel(
            device.handle,
            picoEnum.PICO_CHANNEL['PICO_CHANNEL_A'],
            True,
            picoEnum.PICO_COUPLING['PICO_DC'],
            ps2000.PS2000_VOLTAGE_RANGE['PS2000_5V'],
        )
        assert_pico2000_ok(res)


        # Channel B
        if protocol == 'I2C':
            res = ps2000.ps2000_set_channel(
                device.handle,
                picoEnum.PICO_CHANNEL['PICO_CHANNEL_B'],
                True,
                picoEnum.PICO_COUPLING['PICO_DC'],
                ps2000.PS2000_VOLTAGE_RANGE['PS2000_5V'],
            )
            assert_pico2000_ok(res)
        else:
            # Disable channel B for UART
            res = ps2000.ps2000_set_channel(
                device.handle,
                picoEnum.PICO_CHANNEL['PICO_CHANNEL_B'],
                False,
                picoEnum.PICO_COUPLING['PICO_DC'],
                ps2000.PS2000_VOLTAGE_RANGE['PS2000_5V'],
            )
            assert_pico2000_ok(res)

        # Set sampling parameters
        if protocol == 'UART':
            sample_interval = 1500
            time_units = 2
            max_samples = 100_000
        elif protocol == 'I2C':
            sample_interval = 300
            time_units = 2
            max_samples = 250_000
        auto_stop = False
        samples_per_aggregate = 1
        overview_buffer_size = 100_000

        # Start streaming mode
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

        # Collect data for the specified capture time
        start_time = time.time_ns()
        while time.time_ns() - start_time < capture_time:
            ps2000.ps2000_get_streaming_last_values(
                device.handle,
                callback
            )

        end_time = time.time_ns()

        ps2000.ps2000_stop(device.handle)

        # Gathering data
        sample_period_s = float(sample_interval) * 1e-9
        time_array_s = np.arange(len(adc_values_a), dtype=np.float64) * sample_period_s
        time_array_ms = time_array_s * 1e3

        # create voltage array for channel A
        range_index = ps2000.PS2000_VOLTAGE_RANGE['PS2000_5V']
        volts_a = np.array(adc_to_v(adc_values_a, range_index), dtype=np.float64)
        
        # create voltage array for channel B if I2C
        if protocol == 'I2C':
            volts_b = np.array(adc_to_v(adc_values_b, range_index), dtype=np.float64)
        
        samples_per_bit = max(1, int(1.0 / (BAUD * sample_period_s)))

        # Plotting
        if loop_count <= 1: # Only plot on first iteration of loop
            if protocol == 'UART':
                fig, ax = plt.subplots()

                ax.set_xlabel('time/ms')
                ax.set_ylabel('voltage/V')
                ax.plot(np.linspace(0, (end_time - start_time) * 1e-6, len(volts_a)), volts_a)
                ax.set_title(f'{platform} {model} ({label}), {protocol}, {data_size}:{BAUD}')

                plt.show()

                # Save template figure if it doesn't exist
                dir = f"Data/Devices/{protocol}/{platform}/{model}/{BAUD}/{label}/"
                if not os.path.isfile(dir + f'template_{data_size}.png'):
                    print('saving template figure')
                    fig.savefig(dir + f'template_{data_size}.png')
            elif protocol == 'I2C':
                fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)

                # Plot SDA on top subplot
                ax1.set_ylabel('SDA Voltage (V)')
                ax1.plot(np.linspace(0, (end_time - start_time) * 1e-6, len(volts_a)), volts_a, label='SDA (Channel A)', color = 'g')
                ax1.axhline(y=voltage_threshold, color='r', linestyle='--', alpha=0.7, label=f'Threshold ({voltage_threshold}V)')
                ax1.grid(True, alpha=0.3)
                ax1.legend()
                ax1.set_title(f'{platform} {model} ({label}), {protocol}, {data_size} - SDA Signal')
                
                # Plot SCL on bottom subplot  
                ax2.set_xlabel('Time (ms)')
                ax2.set_ylabel('SCL Voltage (V)')
                ax2.plot(np.linspace(0, (end_time - start_time) * 1e-6, len(volts_b)), volts_b, label='SCL (Channel B)', color='#FFA500')
                ax2.axhline(y=voltage_threshold, color='r', linestyle='--', alpha=0.7, label=f'Threshold ({voltage_threshold}V)')
                ax2.grid(True, alpha=0.3)
                ax2.legend()
                ax2.set_title('SCL Signal')
                
                plt.tight_layout()
                plt.show()

                # Save template figure if it doesn't exist
                dir = f"Data/Devices/{protocol}/{platform}/{model}/{BAUD}/{label}/"
                if not os.path.isfile(dir + f'template_{data_size}.png'):
                    print('saving template figure')
                    fig.savefig(dir + f'template_{data_size}.png')


    # Decoding UART bytes to verify capture validity
    print("\nDecoding bytes...")
    if protocol == 'UART':
        logic_levels = []
        for v in volts_a:
            if v > voltage_threshold:
                logic_levels.append(1)
            else:
                logic_levels.append(0)

        sample_period = (end_time - start_time) * 1e-9 / len(volts_a)  

        # Calculate samples per bit
        samples_per_bit = int(1 / (BAUD * sample_period))

        # Find start bits
        bits_per_byte = 10  # 1 start, 8 data, 1 stop
        frame_length = bits_per_byte * samples_per_bit

        # Filter
        volts_filtered = signal.medfilt(volts_a, kernel_size=5)

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
        volts = volts_a
    elif protocol == 'I2C':
        logic_levels = []
        for v in volts_a:
            if v > voltage_threshold:
                logic_levels.append(1)
            else:
                logic_levels.append(0)
                ## TODO: I2C decoding
        volts = volts_a

        

    ## Data Collection
    # determine idle level using the first 5% of samples
    idle_slice = max(1, int(0.05 * len(volts)))
    idle_mean = np.mean(volts[:idle_slice])
    idle_level = 1 if idle_mean > voltage_threshold else 0
    active_level = 1 - idle_level  

    logic = np.asarray(logic_levels, dtype=int)

    # find indexes where signal is active
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


    ## Save to CSV
    dir = f"Data/Devices/{protocol}/{platform}/{model}/{BAUD}/{label}/"
    CSV_num = 0

    # Update metadata.json
    with open('Data/metadata.json', 'r+') as f:
        data = json.load(f)
        CSV_num = data[protocol][platform][model][str(BAUD)][label][f'Captures_{data_size}'] + 1
        data[protocol][platform][model][str(BAUD)][label][f'Captures_{data_size}'] = CSV_num
        f.seek(0)
        json.dump(data, f, indent=4)
        f.truncate()

    # write CSV
    with open(dir + f'voltages_{data_size}_{CSV_num}.csv', "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Time (ms)", "Voltage (V)"])
        for t, v in zip(kept_times, kept_volts):
            writer.writerow([t, v])

    
    print(f"\nData saved to {dir}voltages_{data_size}_{CSV_num}.csv")

    # Save last run data 
    with open(last_run, 'w') as f:
        lastDev = f"{platform}:{model}:{device_voltage}:{data_size}:{str(BAUD)}:{label}:{protocol}"
        f.write(lastDev)
