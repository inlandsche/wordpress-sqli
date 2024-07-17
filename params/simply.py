def process_file(input_file, output_file):
    # Read content from the input file
    with open(input_file, 'r') as file:
        lines = file.readlines()

    # Process each line
    processed_lines = []
    for i, line in enumerate(lines, start=1):
        # Calculate the line number with wrap-around at 30
        line_number = (i - 1) % 30 + 1
        
        # Add line number after the '*'
        if '*' in line:
            line = line.replace('*', f'*{line_number}', 1)
        processed_lines.append(line)

    # Write the processed content to the output file
    with open(output_file, 'w') as file:
        file.writelines(processed_lines)

# Input and output file paths
input_file = 'output.txt'
output_file = 'output-1.txt'

# Process the file
process_file(input_file, output_file)

# Optionally print the result
with open(output_file, 'r') as file:
    print(file.read())
