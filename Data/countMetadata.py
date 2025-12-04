from pathlib import Path
import json

BASE = Path(__file__).parent
META = BASE / "metadata.json"
DEVICE_DIR = BASE / "Devices"

data = {}

if not DEVICE_DIR.exists():
    raise FileNotFoundError(f"Devices directory not found: {DEVICE_DIR.resolve()}")

def count_csv_files_by_size(label_dir):
    counts = {"Captures_Small": 0, "Captures_Medium": 0, "Captures_Large": 0}
    
    if not label_dir.exists() or not label_dir.is_dir():
        return counts
    
    for f in label_dir.iterdir():
        if not f.is_file() or f.suffix.lower() != ".csv":
            continue
        name = f.name.lower()
        if "small" in name:
            counts["Captures_Small"] += 1
        elif "medium" in name:
            counts["Captures_Medium"] += 1
        elif "large" in name:
            counts["Captures_Large"] += 1
    
    return counts

# protocols
for protocol_dir in DEVICE_DIR.iterdir():
    if not protocol_dir.is_dir():
        continue
    
    protocol = protocol_dir.name.upper() 
    data[protocol] = {}
    
    print(f"\nProcessing {protocol} protocol...")
    
    # platforms
    for platform_dir in protocol_dir.iterdir():
        if not platform_dir.is_dir():
            continue
        platform = platform_dir.name
        data[protocol][platform] = {}
        
        # models 
        for model_dir in platform_dir.iterdir():
            if not model_dir.is_dir():
                continue
            model = model_dir.name
            data[protocol][platform][model] = {}
            
            # baud
            for freq_dir in model_dir.iterdir():
                if not freq_dir.is_dir() or freq_dir.name == "old":
                    continue  
                
                freq = freq_dir.name
                data[protocol][platform][model][freq] = {}
                
                # Process device labels (A, B, C, etc.)
                for label_dir in freq_dir.iterdir():
                    if not label_dir.is_dir():
                        continue
                    label = label_dir.name
                    
                    counts = count_csv_files_by_size(label_dir)
                    data[protocol][platform][model][freq][label] = counts
                    

# Write metadata
with META.open("w", encoding="utf-8") as f:
    json.dump(data, f, indent=4)

print(f"\nMetadata saved to: {META}")