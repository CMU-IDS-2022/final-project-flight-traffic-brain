import streamlit as st
import pandas as pd
import altair as alt

from map import create_map

map_air = create_map()


st.altair_chart(map_air)


# details['time']['scheduled']['arrival']
# value = datetime.datetime.fromtimestamp(temp)
# value.strftime('%Y-%m-%d %H:%M:%S')


# Add a most delayed visualization (red flag), also shown in network graph?

# Add aircraft, speed, scheduled time...


