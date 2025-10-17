import importFile as imf
import numpy as np
import input as ipt
import re
import math

# Try the simple loader first
try:
    file_name = ipt.input_name()  # Get the file name from user input
    data, metadata = imf.simple_csv_loader(file_name)  ## need a to input file name from user
    print("Successfully loaded with simple loader!")
    summary = imf.get_data_summary(data, metadata)
    print(f"Loaded: {summary['shape']}")
    print("First few columns:")
    for col_name in list(metadata['column_names']):
        col_info = summary['columns'][col_name]
        print(f"  {col_name}: {col_info['type']} ({col_info['non_empty']} values)")
        
except Exception as e:
    print(f"Simple loader failed: {e}")
    # Fall back to robust loader
    try:
        data, metadata = imf.load_csv_data('customers-100.csv')
        print("Successfully loaded with robust loader!")
    except Exception as e2:
        print(f"Both loaders failed: {e2}")

# Print detailed summaryclear
#import pprint
#pprint.pprint(summary, width=80, depth=3)

def print_summary(summary):
    print("=" * 50)
    print(f"DATA SUMMARY")
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
        
        print()  # Empty line between columns

'''''
 Usage
print_summary(summary)

print(data['Customer Id'])  # First 5 CustomerID values

# Each column is a proper NumPy array
print(type(data['First Name']))            # <class 'numpy.ndarray'>
print(data['First Name'].shape)            # (100,) - 100 elements
print(data['First Name'].dtype)            # <U8 - Unicode string, max 8 chars
print(data['Index'].dtype)                 # float64 - numeric columns become floats
'''''
    
print_summary(summary)