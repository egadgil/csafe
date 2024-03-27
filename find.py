import pandas as pd

# Read the CSV file into a DataFrame
data = pd.read_csv("results-viz.csv")

# Get the number of unique values in the 'extractor' column
unique_values_count = data['extractor'].unique()

print(unique_values_count)
