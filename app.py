
import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import plotly.express as px

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
            margin: 20px 0;
            font-weight: bold;
        }
        .header-home {
            font-size: 42px;
            color: #E92421;
            font-weight: bold;
        }
        .header-filter {
            font-size: 36px;
            color: #E92421;
            font-weight: bold;
        }
        .header-help {
            font-size: 36px;
            color: #E92421;
            font-weight: bold;
        }
        .welcome {
            text-align: center;
            font-size: 36px;
            color: #E92421;
            font-weight: bold;
            margin-bottom: 10px;
        }
        .emoji-rating {
            display: flex;
            justify-content: center;
            margin-bottom: 10px;
        }
        .emoji {
            font-size: 30px;
            cursor: pointer;
            margin: 0 5px;
        }
        .image-caption {
            text-align: center;
            font-size: 20px;
            color: #4a4a4a;
            margin-top: 10px;
            font-weight: normal;
        }
        .filter-header, .filter-label {
            color: #E92421;
            font-weight: bold;
        }
        .input-text, .select-box, .slider {
            border: 1px solid #E92421;
            border-radius: 5px;
            padding: 8px;
            font-size: 16px;
            width: 100%;
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

# Filter Buses Tab
with tab2:
    st.markdown("<h1 class='header-filter'>Filter Buses</h1>", unsafe_allow_html=True)

    query = "SELECT * FROM bus_routes"
    try:
        df = pd.read_sql(query, engine)
        df['price'] = pd.to_numeric(df['price'], errors='coerce')
        df['seat_availability'] = pd.to_numeric(df['seat_availability'], errors='coerce')  # Ensure seat_availability is numeric

        # State Filter
        states = df['state'].unique()
        selected_state = st.selectbox('Select State:', ['All'] + list(states))

        if selected_state != 'All':
            df = df[df['state'] == selected_state]

        # Bus Routes Filter (Dependent on State)
        filtered_routes = df['route_name'].unique()
        selected_route = st.selectbox("Select Bus Route", filtered_routes)

        # Bus Type Filter
        bus_types = df['bus_type'].unique()
        selected_bus_type = st.selectbox('Select Bus Type:', ['All'] + list(bus_types))

        # Star Rating Filter
        selected_star_rating = st.slider("Select Minimum Star Rating", 1, 5, 3)

        # Price Range Filter
        min_price, max_price = st.slider('Select Price Range:', 
                                         float(df['price'].min()), 
                                         float(df['price'].max()), 
                                         (float(df['price'].min()), float(df['price'].max())))

        # Apply Filters
        df_filtered = df[(df['route_name'] == selected_route) & 
                         (df['star_rating'] >= selected_star_rating)]

        if selected_bus_type != 'All':
            df_filtered = df_filtered[df_filtered['bus_type'] == selected_bus_type]

        df_filtered = df_filtered[(df_filtered['price'] >= min_price) & (df_filtered['price'] <= max_price)]

        st.write("Filtered Bus Data:", df_filtered)

        if not df_filtered.empty:
            best_routes = df_filtered.sort_values(by=['star_rating', 'price'], ascending=[False, True]).head(3)
            st.subheader("Top 3 Recommended Routes")
            st.dataframe(best_routes)

            # Bar chart for top routes
            fig = px.bar(best_routes, x='route_name', y='price', title='Top 3 Recommended Routes')
            st.plotly_chart(fig)

    except Exception as e:
        st.error(f"An error occurred while fetching data: {e}")

# Help Tab
with tab3:
    st.markdown("<h1 class='header-help'>Help</h1>", unsafe_allow_html=True)
    st.write("- This application helps you find and filter bus routes based on your preferences.")
    st.write("- Provide feedback on your experience using the feedback section.")
    st.markdown('''- For any questions, feel free to reach out to [support@redbus.com](https://www.redbus.in/info/contactus)''')


# Feedback Form in Sidebar
st.sidebar.header("Feedback Form")

# Rate Your Experience Section in Sidebar
st.sidebar.markdown("<h3>Rate Your Experience:</h3>", unsafe_allow_html=True)
emoji_rating = st.sidebar.columns(5)
emojis = ['😀', '😃', '😄', '😅', '😞']
selected_emoji = st.session_state.get('selected_emoji', None)

for emoji in emojis:
    if emoji_rating[emojis.index(emoji)].button(emoji):
        selected_emoji = emoji
        st.session_state.selected_emoji = selected_emoji

if selected_emoji:
    st.sidebar.write(f"You selected: {selected_emoji}")

# Need a Recommendation Section in Sidebar
st.sidebar.markdown("<h3>Need a Recommendation?</h3>", unsafe_allow_html=True)
user_query = st.sidebar.text_input("Ask for a bus recommendation...")
if user_query:
    st.sidebar.write("Recommendation Bot: Based on your query, we suggest checking out the bus options!")

# Feedback Text Area
feedback = st.sidebar.text_area("Leave your feedback:", placeholder="Your comments...")
st.sidebar.write(f"Feedback: {feedback}")
