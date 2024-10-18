import pandas as pd
import glob


file_path = r'E:\Red bus Project\merge_10_state'

# List to store data from each CSV file
dataframe = []

# Load all CSV files from the specified folder
all_csv = glob.glob(file_path + "/*.csv")


for file in all_csv:
    df = pd.read_csv(file)
    df.dropna(axis=1, how='all', inplace=True)  
    dataframe.append(df)


merge_data_10 = pd.concat(dataframe, ignore_index=True)


merged_data_cleaned = merge_data_10.drop_duplicates().copy()


merged_data_cleaned = merged_data_cleaned.dropna(subset=[
    'Bus Name', 'Bus Type', 'Departure Time', 'Arrival Time', 'Duration', 'Seat Availability'])


merged_data_cleaned.fillna(value={
    'Route Name': 'N/A',
    'Route Link': 'N/A',
    'Price': '0',  
    'Star Rating': '0'  
}, inplace=True)


merged_data_cleaned['Price'] = merged_data_cleaned['Price'].replace({'INR ': '', ',': ''}, regex=True).astype(float)


merged_data_cleaned.to_csv('cleaned_merge_data_10.csv', index=False)

print('All CSV files successfully merged, cleaned, and saved into "cleaned_merge_data_10.csv"')

# DATA EXPLORATION

import pandas as pd
merged_data_cleaned = pd.read_csv('cleaned_merge_data_10.csv')

# Show the first 5 rows of the cleaned data
print(merged_data_cleaned.head())


print(merged_data_cleaned.info())


print(merged_data_cleaned.isnull().sum())

