from pathlib import Path
import json
import re

BASE = Path(__file__).parent
META = BASE / "metadata.json"

pattern = re.compile(r'votlages_([A-Za-z]+)_\d+\.csv', re.I)  

if META.exists():
    data = json.loads(META.read_text())
else:
    data = {}

for platform_dir in BASE.iterdir():
    if not platform_dir.is_dir() or platform_dir.name == "__pycache__":
        continue
    platform = platform_dir.name
    data.setdefault(platform, {})
    for model_dir in platform_dir.iterdir():
        if not model_dir.is_dir():
            continue
        model = model_dir.name
        counts = {"Captures_Small": 0, "Captures_Medium": 0, "Captures_Large": 0}

        for f in model_dir.iterdir():
            if not f.is_file() or f.suffix.lower() != ".csv":
                continue
            m = pattern.match(f.name)
            if m:
                size = m.group(1).lower()
            else:
                # fallback: look for keywords in filename
                name = f.name.lower()
                if "small" in name:
                    size = "small"
                elif "medium" in name:
                    size = "medium"
                elif "large" in name:
                    size = "large"
                else:
                    continue

            if size == "small":
                counts["Captures_Small"] += 1
            elif size == "medium":
                counts["Captures_Medium"] += 1
            elif size == "large":
                counts["Captures_Large"] += 1

        data[platform][model] = counts

# write updated metadata (overwrite)
META.write_text(json.dumps(data, indent=4))
print(f"Updated metadata: {META}")