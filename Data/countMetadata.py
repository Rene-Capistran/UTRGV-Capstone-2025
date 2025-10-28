from pathlib import Path
import json
import re

BASE = Path(__file__).parent
META = BASE / "metadata.json"
DEVICE_DIR = BASE / "Devices"


# load existing metadata
if META.exists():
    with META.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
else:
    data = {}

if not DEVICE_DIR.exists():
    raise FileNotFoundError(f"Devices directory not found: {DEVICE_DIR.resolve()}")

# iterate platform > model > device_label
for platform_dir in DEVICE_DIR.iterdir():
    if not platform_dir.is_dir():
        continue
    platform = platform_dir.name
    data.setdefault(platform, {})

    for model_dir in platform_dir.iterdir():
        if not model_dir.is_dir():
            continue
        model = model_dir.name
        data[platform].setdefault(model, {})


        for baud_dir in model_dir.iterdir():
            if not baud_dir.is_dir():
                continue
            baud = baud_dir.name
            data[platform][model].setdefault(baud, {})

            for device_label in baud_dir.iterdir():
                label_dir = baud_dir / device_label
                if not label_dir.is_dir():
                    continue
                label = device_label.name
                counts = {"Captures_Small": 0, "Captures_Medium": 0, "Captures_Large": 0}
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

                data[platform][model][baud][label] = counts

# write updated metadata
with META.open("w", encoding="utf-8") as f:
    json.dump(data, f, indent=4)

print(f"Updated metadata: {META}")