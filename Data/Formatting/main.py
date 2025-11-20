# -*- coding: utf-8 -*-
"""
Created on Mon May 22 12:08:57 2023

@author: Jorge Castillo
"""

import pandas as pd
pd.options.display.float_format = '{:,.10f}'.format
from framework import USARTConfig, BoardExperiment
from pathlib import Path
import tempfile

baseDir = Path(__file__).parent.parent
devDir = baseDir / "Devices"
outputDir = baseDir / "Processed"
outputDir.mkdir(exist_ok=True)

baud_rates = [9600, 115200]
sizes = ['small', 'medium', 'large']
boards = []
models_3v = ['32', '5b']
models_5v = ['uno', 'nano']

skip = ['uno', '32']


for BAUD in baud_rates:
    print(f"\n=== Processing BAUD rate: {BAUD} ===")
    
    
    
    for device in devDir.iterdir():
        if not device.is_dir():
            continue
        platform = device.name
        
        for model_dir in device.iterdir():
            if not model_dir.is_dir():
                continue
            model = model_dir.name
            if model.lower() in skip:   #skip chosen directories
                print(f'\n=== Skipping {model} ===')
                continue
            board = f"{platform}_{model}"

            #Voltage by model
            if model.lower in models_5v:
                volts = 5.0
            else:
                volts = 3.3
            config = USARTConfig(8, 0, 1, baud_rate=BAUD, vih=volts)

            if board not in boards:
                boards.append(board)
                print(f"\nProcessing Board: {board}")

            baud_dir = model_dir / str(BAUD)           
          
            datasets = [] 
            for size in sizes:
                if size == 'small':
                    char_len = 13
                elif size == 'medium':
                    char_len = 44
                elif size == 'large':
                    char_len = 174         
                for label_dir in baud_dir.iterdir():
                    if not label_dir.is_dir():
                        continue
                    label = label_dir.name
                    
                    for f in label_dir.iterdir():
                        if (f.is_file() and 
                            f.suffix.lower() == '.csv' and 
                            size.lower() in f.name.lower() and 
                            f.stat().st_size > 100):
                            
                            print(f"Processing: {f}")
                            try:
                                # Convert UTF-8-sig to utf-8
                                df = pd.read_csv(f, encoding='utf-8-sig')
                                
                                with tempfile.TemporaryDirectory() as temp_dir:
                                    temp_file = Path(temp_dir) / f.name
                                    df.to_csv(temp_file, index=False, encoding='utf-8')
                                    
                                    # Process data
                                    exp = BoardExperiment(str(temp_dir), label=label, usart_config=config, msg_size=size, char_len=char_len)
                                    dataset = exp.create_dataset()
                                    datasets.append(dataset)
                                    
                            except Exception as e:
                                print(f"Error processing {f}: {e}")
                                continue

            # Create dataset
            if datasets:
                df = pd.concat(datasets, axis=0).sample(frac=1).reset_index(drop=True)
                output_file = outputDir / f"{board}_{BAUD}_dataset.csv"
                df.to_csv(output_file, float_format='%.10f', index=False)
                print(f"Saved dataset to {output_file} with {len(df)} samples")

print(f"Found boards: {set(boards)}")