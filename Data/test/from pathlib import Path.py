from pathlib import Path
import pandas as pd
import chardet
import shutil
from datetime import datetime

def detect_and_convert_csv_to_utf8(root_dir):
    """
    Recursively find all CSV files and convert them to UTF-8 encoding
    """
    root_path = Path(root_dir)
    
    if not root_path.exists():
        print(f"Error: Directory {root_path} does not exist")
        return
    
    # Create backup directory with timestamp
    backup_dir = root_path.parent / f"CSV_Backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    backup_dir.mkdir(exist_ok=True)
    
    converted_count = 0
    error_count = 0
    already_utf8_count = 0
    
    # Find all CSV files recursively
    csv_files = list(root_path.rglob("*.csv"))
    print(f"Found {len(csv_files)} CSV files to process...")
    
    for csv_file in csv_files:
        try:
            print(f"Processing: {csv_file}")
            
            # Detect current encoding
            with open(csv_file, 'rb') as f:
                raw_data = f.read()
                encoding_result = chardet.detect(raw_data)
                current_encoding = encoding_result['encoding']
                confidence = encoding_result['confidence']
            
            print(f"  Detected encoding: {current_encoding} (confidence: {confidence:.2f})")
            
            # Skip if already UTF-8
            if current_encoding and current_encoding.lower().startswith('utf-8'):
                print(f"  Already UTF-8, skipping...")
                already_utf8_count += 1
                continue
            
            # Create backup
            relative_path = csv_file.relative_to(root_path)
            backup_file = backup_dir / relative_path
            backup_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(csv_file, backup_file)
            print(f"  Backup created: {backup_file}")
            
            # Try to read with detected encoding
            try:
                df = pd.read_csv(csv_file, encoding=current_encoding)
            except:
                # If detected encoding fails, try common encodings
                encodings_to_try = ['utf-8-sig', 'cp1252', 'latin1', 'iso-8859-1']
                df = None
                working_encoding = None
                
                for enc in encodings_to_try:
                    try:
                        df = pd.read_csv(csv_file, encoding=enc)
                        working_encoding = enc
                        print(f"  Successfully read with: {enc}")
                        break
                    except:
                        continue
                
                if df is None:
                    print(f"  ERROR: Could not read file with any encoding")
                    error_count += 1
                    continue
            
            # Save as UTF-8
            df.to_csv(csv_file, index=False, encoding='utf-8')
            print(f"  Converted to UTF-8 successfully")
            converted_count += 1
            
        except Exception as e:
            print(f"  ERROR processing {csv_file}: {e}")
            error_count += 1
            continue
    
    # Summary
    print(f"\n" + "="*50)
    print(f"CONVERSION SUMMARY:")
    print(f"Total CSV files found: {len(csv_files)}")
    print(f"Already UTF-8: {already_utf8_count}")
    print(f"Successfully converted: {converted_count}")
    print(f"Errors: {error_count}")
    print(f"Backup directory: {backup_dir}")
    print(f"="*50)

if __name__ == "__main__":
    # Set your devices directory path
    devices_dir = "E:/GitHub/UTRGV-Capstone-2025/Data/Devices"
    
    print("CSV Encoding Converter")
    print(f"Root directory: {devices_dir}")
    print("This will:")
    print("1. Create a timestamped backup of all CSV files")
    print("2. Convert all CSV files to UTF-8 encoding")
    print("3. Preserve original file structure")
    
    response = input("\nProceed? (y/N): ").lower().strip()
    if response == 'y':
        detect_and_convert_csv_to_utf8(devices_dir)
    else:
        print("Operation cancelled.")