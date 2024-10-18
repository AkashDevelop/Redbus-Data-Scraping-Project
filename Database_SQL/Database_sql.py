import pandas as pd
from sqlalchemy import create_engine

# Load the CSV file
cleaned_data = pd.read_csv(r"E:\Red bus Project\cleaned_merge_data\cleaned_merge_data_10.csv")

cleaned_data.rename(columns={
    'Route Name': 'Route_Name',
    'Route Link': 'Route_Link',
    'Bus Name': 'Bus_Name',
    'Bus Type': 'Bus_Type',
    'Departure Time': 'Departure_Time',
    'Arrival Time': 'Arrival_Time',
    'Duration': 'Duration',
    'Seat Availability': 'Seat_Availability',
    'Price': 'Price',
    'Star Rating': 'Star_Rating'
}, inplace=True)

engine = create_engine("mysql+mysqlconnector://root:Hotwater&01@localhost/Red_bus_project")

# Insert the data into the bus_routes table
cleaned_data.to_sql('bus_routes', con=engine, if_exists='append', index=False)

print( "Data inserted successfully into sql table")
