import csv
import numpy as np
from pathlib import Path

""""""
def load_csv_data(file_path): # Do not use, use simple_csv_loader instead #
    """
    Load CSV data with robust delimiter detection and flexible structure.
    Returns data as numpy arrays with column names and metadata.
    """
    data = {} #: Empty dictionary that will store {'column_name': numpy_array} pairs
    metadata = {
        'file_path': str(file_path),
        'column_names': [],
        'column_types': [],
        'num_rows': 0,
        'num_cols': 0
    }
    
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            # Read first few lines to analyze the file
            sample = file.read(2048)
            file.seek(0)  # Reset file pointer
            
            # Try to detect delimiter, fallback to comma if detection fails/delimeter is ambiguous
            try:
                dialect = csv.Sniffer().sniff(sample)
            except csv.Error:
                # If sniffer fails, use comma as default delimiter
                dialect = csv.excel()
                dialect.delimiter = ','
            
            # Check for header by looking at first two rows
            file.seek(0)
            reader = csv.reader(file, dialect)
            first_row = next(reader, None)
            second_row = next(reader, None)
            file.seek(0)
            
            if not first_row: # Empty file 
                raise ValueError("CSV file is empty")
            
            # Simple header detection: if first row contains strings and second contains mixed types - then first row is header
            has_header = True
            if second_row:
                # Check if first row looks like header (mostly strings) and second row has potential data
                first_row_all_string = all(isinstance(cell, str) and not cell.replace('.', '').replace('-', '').isdigit() for cell in first_row)
                """
                Complex check to see if a cell contains only numbers

                Removes decimal points and negative signs

                Checks if remaining characters are all digits

                all(...): Returns True only if ALL cells in first row appear to be text headers

                Decision: If first row is all text and second row exists, assume first row is header

                """""
                if first_row_all_string:
                    has_header = True
                else:
                    has_header = False
            else:
                has_header = False
            
            # Read the data
            if has_header:
                reader = csv.DictReader(file, dialect) # Creates reader that returns OrderedDict for each row with column names as keys
                headers = reader.fieldnames # Extracts column names from header row
                rows = list(reader)  #  Converts all rows to list of dictionaries
            else: # No header, create artificial headers
                  # Create artificial headers like col_0, col_1, ...
                file.seek(0)
                reader = csv.reader(file, dialect)
                rows = list(reader)
                headers = [f'col_{i}' for i in range(len(rows[0]))]
                # Re-read as DictReader for consistency
                file.seek(0)
                reader = csv.DictReader(file, fieldnames=headers, dialect=dialect)
                rows = list(reader)
                if has_header:  # Remove the header row if we created artificial headers
                    rows = rows[1:]
            
            metadata['column_names'] = headers
            metadata['num_cols'] = len(headers)
            metadata['num_rows'] = len(rows)
            metadata['has_header'] = has_header
            metadata['delimiter'] = dialect.delimiter
            
            # Convert to numpy arrays with automatic type detection
            for header in headers:
                column_data = []
                for row in rows:
                    value = row[header]
                    if value is None or value == '': # Skip empty values
                        continue
                    column_data.append(value)
                
                if not column_data:
                    data[header] = np.array([])
                    metadata['column_types'].append('empty')
                    continue
                
                # Try to convert to numeric types first
                try:
                    # Try float conversion
                    numeric_data = []
                    for item in column_data:
                        try:
                            numeric_data.append(float(item))
                        except ValueError:
                            # If any item can't be converted to float, break
                            raise ValueError("Non-numeric value found")
                    
                    data[header] = np.array(numeric_data)
                    metadata['column_types'].append('numeric')
                except (ValueError, TypeError): # If ANY value fails conversion, entire column becomes strings
                    # Keep as string if conversion fails
                    data[header] = np.array(column_data, dtype=str)
                    metadata['column_types'].append('string')
            
            return data, metadata

            
    except Exception as e:
        raise Exception(f"Error loading CSV file {file_path}: {str(e)}")

def get_data_summary(data, metadata):
    """Generate a summary of the loaded data"""
    summary = {
        'file': metadata['file_path'],
        'shape': f"{metadata['num_rows']} rows × {metadata['num_cols']} columns",
        'columns': {}
    }
    
    for i, col_name in enumerate(metadata['column_names']):
        col_data = data[col_name]
        col_type = metadata['column_types'][i]
        
        col_info = {
            'type': col_type,
            'non_empty': len(col_data)
        }
        
        if col_type == 'numeric' and len(col_data) > 0: # Only compute stats if there is data
            col_info.update({
                'min': float(np.min(col_data)), 
                'max': float(np.max(col_data)), 
                'mean': float(np.mean(col_data)),
                'std': float(np.std(col_data))
            })
        elif col_type == 'string' and len(col_data) > 0:
            col_info['unique_values'] = len(np.unique(col_data))
        
        summary['columns'][col_name] = col_info
    
    return summary

# Simple alternative function if the above still has issues
def simple_csv_loader(file_path):
    """Simple CSV loader with proper number handling"""
    data = {} #: Empty dictionary that will store {'column_name': numpy_array} pairs
    metadata = {
        'file_path': str(file_path),
        'column_names': [],
        'column_types': [],
        'num_rows': 0,
        'num_cols': 0,
        'has_header': True,
        'delimiter': ',' # delimiter is assumed to be comma for simplicity
    }
    
    with open(file_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        rows = list(reader)
        
        if not rows:
            return data, metadata
        
        headers = reader.fieldnames
        metadata['column_names'] = headers # List of column names - program assumes first row is header
        metadata['num_cols'] = len(headers)
        metadata['num_rows'] = len(rows)
        
        for header in headers:
            column_data = [row[header] for row in rows if row[header] != ''] 
            
            if not column_data:
                data[header] = np.array([])
                metadata['column_types'].append('empty')
                continue
            
            # Try numeric conversion with proper cleaning - only two types: numeric or string
            if _can_convert_to_numeric(column_data, header):
                numeric_data = [] # Try to convert all items to numeric
                for item in column_data: # Try to clean and convert each item
                    try:
                        numeric_data.append(_clean_number(item))
                    except ValueError:
                        # If any item fails, mark entire column as string
                        data[header] = np.array(column_data, dtype=str)
                        metadata['column_types'].append('string')
                        break
                else: 
                    # All items converted successfully
                    data[header] = np.array(numeric_data)
                    metadata['column_types'].append('numeric')
            else:
                data[header] = np.array(column_data, dtype=str)
                metadata['column_types'].append('string')
    
    return data, metadata

def _can_convert_to_numeric(column_data, header_name): # returns True if column can be treated as numeric
    """Check if column should be treated as numeric"""
    header_lower = header_name.lower()
    
    # These headers are almost always numeric
    numeric_headers = ['rating', 'score', 'votes', 'gross', 'revenue', 'price', 
                      'amount', 'total', 'count', 'number', 'percentage', 'percent',
                      'year', 'time', 'duration', 'runtime', 'length']
    
    if any(indicator in header_lower for indicator in numeric_headers): # If header name suggests numeric data, assume numeric
        return True 
    
    # Try to convert a sample to check if numeric
    sample_size = min(5, len(column_data)) 
    for i in range(sample_size):
        try:
            _clean_number(column_data[i]) # Try to clean and convert
        except ValueError:
            return False
    return True

def _clean_number(value):
    """Clean and convert string numbers with commas, currency, and million/billion notation"""
    if value is None or value == '' or str(value).strip() == '':
        return float('nan')
    
    original_value = str(value).strip()
    cleaned = original_value
    
    # Remove parentheses around years like (1972)
    cleaned = cleaned.strip('()')

    # Remove currency symbols and commas
    cleaned = cleaned.replace(',', '')  # Remove commas from numbers
    cleaned = cleaned.replace('$', '')  # Remove dollar signs
    cleaned = cleaned.replace('€', '')  # Remove euro signs
    cleaned = cleaned.replace('£', '')  # Remove pound signs
    cleaned = cleaned.replace(' ', '')  # Remove spaces
    
    # Handle empty result after cleaning
    if not cleaned or cleaned == '-':
        raise ValueError("Not a numeric value")
    
    # Handle million/billion notation
    multiplier = 1
    if cleaned.upper().endswith('M'):
        cleaned = cleaned[:-1]  # Remove the 'M'
        multiplier = 1_000_000
    elif cleaned.upper().endswith('B'):
        cleaned = cleaned[:-1]  # Remove the 'B'  
        multiplier = 1_000_000_000
    elif cleaned.upper().endswith('K'):
        cleaned = cleaned[:-1]  # Remove the 'K'
        multiplier = 1_000
    
    # Handle percentage values
    if cleaned.endswith('%'):
        cleaned = cleaned[:-1]
        return float(cleaned) / 100
    
    # Convert to float and apply multiplier
    try:
        result = float(cleaned) * multiplier

        # If value is a whole number (like 1972.0), convert to int
        if result.is_integer():
            result = int(result)
            
        return result
    except ValueError:
        raise ValueError(f"Could not convert '{original_value}' to number")
    

