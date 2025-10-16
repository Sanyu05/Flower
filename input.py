
def input_name():
    # Ask the user for a CSV file name and validate it
    file_name = input("Introduce the file name: ")

    # Check if the file name ends with '.csv'
    if not file_name.lower().endswith('.csv'):
    # Error handling: raise an exception if the file name is incorrect and ask for a correct name
        raise ValueError("Error: The file name must end with '.csv'. Please provide a valid CSV file name.")

    # If the name is correct print a confirmation message
    print(f"The file name '{file_name}' is valid.")
    return file_name