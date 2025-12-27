# UTRGV-Capstone-2025
The goal of this project was to create a machine-learning model capable of accurately identifying devices based on voltage irregularities.  
We used Arduino nanos, Arduino Megas, Raspberry Pi 5Bs and ESP32s to exchange data, then collected that data with an oscilloscope. StreamCollect.py is the script used to collect and organize the raw data. Currently, StreamCollect.py supports UART and I2C communication capture. However, only UART is finished and can be preprocessed for machine learning.  
Preprocessing was done by extracting 20 statistical features from each raw capture. One row within each dataset is made up of a single raw capture, compiled into its statistical features.    
Once preprocessing was finished, the datasets were fed to 5 machine learning algorithms: Random Forest, Support Vector Machine (SVM), K-Nearest Neighbors (KNN), Logistic Regression, and XGBoost. Afterwards, when the model with the highest accuracy was determined, it was deployed.

## Directory Structure
├── Data/
│   ├── StreamCollect.py          # Real-time data collection
│   ├── Formatting/
│   │   ├── framework.py          # Signal analysis framework
│   │   ├── main.py               # Feature extraction pipeline
│   │   └── utils.py              # Metrics and utility functions
│   ├── Processed/                # Feature-extracted CSV datasets
│   └── Devices/                  # Raw oscilloscope captures (UART/I2C)
├── UART scripts/                 # UART transmitter/receiver code
├── I2C scripts/                  # I2C transmitter/receiver code
├── ML/
│   ├── ml_model.ipynb            # initial ML training & evaluation notebook
│   └── ml_model_final.ipynb      # Final ML training & evaluation notebook
└── README.md                     # This

## Dependencies

PicoSDK:  
https://www.picotech.com/downloads/sdk-release/pico-software-development-kit-64bit  

python wrappers:  
https://github.com/picotech/picosdk-python-wrappers  


## External Documentation
PicoSDK Docs:  
https://www.picotech.com/download/manuals/picoscope-2000-series-programmers-guide.pdf  
