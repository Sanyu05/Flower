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
    plot_type = input("Enter plot type (bar, line, scatter): ").lower()
    if plot_type not in ['bar', 'line', 'scatter']:
        print("Invalid plot type. Using bar chart.")
        plot_type = 'bar'

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
        plt.scatter(x_values, y_values, color='red')

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
