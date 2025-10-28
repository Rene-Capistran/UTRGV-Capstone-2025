from pathlib import Path
import os 
DEVICE_DIR = Path(__file__).parent


labels = ['A','B','C','D','E','F','G','H','I','J','K','L']

for device in DEVICE_DIR.iterdir():
    if not device.is_dir():
        continue
    for model in device.iterdir():
        if not model.is_dir():
            continue
        for baud in ['9600', '115200']:
            baud_dir = model / baud
            if not baud_dir.is_dir():
                os.makedirs(baud_dir)
                print(f"Created directory: {baud_dir}")
            for label in labels:
                label_dir = baud_dir / label
                if not label_dir.is_dir():
                    os.makedirs(label_dir)
                    print(f"Created directory: {label_dir}")
