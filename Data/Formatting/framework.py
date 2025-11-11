# -*- coding: utf-8 -*-
"""
Created on Mon May 22 12:06:57 2023

@author: Jorge Castillo
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from utils import Metrics

class USARTConfig:
    def __init__(self, data_bits:int, parity_type:int=0, stop_bits:int=1, baud_rate:int=9600, vih:float=5.0):
        # Parity Type: 0 = None; 1 = Even; -1 = Odd
        parity = {0: 'None', 1: 'Even', -1: 'Odd'}
        self.parity_bit = parity[parity_type]
        self.data_bits = data_bits
        self.stop_bits = stop_bits
        self.start_bits = 1
        self.baud_rate = baud_rate
        self.device_voltage = vih
        self.calculate_frame_length()
        self.calculate_transmission_rate()
        self.calculate_bit_time()
        
    def calculate_frame_length(self):
        tmp = 0
        if self.parity_bit != 0:
            tmp = 1
        self.frame_length = self.start_bits + self.data_bits + tmp + self.stop_bits

    def calculate_transmission_rate(self):
        self.tx_rate = self.baud_rate / self.frame_length
        
    def calculate_bit_time(self):
        # Result is in milliseconds
        self.bit_time = 1000 / self.baud_rate
        
    def __str__(self):
        txt = "*************************\n** USART Configuration **\n*************************\n"
        txt += "   Device Voltage: \t{}\n   Parity: \t{}\n   Data Bits: \t{}\n   Stop Bits: \t{}\n   Baud Rate: \t{}".format(self.device_voltage,\
                                     self.parity_bit,\
                                     self.data_bits, self.stop_bits,\
                                     self.baud_rate)
        return str(txt)

class BoardExperiment:
    def __init__(self, path, label, msg_size, char_len, usart_config:USARTConfig):
        # TODO - infer usart_config?
        self.label = label
        self.config = usart_config
        self.exp_path = path
        self.msg_size = msg_size
        self.char_len = char_len
        self.ss = [f for f in os.listdir(path)]
#        print("{}\n\n{}".format(self.config, self))
        
    def read_data(self, ss_no=1):
        # TODO - validate inputs
        self.data_path = '{}/{}'.format(self.exp_path, self.ss[ss_no-1])
        raw_frame = pd.read_csv(self.data_path)
        self.process_data(raw_frame)

    def process_data(self, frame):
        frame = frame.tail(-1)
        x = [float(i) for i in frame.iloc[:,0]]
        x = [i-x[0] for i in x]
        y = [float(i) for i in frame.iloc[:,1]]
        self.data = pd.DataFrame(columns=['Time', 'Voltage'])
        self.data.loc[:,'Time'] = x
        self.data.loc[:,'Voltage'] = y
    
    def analyze_waveform(self, ss_no=1, display=False):
        self.read_data(ss_no)
        # TODO - display waveform and statistics
        v_th = self.config.device_voltage * 0.5  # Changed threshold to half of device voltage
        # TODO - fix method for tr and tf
        data = { 'ones':[], 'ones_index':[], 'zeros':[], 'zeros_index':[], 'tr':[], 'tf':[] }
        transition = True
        for i, s in enumerate(self.data['Voltage']):
            if s <= v_th:
                data['zeros'].append(s)
                data['zeros_index'].append(i)
                if transition and i > 0: # Added i>0 because i kept getting an out-of-bounds error
                    # tr are in microseconds
                    data['tr'].append((self.data['Time'][i] - self.data['Time'][i-1])*1000)
                    transition = False
            else:
                data['ones'].append(s)
                data['ones_index'].append(i)
                if not transition and i > 0:
                    # tf are in microseconds
                    data['tf'].append((self.data['Time'][i] - self.data['Time'][i-1])*1000)
                    transition = True
        self.tmp = data
        metrics = ['mse','mean','std','var','skew','kurt','rms','en','max','min']
        # Note that we also calculate every metric for half case
        metrics_zeros = Metrics(np.array([0 for i in self.tmp['zeros']]), self.tmp['zeros']).evaluate(metrics=metrics)
        metrics_ones = Metrics(np.array([self.config.device_voltage for i in self.tmp['ones']]), self.tmp['ones']).evaluate(metrics=metrics)
        metrics_half_zeros = Metrics(np.array([self.config.device_voltage/2 for i in self.tmp['zeros']]), 
                                     self.tmp['zeros']).evaluate(metrics=['cos'])
        metrics_half_ones = Metrics(np.array([self.config.device_voltage/2 for i in self.tmp['ones']]), 
                                     self.tmp['ones']).evaluate(metrics=['cos'])
        
        sample = {}      
        sample['mean_one'] = metrics_ones['mean']
#        sample['mean_zero'] = metrics_zeros['mean']
        
        sample['std_one'] = metrics_ones['std']
        sample['std_zero'] = metrics_zeros['std']
        
        sample['var_one'] = metrics_ones['var']
        sample['var_zero'] = metrics_zeros['var']
        
        sample['skew_one'] = metrics_ones['skew']
        sample['skew_zero'] = metrics_zeros['skew']
        
        sample['kurt_one'] = metrics_ones['kurt']
        sample['kurt_zero'] = metrics_zeros['kurt']
        
        sample['rms_one'] = metrics_ones['rms']
        sample['rms_zero'] = metrics_zeros['rms']
        
        sample['en_one'] = metrics_ones['en']
        sample['en_zero'] = metrics_zeros['en']
        
        sample['max_one'] = metrics_ones['max']
        sample['max_zero'] = metrics_zeros['max']
        
        sample['min_one'] = metrics_ones['min']
        sample['min_zero'] = metrics_zeros['min']
        
        sample['mse_one'] = metrics_ones['mse']
#        sample['mse_zero'] = metrics_zeros['mse']   
        
        # Cosine similarity w.r.t. 2.5V (half os signal)
        sample['cos_one'] = metrics_half_ones['cos']
        sample['cos_zero'] = metrics_half_zeros['cos']

        sample['msg_size'] = self.msg_size
        sample['char_len'] = self.char_len

        # TODO - fix tr/tf measurment 
#        sample['ave_tr'] = np.mean(self.tmp['tr'])
#        sample['ave_tf'] = np.mean(self.tmp['tf'])
        
        if display:
            self.print_waveform()
        return sample
        
    def create_dataset(self):
        data = []
        for i in range(1, len(self.ss)+1):
            sample = self.analyze_waveform(ss_no=i)
            sample['label'] = self.label
            data.append(sample)
        return pd.DataFrame(data)

    def print_waveform(self):
        fig, ax = plt.subplots(1, figsize=(12,6))
        # TODO - Beautify
        ax.plot(self.data.iloc[self.tmp['zeros_index'],:]['Time'], self.tmp['zeros'], marker='.', 
                markersize=9, linestyle='None', color='cornflowerblue')
        ax.plot(self.data.iloc[self.tmp['ones_index'],:]['Time'], self.tmp['ones'], marker='.', 
                markersize=9, linestyle='None', color='salmon')
        ax.plot(self.data['Time'], self.data['Voltage'], color='k', linewidth=1)
        ax.set_xlabel("Time (ms)")
        ax.set_ylabel("Voltage (V)")
        
    def __str__(self):
        txt = "****************************\n** Experiment Setup **\n****************************\n"
        txt += "   Experiment Path: \t{}\n   No Scope Shots: \t{}".format(self.exp_path, len(self.ss))
        return str(txt)