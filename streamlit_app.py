import streamlit as st
import pandas as pd
import altair as alt

from map import create_map
from airdata import AirData
from utils import parse_time, parse_time_hms

ad = AirData()
flight_df = ad.get_flights_df()


map_air = create_map(flight_df)


st.altair_chart(map_air)

option = st.selectbox("Which flight number are you looking into?",
                        flight_df['number'])
# Get the corresponding flight row in the dataframe
option_row = flight_df[flight_df['number'] == option]
option_id = option_row.id.values[0]
option_detail = ad.get_flight_details(option_id)
option_time = option_detail['time']


# Display scheduled and actual time for departual and arrival using metric
col1, col2 = st.columns(2)
col1.metric("Scheduled departure time", 
            parse_time(option_time['scheduled']['departure']))

depart_delta = option_time['real']['departure'] - option_time['scheduled']['departure']
col2.metric("Actual departure time", 
            parse_time(option_time['real']['departure']),
            parse_time_hms(depart_delta),
            delta_color='inverse')


col3, col4 = st.columns(2)
col3.metric("Scheduled arrival time", parse_time(option_time['scheduled']['arrival']))
col4.metric("Actual arrival time", parse_time(option_time['real']['arrival']))


# details['time']['scheduled']['arrival']
# value = datetime.datetime.fromtimestamp(temp)
# value.strftime('%Y-%m-%d %H:%M:%S')


# Add a most delayed visualization (red flag), also shown in network graph?

# Add aircraft, speed, scheduled time...


