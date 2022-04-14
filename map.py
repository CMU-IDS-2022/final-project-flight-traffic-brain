import altair as alt
from vega_datasets import data
import streamlit as st


# Adapt from: https://altair-viz.github.io/gallery/airport_connections.html

def get_static_data():
    # Get static data including airports, static flights, and the states in US
    airports = data.airports.url
    flights_airport = data.flights_airport.url
    states = alt.topo_feature(data.us_10m.url, feature="states")
    return airports, flights_airport, states


def mouse_selection():
    # Create mouseover selection
    select_city = alt.selection_single(
        on="mouseover", fields=["origin"], empty="none"
    )
    return select_city

def lookup(airports):
    # Define which attributes to lookup from airports.csv
    lookup_data = alt.LookupData(
        airports, key="iata", fields=["state", "latitude", "longitude"]
    )
    return lookup_data

def init_background(states):
    background = alt.Chart(states).mark_geoshape(
        fill="lightgreen",
        stroke="white"
    ).properties(
        width=750,
        height=500
    ).project("albersUsa")
    return background

def init_connections(flights_airport, lookup_data, select_city):
    connections = alt.Chart(flights_airport).mark_rule(opacity=0.35).encode(
        latitude="latitude:Q",
        longitude="longitude:Q",
        latitude2="lat2:Q",
        longitude2="lon2:Q"
    ).transform_lookup(
        lookup="origin",
        from_=lookup_data
    ).transform_lookup(
        lookup="destination",
        from_=lookup_data,
        as_=["state", "lat2", "lon2"]
    ).transform_filter(
        select_city
    )
    return connections



def init_airports(flights_airport, lookup_data, select_city):
    points = alt.Chart(flights_airport).mark_circle().encode(
        latitude="latitude:Q",
        longitude="longitude:Q",
        size=alt.Size("routes:Q", scale=alt.Scale(range=[0, 1000]), legend=None),
        order=alt.Order("routes:Q", sort="descending"),
        tooltip=["origin:N", "routes:Q"]
    ).transform_aggregate(
        routes="count()",
        groupby=["origin"]
    ).transform_lookup(
        lookup="origin",
        from_=lookup_data
    ).transform_filter(
        (alt.datum.state != "PR") & (alt.datum.state != "VI")
    ).add_selection(
        select_city
    )
    return points


def init_flights(flights):
    # brush = alt.selection(type='single') 
    # Note: interval selection directly on map is not feasible: https://github.com/altair-viz/altair/issues/1232
    interval = alt.selection(type='interval')
    # change scatter point size interactively?
    scatter = alt.Chart(flights).mark_point(size=2.0).encode(
        alt.X("latitude", scale=alt.Scale(zero=False)),
        alt.Y("longitude", scale=alt.Scale(zero=False)),
        color = alt.condition(interval, alt.value("purple"), alt.value("grey")),
        opacity = alt.condition(interval, alt.value(1), alt.value(0.2))
    ).add_selection(interval)

    hist = alt.Chart(flights).mark_bar(tooltip=True
            ).encode(
                    alt.X("ground_speed", bin=True),
                    alt.Y(aggregate="count", type='quantitative')
            ).transform_filter(interval)


    points = alt.Chart(flights).mark_square().encode(
        latitude="latitude:Q",
        longitude="longitude:Q",
        tooltip=["number:N", "origin_airport_iata:N", "destination_airport_iata:N"],
        color=alt.condition(interval, alt.value("red"), alt.value("grey"))
    )
    # todo: connect brush with extra flight information to display...
    return points, scatter, hist

@st.cache
def create_map(flight_df):
    '''
    flight_df: real time flight dataframe from AirData
    '''

    # Prepare data
    airports, flights_airport, states = get_static_data()
    lookup_data = lookup(airports)
    select_city = mouse_selection()

    
    # The map consists of background US map, connections between airports, 
    # airport points, and flight points
    background = init_background(states)
    connections = init_connections(flights_airport, lookup_data, select_city)
    airport_pts = init_airports(flights_airport, lookup_data, select_city)
    flights_pts, scatter, hist = init_flights(flight_df)

    map_view = alt.layer(background, connections, airport_pts, flights_pts)
    map_stat_view = alt.hconcat(scatter, hist)
    map_airport = alt.vconcat(map_view, map_stat_view).configure_view(stroke=None)
    return map_airport

