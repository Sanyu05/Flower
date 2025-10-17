import importFile as imf
import numpy as np
import input as ipt
import Visualization as viz

# -------------------------------
# STEP 1: Load CSV Data
# -------------------------------
def load_data_interactive():
    """
    Load CSV data using simple loader first, and fall back to robust loader if needed.
    
    Returns:
        data (dict): Dictionary mapping column names to NumPy arrays
        metadata (dict): Metadata including column names, types, row/column counts
    """
    file_name = ipt.input_name()  # Get the file name from user input
    
    try:
        data, metadata = imf.simple_csv_loader(file_name)
        print("✅ Successfully loaded with simple loader!")
        return data, metadata
    except Exception as e:
        print(f"⚠️ Simple loader failed: {e}")
        # Fall back to robust loader
        try:
            data, metadata = imf.load_csv_data(file_name)
            print("✅ Successfully loaded with robust loader!")
            return data, metadata
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

# -------------------------------
# STEP 3: Manual Conversion Option
# (Uses functions from importFile.py)
# -------------------------------

# -------------------------------
# MAIN PROGRAM
# -------------------------------
def main():
    """Main program loop for data analysis and visualization."""
    
    # Load data
    data, metadata = load_data_interactive()
    
    # Display initial summary
    summary = imf.get_data_summary(data, metadata)
    print(f"\nLoaded: {summary['shape']}")
    print("First few columns:")
    for col_name in list(metadata['column_names']):
        col_info = summary['columns'][col_name]
        print(f"  {col_name}: {col_info['type']} ({col_info['non_empty']} values)")
    
    print_summary(summary)
    
    # Offer string to numeric conversion
    imf.prompt_user_for_conversion(data, metadata)
    
    # Update and reprint summary after potential conversion
    summary = imf.get_data_summary(data, metadata)
    print("\nUPDATED SUMMARY:")
    print_summary(summary)
    
    # Interactive visualization loop
    while True:
        print("\n" + "=" * 50)
        choice = input("\nWould you like to create a visualization? (yes/no): ").lower()
        if choice in ['yes', 'y']:
            try:
                viz.interactive_plot(data, metadata)
            except Exception as e:
                print(f"❌ Error creating plot: {e}")
        else:
            print("Exiting program. Goodbye!")
            break

if __name__ == "__main__":
    main()