import re
import pandas as pd

input_file = 'par_batch_results.txt'
output_file = 'par_batch_results.csv'

# Regular expressions to capture the data from the text file
patterns = {
    'Total Customers Generated': r'Total customers generated: (\d+)',
    'Total Customers Served': r'Total customers served: (\d+)',
    'Customers Left in Queue': r'Customers left in queue: (\d+)',
    'Average Wait Time': r'Average wait time for served customers: ([\d.]+)',
    'Maximum Wait Time': r'Maximum wait time: (\d+)',
    'Minimum Wait Time': r'Minimum wait time: (\d+)',
    'Average Queue Length': r'Average queue length: ([\d.]+)',
    'Max Queue Length': r'Max queue length: (\d+)',
    'Teller Utilization': r'Teller utilization: ([\d.]+)%'
}

# Function to parse the input file and return records as a list of dictionaries
def parse_input_file(input_file, patterns):
    records = []
    current_record = {}

    with open(input_file, 'r') as file:
        for line in file:
            for key, pattern in patterns.items():
                match = re.search(pattern, line)
                if match:
                    current_record[key] = float(match.group(1)) if '.' in match.group(1) else int(match.group(1))

            # If all fields are present, add the record to the list and reset
            if len(current_record) == len(patterns):
                records.append(current_record)
                current_record = {}

    return records

# Main logic to convert text data to CSV
def main():
    records = parse_input_file(input_file, patterns)
    
    if not records:
        print("No records found. Please check the input file.")
        return

    # Convert the list of records to a pandas DataFrame
    df = pd.DataFrame(records)

    # Save the DataFrame to a CSV file
    df.to_csv(output_file, index=False)
    print(f"Data has been converted and saved to '{output_file}'")

if __name__ == "__main__":
    main()
