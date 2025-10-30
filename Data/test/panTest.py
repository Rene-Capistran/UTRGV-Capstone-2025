import pandas as pd
import os

PATH = './'

def read_data(ss_no=1):
    data_path = os.path.join(PATH, 'voltages_Small_1.csv')
    raw_frame = pd.read_csv(data_path)
    return process_data(raw_frame)  # Return the processed data

def process_data(frame):
    frame = frame.tail(-1)
    x = [float(i) for i in frame.iloc[:,0]]
    x = [i-x[0] for i in x]
    y = [float(i) for i in frame.iloc[:,1]]
    data = pd.DataFrame(columns=['Time', 'Voltage'])
    data.loc[:,'Time'] = x
    data.loc[:,'Voltage'] = y
    return data

df = pd.concat([read_data()], axis=0).sample(frac=1).reset_index(drop=True)
df.to_csv(os.path.join(PATH, 'boards_dataset2.csv'), float_format='%.10f', index=False)