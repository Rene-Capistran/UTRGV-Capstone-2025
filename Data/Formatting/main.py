# -*- coding: utf-8 -*-
"""
Created on Mon May 22 12:08:57 2023

@author: Jorge Castillo
"""
import pandas as pd
pd.options.display.float_format = '{:,.10f}'.format
from framework import USARTConfig, BoardExperiment

baseDir = "./data/"
outputDir = f"{baseDir}processed/"



config = USARTConfig(8, 0, 1, baud_rate=9600)

#expA = BoardExperiment('{}/{}'.format(folder, 'arduino_A_U'), label='A', usart_config=config)
#expA.analyze_waveform(ss_no=1, display=True)
#datasetA = expA.create_dataset()
#expB = BoardExperiment('{}/{}'.format(folder, 'arduino_B_U'), label='B', usart_config=config)
#expB.analyze_waveform(ss_no=1, display=True)
#datasetB = expB.create_dataset()
#
#datasets = [datasetA, datasetB]

datasets = []
for b in 'A,B,C,D,E,F,G,H,I,J,K,L'.split(','):
    board = 'arduino_{}_U'.format(b)
    exp = BoardExperiment('{}/{}'.format(folder, board), label=b, usart_config=config)
    dataset = exp.create_dataset()
    datasets.append(dataset)

df = pd.concat(datasets, axis=0).sample(frac=1).reset_index(drop=True)
df.to_csv('{}\{}'.format(outputDir, 'boards_dataset.csv'), float_format='%.10f', index=False)
#print(df)