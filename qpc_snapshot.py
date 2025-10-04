import re
import os
import sys
from datetime import datetime

"""
    QPC State snapshot
    ============================
    This module generate a library to get the current state of your state machines, just for the sake of Assert Log.

    Usage: python.py "path/to/qp_snapshot.py" "['path/to/the/qm/generated/files/','another/path/if/necessary']"

    Author: Ramon Rodrigues Martins (https://github.com/mon-martins)

    Date: 04/10/25
    
    Version: 1.0.0

"""

def generate_enum_from_header(header_path, enum_name, allowed_return_types=None, required_param_types=None):
    """
    Parses a C header file and generates a C enum with numeric values for each function found,
    optionally filtering by return types and required parameter types.

    Args:
        header_path (str): Path to the C header file.
        enum_name (str): Name of the enum to be generated.
        allowed_return_types (list[str], optional): List of allowed return types (e.g., ['void', 'int']).
        required_param_types (list[str], optional): List of required parameter types.

    Returns:
        str or None: The generated C enum as a string, or None if no matching functions are found.
    """
    with open(header_path, 'r') as file:
        content = file.read()

    pattern = re.compile(r'\b([\w\s\*\(\)]+?)\s+(\w+)\s*\(([^;{]*)\)\s*;')
    matches = pattern.findall(content)

    if not matches:
        print(f"[INFO] No function declarations found in {header_path}.")
        return None

    enum_lines = [f"typedef enum {enum_name} {{"]

    count = 0
    for return_type, func_name, param_list in matches:
        normalized_return = ' '.join(return_type.strip().split()).replace(' *', '*')
        normalized_params = param_list.replace('\n', ' ').replace('\t', ' ').strip()

        if allowed_return_types and normalized_return not in allowed_return_types:
            continue

        if required_param_types and not all(param_type in normalized_params for param_type in required_param_types):
            continue

        enum_lines.append(f"    {func_name.upper()} = {count},")
        count += 1

    if count == 0:
        print(f"[INFO] No functions matched the provided filters in {header_path}.")
        return None

    enum_lines.append(f"    {enum_name.upper()}_NUMBER_OF_VALUES")
    enum_lines.append(f"}} {enum_name}_t;\n")

    return "\n".join(enum_lines)


def extract_function_names(header_path, allowed_return_types=None, required_param_types=None):
    """
    Parses a C header file and extracts function names based on filters.

    Args:
        header_path (str): Path to the C header file.
        allowed_return_types (list[str], optional): List of allowed return types.
        required_param_types (list[str], optional): List of required parameter types.

    Returns:
        list[str]: List of matching function names.
    """
    with open(header_path, 'r') as file:
        content = file.read()

    pattern = re.compile(r'\b([\w\s\*\(\)]+?)\s+(\w+)\s*\(([^;{]*)\)\s*;')
    matches = pattern.findall(content)

    if not matches:
        print(f"[INFO] No function declarations found in {header_path}.")
        return []

    matching_functions = []

    for return_type, func_name, param_list in matches:
        normalized_return = ' '.join(return_type.strip().split()).replace(' *', '*')
        normalized_params = param_list.replace('\n', ' ').replace('\t', ' ').strip()

        if allowed_return_types and normalized_return not in allowed_return_types:
            continue

        if required_param_types and not all(param_type in normalized_params for param_type in required_param_types):
            continue

        matching_functions.append(func_name)

    return matching_functions


def find_header_files(directory):
    """
    Recursively finds all .h files in a directory and its subdirectories.

    Args:
        directory (str): Path to the root directory.

    Returns:
        list[str]: List of full paths to found .h files.
    """
    header_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.h'):
                header_files.append(os.path.join(root, file))
    return header_files


def generate_qp_snapshot_files(paths_to_search):
    """
    Generates QP snapshot header and source files for state machine inspection.

    Args:
        paths_to_search (list[str]): List of directories to search for header files.

    Returns:
        None
    """
    output_file_base = "qp_snapshot"
    header_file_name = output_file_base + ".h"
    source_file_name = output_file_base + ".c"

    with open(header_file_name, "w", encoding="utf-8") as header_file, \
         open(source_file_name, "w", encoding="utf-8") as source_file:

        current_date = datetime.now().strftime('%Y-%m-%d')

        # Header file preamble
        header_file.write("/************************************************************/\n")
        header_file.write("// Automatically generated C header file\n")
        header_file.write(f"// Date created: {current_date}\n")
        header_file.write("/************************************************************/\n\n")
        header_file.write('#include "qpc.h"\n')

        # Source file preamble
        source_file.write("/************************************************************/\n")
        source_file.write("// Automatically generated C source file\n")
        source_file.write(f"// Date created: {current_date}\n")
        source_file.write("/************************************************************/\n\n")
        source_file.write(f'#include "{header_file_name}"\n')

        # Discover header files
        header_files = []
        for path in paths_to_search:
            header_files += find_header_files(path)

        header_files = list(set(header_files))  # Remove duplicates

        # Process each header file
        for header_path in header_files:
            file_base = os.path.splitext(os.path.basename(header_path))[0]
            enum_name = f"snapshot_{file_base}"

            # Header section
            header_file.write("\n\n")
            header_file.write("// ================================================================================\n")
            header_file.write(f"// State machine from file \"{os.path.basename(header_path)}\"\n")
            header_file.write("// ================================================================================\n\n")

            # Source section
            source_file.write("\n\n")
            source_file.write("// ================================================================================\n")
            source_file.write(f"// State machine from file \"{os.path.basename(header_path)}\"\n")
            source_file.write("// ================================================================================\n\n")

            enum_definition = generate_enum_from_header(
                header_path,
                enum_name,
                allowed_return_types=['QState'],
                required_param_types=['QEvt const * const']
            )

            if not enum_definition:
                continue

            header_file.write(enum_definition)

            function_names = extract_function_names(
                header_path,
                allowed_return_types=['QState'],
                required_param_types=['QEvt const * const']
            )

            # Function declaration in header
            header_file.write("\n")
            header_file.write(f"uint64_t {file_base}_get_current_state(QAsm const * const state_machine);\n")

            # Function implementation in source
            source_file.write(f"uint64_t {file_base}_get_current_state(QAsm const * const state_machine) {{\n")
            source_file.write("    uint64_t current_state = 0;\n")

            for func_name in function_names:
                source_file.write(f"    current_state |= ((uint64_t) QASM_IS_IN(state_machine, {func_name}) << {func_name.upper()});\n")

            source_file.write("    return current_state;\n")
            source_file.write("}\n")

            header_file.write("\n")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise Exception("Missing parameter. Usage: python main.py \"['./dir1', './dir2']\"")

    # Parse input path argument
    raw_input = sys.argv[1].strip("[] ")
    paths = [item.strip().strip("'\"") for item in raw_input.split(',')]

    generate_qp_snapshot_files(paths)
