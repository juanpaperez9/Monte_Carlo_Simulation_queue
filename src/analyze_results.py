# analyze_results.py
import pandas as pd
import matplotlib.pyplot as plt

data_file = 'par_batch_results.csv'

# Load the data from the CSV file
try:
    data = pd.read_csv(data_file)
except FileNotFoundError:
    print(f"Error: The file '{data_file}' was not found. Make sure to run the batch simulations and convert the results first.")
    exit()

# Check if data is empty
if data.empty:
    print("No valid data available for analysis.")
    exit()

# Print basic statistics
print("\nSummary Statistics:")
print(data.describe())

# Function to create histogram plots
def plot_histogram(data, column, xlabel, title, color='blue'):
    plt.figure(figsize=(10, 6))
    plt.hist(data[column], bins=20, color=color, alpha=0.7)
    plt.xlabel(xlabel)
    plt.ylabel('Frequency')
    plt.title(title)
    plt.grid(axis='y', linestyle='--', linewidth=0.5)
    plt.show()

# Function to create line plots
def plot_line(data, column, xlabel, ylabel, title, color='orange'):
    plt.figure(figsize=(10, 6))
    plt.plot(data[column], label=ylabel, color=color)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.legend()
    plt.grid(axis='y', linestyle='--', linewidth=0.5)
    plt.show()

# Wait Time Analysis
plot_histogram(data, 'Average Wait Time', 'Average Wait Time (minutes)', 'Distribution of Average Wait Times', color='blue')

# Queue Length Analysis
plot_line(data, 'Average Queue Length', 'Simulation Run', 'Queue Length', 'Average Queue Length Over Different Simulation Runs', color='orange')

# Teller Utilization Analysis
plot_histogram(data, 'Teller Utilization', 'Teller Utilization (%)', 'Teller Utilization Across Different Runs', color='green')

# Maximum Wait Time Analysis
plot_line(data, 'Maximum Wait Time', 'Simulation Run', 'Maximum Wait Time', 'Maximum Wait Time Across Different Simulation Runs', color='red')

# Execution Time Analysis
plot_histogram(data, 'Total Execution Time', 'Execution Time (seconds)', 'Distribution of Total Execution Time', color='purple')
