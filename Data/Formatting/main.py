# -*- coding: utf-8 -*-
"""
Created on Mon May 22 12:08:57 2023

@author: Jorge Castillo
"""

import pandas as pd
pd.options.display.float_format = '{:,.10f}'.format
from framework import USARTConfig, BoardExperiment
from pathlib import Path


baseDir = Path(__file__).parent.parent
devDir = baseDir / "Devices"
outputDir = baseDir / "Processed"

BAUD = 9600

config = USARTConfig(8, 0, 1, baud_rate=BAUD)

labels = 'A,B,C,D,E,F,G,H,I,J,K,L'.split(',')
sizes = ['small', 'medium', 'large']
boards = []

capture_files = []


for device in devDir.iterdir():
    if not device.is_dir():
        continue
    platform = device.name
    for model_dir in device.iterdir():
        if not model_dir.is_dir():
            continue
        model = model_dir.name

        board = f"{platform}_{model}"
        boards.append(board)
        for label_dir in (model_dir / f"{BAUD}").iterdir():
            if not label_dir.is_dir():
                continue
            label = label_dir.name
            
            for size in sizes:
                
                for f in label_dir.iterdir():
                    if f.is_file() and size.lower() in f.name.lower():
                        datasets = []
                        if size in f.name.lower():
                            exp = BoardExperiment(str(f.parent), label=label, usart_config=config)
                            dataset = exp.create_dataset()
                            datasets.append(dataset)
                        if datasets:
                            df = pd.concat(datasets, axis=0).sample(frac=1).reset_index(drop=True)
                            df.to_csv(outputDir / f"{board}_{label}_{size}_dataset.csv", float_format='%.10f', index=False)
                            print(f"Saved dataset to {outputDir / f'{board}_{label}_{size}_dataset.csv'}")

print(f"Found boards: {boards}")





# for b in 'A,B,C,D,E,F,G,H,I,J,K,L'.split(','):
#     board = 'arduino_{}_U'.format(b)
#     exp = BoardExperiment('{}/{}'.format(folder, board), label=b, usart_config=config)
#     dataset = exp.create_dataset()
#     datasets.append(dataset)

# df = pd.concat(datasets, axis=0).sample(frac=1).reset_index(drop=True)
# df.to_csv('{}\{}'.format(outputDir, 'boards_dataset.csv'), float_format='%.10f', index=False)
# #print(df)