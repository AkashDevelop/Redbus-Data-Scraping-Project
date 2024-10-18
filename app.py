import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import plotly.express as px
import plotly.graph_objs as go

# Database connection details
user = 'root'
password = 'Hotwater&01'
host = 'localhost'
database = 'Red_bus_project'

# Create a connection to the MySQL database
engine = create_engine(f'mysql+mysqlconnector://{user}:{password}@{host}/{database}')

# Custom styles for the Streamlit app
st.markdown(
    """
    <style>
        body {
            background-color: #F0F4F8;  /* Soft light blue */
            font-family: 'Arial', sans-serif; /* Changed font to Arial */
        }
        h1 {
            text-align: center;
            color: #E92421; /* Red color */
            font-size: 48px; /* Adjusted font size */
            margin: 20px 0; /* Added margin for spacing */
            font-weight: bold; /* Bold font */
        }
        .header-home {
            font-size: 42px; /* Increased size for Home */
            color: #E92421; /* Red color */
            font-weight: bold; /* Bold font */
        }
        .header-filter {
            font-size: 36px; /* Increased size for Filter Buses */
            color: #E92421; /* Red color */
            font-weight: bold; /* Bold font */
        }
        .header-help {
            font-size: 36px; /* Increased size for Help */
            color: #E92421; /* Red color */
            font-weight: bold; /* Bold font */
        }

        .emoji-rating {
            display: flex;
            justify-content: center;
            margin-bottom: 10px;
        }
        .emoji {
            font-size: 30px; /* Size of emojis */
            cursor: pointer;
            margin: 0 5px; /* Spacing between emojis */
        }
        .collapsible {
            cursor: pointer;
            padding: 10px;
            border: 1px solid #E92421;
            background-color: #F0F4F8;
            margin: 10px 0;
            border-radius: 5px;
        }
        .content {
            display: none;
            padding: 10px;
            border: 1px solid #E92421;
            border-radius: 5px;
        }
        .image-caption {
            text-align: center; /* Centered caption */
            font-size: 20px; /* Font size for caption */
            color: #4a4a4a; /* Dark gray color for caption */
            margin-top: 10px; /* Spacing above caption */
            font-weight: normal; /* Normal font weight */
        }
        .welcome {
            text-align: center; /* Centered heading */
            font-size: 36px; /* Font size for welcome message */
            color: #E92421; /* Red color for heading */
            margin-bottom: 10px; /* Margin for spacing */
            font-weight: bold; /* Bold font for emphasis */
        }
        .filter-header {
            font-size: 24px; /* Font size for filter headers */
            color: #E92421; /* Red color for headers */
            font-weight: bold; /* Bold font */
            margin-bottom: 5px; /* Reduced margin for spacing */
        }
        .filter-label {
            font-size: 18px; /* Font size for filter labels */
            color: #4a4a4a; /* Dark gray color for labels */
            margin: 3px 0; /* Reduced margin for consistent spacing */
            font-weight: bold; /* Bold font for emphasis */
        }
        .filter-section {
            margin-bottom: 8px; /* Reduced margin for consistent spacing */
        }
        .input-text, .select-box, .slider {
            border: 1px solid #E92421; /* Red border for inputs */
            border-radius: 5px; /* Rounded corners */
            padding: 8px; /* Padding for inputs */
            font-size: 16px; /* Font size for inputs */
            width: 100%; /* Full width */
            margin-top: 3px; /* Margin to reduce space between label and input */
        }
    </style>
    """, unsafe_allow_html=True
)

tab1, tab2, tab3 = st.tabs(["Home", "Filter Buses", "Help"])

# Home Tab
with tab1:
    st.markdown("<h1 class='header-home'>Home</h1>", unsafe_allow_html=True)
    st.markdown("<h2 class='welcome'>Welcome to Redbus</h2>", unsafe_allow_html=True)
    st.image(r'C:\Users\admin\Downloads\misprojectredbus-140810140808-phpapp01-thumbnail.webp', use_column_width='400', caption="")
    st.markdown("<p class='image-caption'>Find Your Ideal Bus Route!</p>", unsafe_allow_html=True)

    # Emoji Rating System
    st.markdown("<h3>Rate Your Experience:</h3>", unsafe_allow_html=True)
    emoji_rating = st.columns(5)
    emojis = ['😀', '😃', '😄', '😅', '😞']
    selected_emoji = st.session_state.get('selected_emoji', None)

    for emoji in emojis:
        if emoji_rating[emojis.index(emoji)].button(emoji):
            selected_emoji = emoji
            st.session_state.selected_emoji = selected_emoji

    if selected_emoji:
        st.write(f"You selected: {selected_emoji}")

    # Recommendation Bot
    st.markdown("<h3>Need a Recommendation?</h3>", unsafe_allow_html=True)
    user_query = st.text_input("Ask for a bus recommendation...")
    if user_query:
        st.write("Recommendation Bot: Based on your query, we suggest checking out the bus options!")

# Filter Buses Tab
with tab2:
    selected_star_rating = st.sidebar.radio("Select Star Rating:", [1, 2, 3, 4, 5], key="unique_star_rating")
    feedback = st.sidebar.text_area("Leave your feedback:", placeholder="Your comments...")

    st.sidebar.write(f"You selected: {selected_star_rating} star{'s' if selected_star_rating > 1 else ''}")
    st.sidebar.write(f"Feedback: {feedback}")

    query = "SELECT * FROM bus_routes"
    try:
        df = pd.read_sql(query, engine)
        df['price'] = pd.to_numeric(df['price'], errors='coerce')
        df['seat_availability'] = pd.to_numeric(df['seat_availability'], errors='coerce')  # Ensure seat_availability is numeric

        st.sidebar.header("Filters")
        st.sidebar.markdown("<h2 class='filter-header'>Filter Options</h2>", unsafe_allow_html=True)

        # Starting Point
        starting_point = st.sidebar.text_input('Starting Point:', '', placeholder="Enter starting point...")

        # Destination
        destination = st.sidebar.text_input('Destination:', '', placeholder="Enter destination...")

        df_filtered = df.copy()
        if starting_point and destination:
            df_filtered = df_filtered[
                df_filtered['route_name'].str.contains(starting_point, case=False, na=False) & 
                df_filtered['route_name'].str.contains(destination, case=False, na=False)
            ]

        # Bus Type
        bus_types = df['bus_type'].unique() 
        selected_bus_type = st.sidebar.selectbox('Select Bus Type:', ['All'] + list(bus_types))

        # Price Range
        min_price, max_price = st.sidebar.slider('Select Price Range:', 
                                                  float(df['price'].min()), 
                                                  float(df['price'].max()), 
                                                  (float(df['price'].min()), float(df['price'].max())))

        if selected_bus_type != 'All':
            df_filtered = df_filtered[df_filtered['bus_type'] == selected_bus_type]

        df_filtered = df_filtered[(df_filtered['price'] >= min_price) & (df_filtered['price'] <= max_price)]
        df_filtered = df_filtered[df_filtered['star_rating'] >= selected_star_rating]

        st.write("Filtered Bus Data:", df_filtered)

        if not df_filtered.empty:
            best_routes = df_filtered.sort_values(by=['star_rating', 'price'], ascending=[False, True]).head(3)
            st.subheader("Top 3 Recommended Routes")
            st.dataframe(best_routes)

            # Bar chart for top routes
            fig = px.bar(best_routes, x='route_name', y='price', title='Top 3 Recommended Routes')
            st.plotly_chart(fig)

            # Bus Availability Heatmap
            heatmap_data = df_filtered.pivot_table(index='route_name', columns='bus_type', values='seat_availability', fill_value=0)


    except Exception as e:
        st.error(f"An error occurred while fetching data: {e}")

# Help Tab
with tab3:
    st.markdown("<h1 class='header-help'>Help</h1>", unsafe_allow_html=True)
    st.write("- This application helps you find and filter bus routes based on your preferences.")
    st.write("- Provide feedback on your experience using the feedback section.")
    st.write("- For any questions, feel free to reach out to support@redbus.com")
    
