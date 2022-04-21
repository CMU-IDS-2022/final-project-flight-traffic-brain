import streamlit as st
import pandas as pd
import altair as alt

from map import create_map
from airdata import AirData
from utils import parse_time, parse_time_hms


# Getting data ready
@st.cache
def get_data():
    ad = AirData()
    flight_df = ad.get_flights_df()
    return ad, flight_df


ad, flight_df = get_data()


# ------------ Map starts ---------------------

with st.sidebar.expander("Analysis for flights/airports"):
    st.write("This is an analysis tool from the perspective of flights or airports")
    to_show = st.selectbox("Data to look at", ["flight", "airport"])
    if to_show == "flight":
        field = st.selectbox("Variable of interest", ["heading", "altitude", "ground_speed"])
    else:
        field = st.selectbox("Variable of interest", ["origin_airport_iata", "destination_airport_iata"])

map_air = create_map(flight_df, field, to_show)

st.altair_chart(map_air)

# ------------ Map ends ---------------------


# ------------ Flight time starts ---------------------


option = st.selectbox("Which flight number are you looking into?",
                        flight_df['number'].sort_values())
# Get the corresponding flight row in the dataframe
option_row = flight_df[flight_df['number'] == option]
option_id = option_row.id.values[0]
option_detail = ad.get_flight_details(option_id)
option_time = option_detail['time']


# Display scheduled and actual time for departual and arrival using metric
col1, col2 = st.columns(2)
col1.metric("Scheduled departure time", 
            parse_time(option_time['scheduled']['departure']))

if option_time['real']['departure'] and option_time['scheduled']['departure']:
    depart_delta = option_time['real']['departure'] - option_time['scheduled']['departure']
else:
    depart_delta = None
col2.metric("Actual departure time", 
            parse_time(option_time['real']['departure']),
            parse_time_hms(depart_delta),
            delta_color='inverse')


col3, col4 = st.columns(2)
col3.metric("Scheduled arrival time", parse_time(option_time['scheduled']['arrival']))
arrival_time = option_time['real']['arrival']
if not arrival_time:
    arrival_time = option_time['estimated']['arrival']
col4.metric("Estimated/Actual arrival time", parse_time(arrival_time))


# ------------ Flight time ends ---------------------


# Note that some flights are not displayed due to... so the number of routes
# may appear larger than...


