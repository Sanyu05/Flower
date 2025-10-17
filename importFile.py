import csv
import numpy as np
from pathlib import Path
import re
import math

"""""" 
def load_csv_data(file_path):  # Do not use, use simple_csv_loader instead #
    """
    Load CSV data with robust delimiter detection and flexible structure.
    Returns data as numpy arrays with column names and metadata.
    """
    data = {}  # Empty dictionary that will store {'column_name': numpy_array} pairs
    metadata = {
        'file_path': str(file_path),
        'column_names': [],
        'column_types': [],
        'num_rows': 0,
        'num_cols': 0
    }

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            sample = file.read(2048)
            file.seek(0)

            try:
                dialect = csv.Sniffer().sniff(sample)
            except csv.Error:
                dialect = csv.excel()
                dialect.delimiter = ','

            file.seek(0)
            reader = csv.reader(file, dialect)
            first_row = next(reader, None)
            second_row = next(reader, None)
            file.seek(0)

            if not first_row:
                raise ValueError("CSV file is empty")

            has_header = True
            if second_row:
                first_row_all_string = all(
                    isinstance(cell, str)
                    and not cell.replace('.', '').replace('-', '').isdigit()
                    for cell in first_row
                )
                has_header = first_row_all_string
            else:
                has_header = False

            if has_header:
                reader = csv.DictReader(file, dialect)
                headers = reader.fieldnames
                rows = list(reader)
            else:
                file.seek(0)
                reader = csv.reader(file, dialect)
                rows = list(reader)
                headers = [f'col_{i}' for i in range(len(rows[0]))]
                file.seek(0)
                reader = csv.DictReader(file, fieldnames=headers, dialect=dialect)
                rows = list(reader)
                if has_header:
                    rows = rows[1:]

            metadata['column_names'] = headers
            metadata['num_cols'] = len(headers)
            metadata['num_rows'] = len(rows)
            metadata['has_header'] = has_header
            metadata['delimiter'] = dialect.delimiter

            for header in headers:
                column_data = []
                for row in rows:
                    value = row[header]
                    if value is None or value == '':
                        continue
                    column_data.append(value)

                if not column_data:
                    data[header] = np.array([])
                    metadata['column_types'].append('empty')
                    continue

                try:
                    numeric_data = [float(item) for item in column_data]
                    data[header] = np.array(numeric_data)
                    metadata['column_types'].append('numeric')
                except (ValueError, TypeError):
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

        if col_type == 'numeric' and len(col_data) > 0:
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


def simple_csv_loader(file_path):
    """Simple CSV loader with proper number handling"""
    data = {}
    metadata = {
        'file_path': str(file_path),
        'column_names': [],
        'column_types': [],
        'num_rows': 0,
        'num_cols': 0,
        'has_header': True,
        'delimiter': ','
    }

    with open(file_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        rows = list(reader)

        if not rows:
            return data, metadata

        headers = reader.fieldnames
        metadata['column_names'] = headers
        metadata['num_cols'] = len(headers)
        metadata['num_rows'] = len(rows)

        for header in headers:
            column_data = [row[header] for row in rows if row[header] != '']

            if not column_data:
                data[header] = np.array([])
                metadata['column_types'].append('empty')
                continue

            if _can_convert_to_numeric(column_data, header):
                numeric_data = []
                for item in column_data:
                    try:
                        numeric_data.append(_clean_number(item))
                    except ValueError:
                        data[header] = np.array(column_data, dtype=str)
                        metadata['column_types'].append('string')
                        break
                else:
                    data[header] = np.array(numeric_data)
                    metadata['column_types'].append('numeric')
            else:
                data[header] = np.array(column_data, dtype=str)
                metadata['column_types'].append('string')

    return data, metadata


def _can_convert_to_numeric(column_data, header_name):
    """Check if column should be treated as numeric"""
    header_lower = header_name.lower()
    numeric_headers = [
        'rating', 'score', 'votes', 'gross', 'revenue', 'price',
        'amount', 'total', 'count', 'number', 'percentage', 'percent',
        'year', 'time', 'duration', 'runtime', 'length'
    ]

    if any(indicator in header_lower for indicator in numeric_headers):
        return True

    sample_size = min(5, len(column_data))
    for i in range(sample_size):
        try:
            _clean_number(column_data[i])
        except ValueError:
            return False
    return True


def _clean_number(value):
    """
    Clean and convert strings like '175 min', '$3.2M', '45%', '2h 15min', etc. to float/int.
    Ignores trailing text or units automatically.
    """
    if value is None:
        return float('nan')

    original_value = str(value).strip()
    if original_value == '':
        return float('nan')

    cleaned = original_value

    # --- Handle runtime strings like '2h 15min' or '150 min' ---
    runtime_pattern = re.compile(r'(?:(\d+)h)?\s*(?:(\d+)m|min)?', re.IGNORECASE)
    if any(unit in cleaned.lower() for unit in ['h', 'min']):
        match = runtime_pattern.fullmatch(cleaned.replace(' ', ''))
        if match:
            hours = int(match.group(1)) if match.group(1) else 0
            minutes = int(match.group(2)) if match.group(2) else 0
            total_minutes = hours * 60 + minutes
            return float(total_minutes)

    cleaned = cleaned.strip('()')
    cleaned = cleaned.replace(',', '').replace('$', '').replace('€', '').replace('£', '').strip()

    if cleaned.endswith('%'):
        try:
            return float(cleaned[:-1]) / 100
        except ValueError:
            pass

    multiplier = 1
    if cleaned.upper().endswith('M'):
        cleaned = cleaned[:-1]
        multiplier = 1_000_000
    elif cleaned.upper().endswith('B'):
        cleaned = cleaned[:-1]
        multiplier = 1_000_000_000
    elif cleaned.upper().endswith('K'):
        cleaned = cleaned[:-1]
        multiplier = 1_000

    match = re.search(r"[-+]?\d*\.?\d+", cleaned)
    if not match:
        raise ValueError(f"Could not extract number from '{original_value}'")

    num_str = match.group(0)
    result = float(num_str) * multiplier
    return int(result) if result.is_integer() else result


def convert_string_to_numeric(data, metadata, column_name):
    if column_name not in data:
        raise KeyError(f"Column '{column_name}' not found in data")

    if metadata['column_types'][metadata['column_names'].index(column_name)] != 'string':
        print(f"Column '{column_name}' is not of type 'string'. No conversion needed.")
        return

    column_data = data[column_name]
    numeric_data = []

    success = True
    for item in column_data:
        try:
            numeric_data.append(_clean_number(item))
        except ValueError:
            success = False
            print(f"⚠️ Warning: '{item}' could not be converted. Conversion aborted.")
            break

    if success:
        data[column_name] = np.array(numeric_data)
        metadata['column_types'][metadata['column_names'].index(column_name)] = 'numeric'
        print(f"✅ Successfully converted '{column_name}' to numeric.")
    else:
        print(f"❌ Column '{column_name}' remains as string (conversion failed).")


def prompt_user_for_conversion(data, metadata):
    """Prompt user to select string columns to convert to numeric manually."""
    string_cols = [col for col, t in zip(metadata['column_names'], metadata['column_types']) if t == 'string']

    if not string_cols:
        print("No string columns available for conversion.")
        return

    print("\nString columns detected:")
    for i, col in enumerate(string_cols, 1):
        print(f"{i}. {col}")

    choice = input("\nEnter the number(s) of columns to convert to numeric (comma-separated), or press Enter to skip: ").strip()
    if not choice:
        return

    try:
        indices = [int(i) - 1 for i in choice.split(',')]
        for idx in indices:
            col_name = string_cols[idx]
            convert_string_to_numeric(data, metadata, col_name)
    except (ValueError, IndexError):
        print("Invalid selection. No columns converted.")
