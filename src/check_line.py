from src.table import Line


def validate_input_sequence(input_sequence: list[str], analysis_table: list[Line]) -> str:
    input_index = 0
    table_position = 0
    stack_list = []
    table_lookup = {entry.number: entry for entry in analysis_table}

    while input_index < len(input_sequence):
        if table_position not in table_lookup:
            return f"Error: Invalid position {table_position}"

        current_entry = table_lookup[table_position]
        current_symbol = input_sequence[input_index]

        if current_symbol not in current_entry.first_set:
            if current_entry.error:
                return f"Error at index {input_index}: '{current_symbol}' not in {current_entry.first_set}"
            else:
                table_position += 1
                continue

        if current_entry.end:
            return "Ok" if input_index == len(input_sequence) - 1 else "Error: Unexpected EOL"

        if current_entry.shift:
            input_index += 1
        if current_entry.stack:
            stack_list.append(table_position + 1)
        if current_entry.pointer:
            table_position = current_entry.pointer
        elif stack_list:
            table_position = stack_list.pop()
        else:
            return f"Error at index {input_index}: No valid pointer"

    return "Error: Incomplete processing (No EOL)"
