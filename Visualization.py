import matplotlib.pyplot as plt
import numpy as np
import importFile as imf
import input as ipt

def load_data_interactive():
    """
    Load CSV data using simple loader first, and fall back to robust loader if needed.
    
    Returns:
        data (dict): Dictionary mapping column names to NumPy arrays
        metadata (dict): Metadata including column names, types, row/column counts
    """
    file_name = ipt.input_name()  
    try:
        data, metadata = imf.simple_csv_loader(file_name)
        print("Successfully loaded with simple loader!")
    except Exception as e:
        print(f"Simple loader failed: {e}")
        try:
            data, metadata = imf.load_csv_data(file_name)
            print("Successfully loaded with robust loader!")
        except Exception as e2:
            raise Exception(f"Both loaders failed: {e2}")
    return data, metadata

def interactive_plot(data, metadata):
    columns = metadata['column_names']
    col_types = metadata['column_types']
    
    print("\nAvailable columns:", columns)

    # Select plot type first
    '''
    plot_type = input("Enter plot type (bar, line, scatter): ").lower()
    if plot_type not in ['bar', 'line', 'scatter']:
        print("Invalid plot type. Using bar chart.")
        plot_type = 'bar'
        '''

    # **UPDATED: Added new plot options**
    plot_type = input("Enter plot type (bar, line, scatter, histogram, pie): ").lower()
    if plot_type not in ['bar', 'line', 'scatter', 'histogram', 'pie']:
        print("Invalid plot type. Using bar chart.")
        plot_type = 'bar'

    numeric_columns = [col for col, typ in zip(columns, col_types) if typ == 'numeric']

    # **HISTOGRAM: only need one numeric column**
    if plot_type == 'histogram':
        print("Columns available for histogram (numeric only):", numeric_columns)
        while True:
            hist_column = input("Enter the column name for histogram: ")
            if hist_column in numeric_columns:
                break
            print(f"Invalid column '{hist_column}'. Must be numeric. Try again.")
        
        plt.figure(figsize=(8, 6))
        plt.hist(data[hist_column], bins=20, color='purple', edgecolor='black')
        plt.xlabel(hist_column)
        plt.ylabel("Frequency")
        plt.title(f"Histogram of {hist_column}")
        plt.tight_layout()
        plt.show()
        return
    
    elif plot_type == 'pie':
        cat_columns = [col for col, typ in zip(columns, col_types) if typ != 'numeric']
        if not cat_columns:
            print("No categorical columns available for pie chart.")
            return
        print("Categorical columns available:", cat_columns)
        cat_col = input("Enter the categorical column for pie chart: ")
        if cat_col not in cat_columns:
            print("Invalid categorical column.")
            return
        values, counts = np.unique(data[cat_col], return_counts=True)
        plt.figure(figsize=(7,7))
        plt.pie(counts, labels=values, autopct='%1.1f%%', startangle=90)
        plt.title(f"Distribution of {cat_col}")
        plt.tight_layout()
        plt.show()
        return

    # Prompt Y-axis until numeric
    numeric_columns = [col for col, typ in zip(columns, col_types) if typ == 'numeric']
    print("Columns available for Y-axis (numeric only):", numeric_columns)
    while True:
        y_column = input("Enter the column name for Y-axis: ")
        if y_column in numeric_columns:
            break
        print(f"Invalid column. '{y_column}' is not numeric. Please try again.")

    # Prompt X-axis based on plot type
    while True:
        if plot_type == 'bar':
            x_column = input("Enter the column name for X-axis (string or numeric): ")
            if x_column in columns:
                break
            print(f"Invalid column '{x_column}'. Try again.")
        else:
            x_numeric_columns = [col for col, typ in zip(columns, col_types) if typ == 'numeric']
            print("Columns available for X-axis (numeric only for line/scatter):", x_numeric_columns)
            x_column = input("Enter the column name for X-axis: ")
            if x_column in x_numeric_columns:
                break
            print(f"Invalid column '{x_column}'. Must be numeric. Try again.")

    x_values = data[x_column]
    y_values = data[y_column]

    # Sort for line/scatter if X is numeric
    if plot_type in ['line', 'scatter'] and np.issubdtype(x_values.dtype, np.number):
        sorted_indices = np.argsort(x_values)
        x_values = x_values[sorted_indices]
        y_values = y_values[sorted_indices]

    # Plot
    plt.figure(figsize=(10,6))
    if plot_type == 'bar':
        plt.bar(x_values, y_values, color='skyblue')
    elif plot_type == 'line':
        plt.plot(x_values, y_values, marker='o', linestyle='-', color='green')
    elif plot_type == 'scatter':
        plt.scatter(x_values, y_values, color='red', alpha = 0.7)
    # **NEW: Add regression trendline (optional)**
    if np.issubdtype(x_values.dtype, np.number):
            m, b = np.polyfit(x_values, y_values, 1)
            plt.plot(x_values, m*x_values + b, color='black', linestyle='--', label='Trendline')
            plt.legend()

    plt.xlabel(x_column)
    plt.ylabel(y_column)
    plt.title(f"{y_column} vs {x_column} ({plot_type.title()} Plot)")

    if np.issubdtype(x_values.dtype, np.str_):
        plt.xticks(rotation=45, ha='right')

    plt.tight_layout()
    plt.show()

def main():
    data, metadata = load_data_interactive()
    interactive_plot(data, metadata)

if __name__ == "__main__":
    main()

'''
# original code block for reference

def interactive_plot(data, metadata):
    columns = metadata['column_names']
    col_types = metadata['column_types']
    
    print("\nAvailable columns:", columns)

    # Extended plot options
    available_plots = ['bar', 'line', 'scatter']
    plot_type = input(f"Enter plot type {available_plots}: ").lower()
    if plot_type not in available_plots:
        print(f"Invalid plot type. Defaulting to 'bar'.")
        plot_type = 'bar'

    numeric_columns = [col for col, typ in zip(columns, col_types) if typ == 'numeric']

    print("Columns available for Y-axis (numeric only):", numeric_columns)
    while True:
        y_column = input("Enter the column name for Y-axis: ")
        if y_column in numeric_columns:
            break
        print(f"Invalid column. '{y_column}' is not numeric. Please try again.")

    while True:
        if plot_type == 'bar':
            x_column = input("Enter the column name for X-axis (string or numeric): ")
            if x_column in columns:
                break
            print(f"Invalid column '{x_column}'. Try again.")
        else:
            x_numeric_columns = [col for col, typ in zip(columns, col_types) if typ == 'numeric']
            print("Columns available for X-axis (numeric only for line/scatter):", x_numeric_columns)
            x_column = input("Enter the column name for X-axis: ")
            if x_column in x_numeric_columns:
                break
            print(f"Invalid column '{x_column}'. Must be numeric. Try again.")

    x_values = data[x_column]
    y_values = data[y_column]

    if plot_type in ['line', 'scatter'] and np.issubdtype(x_values.dtype, np.number):
        sorted_indices = np.argsort(x_values)
        x_values = x_values[sorted_indices]
        y_values = y_values[sorted_indices]

    plt.figure(figsize=(10,6))
    if plot_type == 'bar':
        plt.bar(x_values, y_values, color='skyblue')
    elif plot_type == 'line':
        plt.plot(x_values, y_values, marker='o', linestyle='-', color='green')
    elif plot_type == 'scatter':
        plt.scatter(x_values, y_values, color='red')

    plt.xlabel(x_column)
    plt.ylabel(y_column)
    plt.title(f"{y_column} vs {x_column} ({plot_type.title()} Plot)")

    if np.issubdtype(x_values.dtype, np.str_):
        plt.xticks(rotation=45, ha='right')

    plt.tight_layout()
    plt.show()

    '''
