import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import plotly.express as px
from datetime import time
import folium
from streamlit_folium import st_folium

user = 'root'
password = 'Hotwater&01'
host = 'localhost'
database = 'Red_bus_project'

engine = create_engine(f'mysql+mysqlconnector://{user}:{password}@{host}/{database}')

st.markdown(
    """
    <style>
        body {
            background-color: #F7F9FC;  /* Light, soft background for the entire app */
            color: #333333;  /* Dark text color for better readability */
            font-family: 'Arial', sans-serif;  /* Font style */
        }
        h1 {
            text-align: center;
            color: #005f73;  /* Dark teal color for headers */
            font-size: 48px;
            margin: 20px 0;
            font-weight: bold;
        }
        .header-home, .header-filter, .header-help {
            font-size: 36px;
            color: #005f73;  /* Dark teal for headers */
            font-weight: bold;
            font-family: 'Times New Roman', Times, serif;  /* Font change for header */
        }
        .welcome {
            text-align: center;
            font-size: 36px;
            color: #005f73;  /* Dark teal for headers */
            font-weight: bold;
            margin-bottom: 10px;
        }
        .image-caption {
            text-align: center;
            font-size: 20px;
            color: #555555;  /* Soft gray for captions */
            margin-top: 10px;
            font-weight: normal;
        }
        .stTextInput, .stTextArea, .stSelectbox {
            background-color: #FFFFFF;  /* White background for input fields */
            color: #333333;  /* Dark text color */
            border: 1px solid #B0B0B0;  /* Light gray border for input fields */
            border-radius: 5px;  /* Rounded corners */
            transition: border-color 0.3s;  /* Smooth border transition */
        }
        .stTextInput:focus, .stTextArea:focus {
            border-color: #005f73;  /* Dark teal border on focus */
        }
        /* Style for the filter column names */
        .filter-column-name {
            font-family: 'Times New Roman', Times, serif;  /* Font for column names */
            font-size: 18px;  /* Font size for column names */
            color: #003d5b;  /* Dark blue color for professionalism */
            font-weight: bold;  /* Bold text */
            margin-bottom: 5px;  /* Space below each column name */
        }
        /* Style for the Submit button */
        .submit-button {
            background-color: #E92421;  /* Red color for the button */
            text-align: center;  /* Center text */
            display: block;  /* Make it a block element to center */
            font-size: 14px;  /* Smaller font size */
            margin: 10px auto;  /* Center margin */
            padding: 8px 16px;  /* Padding for the button */
            border-radius: 4px;  /* Slightly rounded corners */
            cursor: pointer;  /* Pointer cursor on hover */
        }
        .submit-button:hover {
            background-color: #c72c2a;  /* Darker red on hover */
        }
        /* Style for data frames and other components */
        .stDataFrame {
            background-color: #FFFFFF;  /* White background for data frames */
            color: #333333;  /* Dark text color in tables */
            border-radius: 8px;  /* Rounded corners for tables */

            .filtered-data-header {
            font-size: 24px;  /* Font size for the header */
            color: #005f73;  /* Professional color for the header */
            margin-top: 20px;  /* Space above the header */
            margin-bottom: 10px;  /* Space below the header */
            font-weight: normal;  /* Normal font weight */
        
        }
        /* Responsive adjustments */
        @media (max-width: 600px) {
            h1 {
                font-size: 32px;  /* Smaller header on small screens */
            }
            .header-home, .header-filter, .header-help {
                font-size: 28px;  /* Smaller header for sections */
            }
            .welcome {
                font-size: 28px;  /* Smaller welcome text */
            }
        }
    </style>
    """, unsafe_allow_html=True
)

# Tabs for the different sections of the app
tab1, tab2, tab3 = st.tabs(["Home", "Filter Buses", "Help"])

with tab1:
    st.markdown("<h1 class='header-home'>Home</h1>", unsafe_allow_html=True)
    st.markdown("<h2 class='welcome'>India's No. 1 Online Bus Ticket Booking Site</h2>", unsafe_allow_html=True)
    st.image(r'C:\Users\admin\Downloads\misprojectredbus-140810140808-phpapp01-thumbnail.webp', use_column_width=True, caption="Find Your Ideal Bus Route!")

with tab2:
    st.markdown("<h1 class='header-filter'>Filter Buses</h1>", unsafe_allow_html=True)

    query = "SELECT * FROM bus_routes"

    try:
        # Load the data from the SQL database
        df = pd.read_sql(query, engine)

        # Ensure price and seat availability are numeric
        df['price'] = pd.to_numeric(df['price'], errors='coerce')
        df['seat_availability'] = pd.to_numeric(df['seat_availability'], errors='coerce')

        # Display filter selections
        st.write("Filter Inputs:")

        st.markdown("<div class='filter-column-name'>Select State:</div>", unsafe_allow_html=True)
        selected_state = st.selectbox('', ['All'] + list(df['state'].unique())) 
        
        # Filter by state if selected
        if selected_state != 'All':
            df = df[df['state'] == selected_state]
        
        st.markdown("<div class='filter-column-name'>Select Bus Route:</div>", unsafe_allow_html=True)
        selected_route = st.selectbox('', df['route_name'].unique())  # No label for selectbox

        st.markdown("<div class='filter-column-name'>Select Maximum Star Rating:</div>", unsafe_allow_html=True)
        selected_star_rating = st.slider('', 1, 5, 3)  # No label for slider

        # Display selected filter values
        st.write(f"Selected Filters - Route: {selected_route}, State: {selected_state}, Star Rating: {selected_star_rating}")

        # Updated Bus Type Filter with specified options
        bus_type_options = ['All', 'A/C Sleeper (2+1)', 'NON A/C Sleeper (2+1)', 'Non A/C Seater / Sleeper (2+1)']
        st.markdown("<div class='filter-column-name'>Select Bus Type:</div>", unsafe_allow_html=True)
        selected_bus_type = st.selectbox('', bus_type_options) 

        # Seat Availability Filters
        available_seats = st.checkbox("Available Seats Only")
        sleeper_ac_seats = st.checkbox("Sleeper AC Seat Availability")

        # Price Range Filter
        st.markdown("<div class='filter-column-name'>Select Price Range:</div>", unsafe_allow_html=True)
        min_price, max_price = st.slider('', 
                                           float(df['price'].min()), 
                                           float(df['price'].max()), 
                                           (float(df['price'].min()), float(df['price'].max())))

        # Base query and parameters
        base_query = """
                SELECT route_name,route_link,bus_name,bus_type,departure_time,arrival_time,duration,seat_availability,price,star_rating 
                FROM bus_routes 
                WHERE route_name = %s 
                AND star_rating <= %s 
                AND price BETWEEN %s AND %s
            """

        # Add conditions based on user selections
        params = [selected_route, selected_star_rating, min_price, max_price]


        if available_seats:
            base_query += " AND seat_availability > 0"
        if sleeper_ac_seats:
            base_query += " AND bus_type LIKE '%Sleeper AC%'"

        df_filtered = pd.read_sql(base_query, engine, params=tuple(params))

        if selected_bus_type != 'All':
            df_filtered = df_filtered[df_filtered['bus_type'] == selected_bus_type]

        # Display Filtered Data
        st.markdown("<div class='filtered-data-header'>Filtered Bus Data:</div>", unsafe_allow_html=True)

        st.write("", df_filtered)

        # Display Top 3 Routes if available
        if not df_filtered.empty:
            best_routes = df_filtered.sort_values(by=['star_rating', 'price'], ascending=[False, True]).head(3)
            st.subheader("Top 3 Recommended Routes")
            st.dataframe(best_routes)

        else:
            st.warning("No buses found with the selected filters.")

    except Exception as e:
        st.error(f"An error occurred while fetching data: {e}")

# Assuming you have a Streamlit tab structure already in place
with tab3:
    st.markdown("<h1 class='header-help'>RedBus Help 📍</h1>", unsafe_allow_html=True)

    # Overview
    st.write("- This application helps you find and filter bus routes based on your preferences.")

    # FAQ Section
    st.markdown("<h2>Frequently Asked Questions (FAQ)</h2>", unsafe_allow_html=True)
    st.write("1. **How do I book a bus?**")
    st.write("   - To book a bus, select your route, choose a bus, and follow the prompts to complete your booking.")
    st.write("2. **What should I do if I encounter a problem?**")
    st.write("   - Please check our troubleshooting tips or contact support.")

    # User Guide
    st.markdown("<h2>User Guide</h2>", unsafe_allow_html=True)
    st.write("For detailed instructions on using the app, please refer to our [User Guide](https://www.redbus.in/info/faq).")

    # Feedback Section
    st.markdown("<h2>Feedback</h2>", unsafe_allow_html=True)
    st.write("We value your feedback! Please let us know about your experience using the feedback section .")

    # Contact Us
    st.markdown("<h2>Contact Us</h2>", unsafe_allow_html=True)
    st.write("For any questions, feel free to reach out to [support@redbus.com](mailto:support@redbus.com) or call us at +919945600000.")
    st.write("Our support team is available from 9 AM to 6 PM, Monday to Friday.")



# Sidebar feedback form
st.sidebar.header("Feedback Form")

# Rate Your Experience
st.sidebar.markdown("<h3>Rate Your Experience:</h3>", unsafe_allow_html=True)
emoji_rating = st.sidebar.columns(5)
emojis = ['😡', '💀', '🙏🏻', '😊', '😍']
selected_emoji = st.session_state.get('selected_emoji', None)

for emoji in emojis:
    if emoji_rating[emojis.index(emoji)].button(emoji):
        selected_emoji = emoji
        st.session_state.selected_emoji = selected_emoji

if selected_emoji:
    st.sidebar.write(f"You selected: {selected_emoji}")

    def create_static_map():
        lat, lon = 11.0168, 76.9558
        static_map = folium.Map(location=[lat, lon], zoom_start=12)
        folium.Marker(
             [lat, lon],
               tooltip="Default Location: Coimbatore",
               icon=folium.Icon(color="blue")
          ).add_to(static_map)
        return static_map

# Display the map in Streamlit
    st.subheader("Redbus Location Map")
    static_map = create_static_map()
    st_folium(static_map, width=700, height=300)

# Need a Recommendation?
st.sidebar.markdown("<h3>Need a Recommendation?</h3>", unsafe_allow_html=True)

# Leave your feedback
feedback = st.sidebar.text_area("Leave your feedback:", placeholder="Your comments...", height=40)

# Upload a screenshot
uploaded_file = st.sidebar.file_uploader("Upload a screenshot (if applicable):", type=["png", "jpg", "jpeg"])
if uploaded_file:
    st.sidebar.success("File uploaded successfully!")

# Submit Button
if st.sidebar.button("Submit Feedback", key="submit_button"):
    if feedback or selected_emoji or uploaded_file:
        st.sidebar.success("Thank you for your feedback! We appreciate your input.")
    else:
        st.sidebar.warning("Please provide some feedback before submitting.")

