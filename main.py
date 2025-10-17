import importFile as imf
import numpy as np
import input as ipt
import re
import math

# -------------------------------
# STEP 1: Load CSV Data
# -------------------------------
try:
    file_name = ipt.input_name()  # Get the file name from user input
    data, metadata = imf.simple_csv_loader(file_name)
    print("✅ Successfully loaded with simple loader!")
    summary = imf.get_data_summary(data, metadata)
    print(f"\nLoaded: {summary['shape']}")
    print("First few columns:")
    for col_name in list(metadata['column_names']):
        col_info = summary['columns'][col_name]
        print(f"  {col_name}: {col_info['type']} ({col_info['non_empty']} values)")

except Exception as e:
    print(f"⚠️ Simple loader failed: {e}")
    # Fall back to robust loader
    try:
        data, metadata = imf.load_csv_data(file_name)
        print("✅ Successfully loaded with robust loader!")
        summary = imf.get_data_summary(data, metadata)
    except Exception as e2:
        print(f"❌ Both loaders failed: {e2}")
        exit(1)

# -------------------------------
# STEP 2: Display Summary
# -------------------------------
def print_summary(summary):
    print("\n" + "=" * 50)
    print("DATA SUMMARY")
    print("=" * 50)
    print(f"File: {summary['file']}")
    print(f"Shape: {summary['shape']}")
    print("\nCOLUMNS:")
    print("-" * 30)
    
    for col_name, col_info in summary['columns'].items():
        print(f"📊 {col_name}:")
        print(f"   Type: {col_info['type']}")
        print(f"   Non-empty values: {col_info['non_empty']}")
        
        if col_info['type'] == 'numeric':
            print(f"   Min: {col_info['min']:.2f}")
            print(f"   Max: {col_info['max']:.2f}")
            print(f"   Mean: {col_info['mean']:.2f}")
            print(f"   Std: {col_info['std']:.2f}")
        elif col_info['type'] == 'string':
            print(f"   Unique values: {col_info['unique_values']}")
        
        print()

# Print initial summary
print_summary(summary)

# -------------------------------
# STEP 3: Manual Conversion Option
# -------------------------------
def convert_string_to_numeric(data, metadata, column_name):
    """Try converting a string column to numeric."""
    if column_name not in data:
        print(f"❌ Column '{column_name}' not found.")
        return

    idx = metadata['column_names'].index(column_name)
    if metadata['column_types'][idx] != 'string':
        print(f"⚠️ Column '{column_name}' is not a string column.")
        return

    col_data = data[column_name]
    new_data = []
    success = True
    for val in col_data:
        try:
            new_data.append(imf._clean_number(val))
        except ValueError:
            print(f"⚠️ Value '{val}' could not be converted — aborting conversion.")
            success = False
            break

    if success:
        data[column_name] = np.array(new_data)
        metadata['column_types'][idx] = 'numeric'
        print(f"✅ Column '{column_name}' successfully converted to numeric.")
    else:
        print(f"❌ Conversion of '{column_name}' failed — column left unchanged.")


def prompt_user_for_conversion(data, metadata):
    """Prompt user to convert string columns to numeric manually."""
    string_cols = [col for col, t in zip(metadata['column_names'], metadata['column_types']) if t == 'string']
    if not string_cols:
        print("\nNo string columns available for conversion.")
        return

    print("\nString columns detected:")
    for i, col in enumerate(string_cols, start=1):
        print(f"{i}. {col}")

    choice = input("\nEnter the number(s) of columns to convert (comma-separated), or press Enter to skip: ").strip()
    if not choice:
        return

    try:
        indices = [int(i.strip()) - 1 for i in choice.split(',')]
        for idx in indices:
            if 0 <= idx < len(string_cols):
                convert_string_to_numeric(data, metadata, string_cols[idx])
            else:
                print(f"⚠️ Invalid selection: {idx + 1}")
    except ValueError:
        print("❌ Invalid input. Please enter valid numbers.")

# -------------------------------
# STEP 4: Run conversion prompt
# -------------------------------
prompt_user_for_conversion(data, metadata)

# Update and reprint summary after potential conversion
summary = imf.get_data_summary(data, metadata)
print("\nUPDATED SUMMARY:")
print_summary(summary)
