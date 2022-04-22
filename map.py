import altair as alt
from vega_datasets import data
import streamlit as st


# Reference: https://altair-viz.github.io/gallery/airport_connections.html

def get_static_data():
    # Get static data including airports, static flights, and the states in US
    airports = data.airports.url
    flights_airport = data.flights_airport.url
    states = alt.topo_feature(data.us_10m.url, feature="states")
    return airports, flights_airport, states



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

def init_airport_connect_airport(flights_airport, lookup_data, select_city):
    # Not used
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


def init_flight_connect_airport(flight_df, lookup_data, select_flight, select_airport):
    flights_from = alt.Chart(flight_df).mark_rule(opacity=0.35).encode(
        latitude="latitude:Q",
        longitude="longitude:Q",
        latitude2="port_latitude:Q",
        longitude2="port_longitude:Q",
        color = alt.value("#8c564b")
    ).transform_lookup(
        lookup="origin_airport_iata",
        from_=lookup_data,
        as_=["state", "port_latitude", "port_longitude"]
    ).transform_filter(
        select_flight
    )

    # flights_to = alt.Chart(flight_df).mark_rule(opacity=0.35).encode(
    #     latitude="latitude:Q",
    #     longitude="longitude:Q",
    #     latitude2="port_latitude:Q",
    #     longitude2="port_longitude:Q",
    #     color = alt.value("purple")
    # ).transform_lookup(
    #     lookup="destination_airport_iata",
    #     from_=lookup_data,
    #     as_=["state", "port_latitude", "port_longitude"]
    # ).transform_filter(
    #     select_flight
    # ).transform_filter(
    #     select_airport
    # )
    return flights_from


def init_airport_connect_flight(flight_df, lookup_data, select_airport):
    airports_to = alt.Chart(flight_df).mark_rule().encode(
        latitude="port_latitude:Q",
        longitude="port_longitude:Q",
        latitude2="latitude:Q",
        longitude2="longitude:Q",
        color = alt.value("black")
    ).transform_lookup(
        lookup="destination_airport_iata",
        from_=lookup_data,
        as_=["state", "port_latitude", "port_longitude"]
    ).transform_filter(
        select_airport
    )
    return airports_to

def init_airports(flight_df, lookup_data, select_city, interval):

    airport_df = flight_df[["origin_airport_iata", "destination_airport_iata"]]

    points = alt.Chart(airport_df).mark_circle().encode(
        latitude="port_latitude:Q",
        longitude="port_longitude:Q",
        size=alt.Size("dest_routes:Q", scale=alt.Scale(range=[100,400]), legend=None),
        order=alt.Order("dest_routes:Q", sort="descending"),
        color=alt.condition(interval, alt.value("blue"), alt.value("grey")),
        tooltip=["destination_airport_iata:N", "dest_routes:Q"]
    ).transform_aggregate(
        dest_routes="count()",
        groupby=["destination_airport_iata"]
    ).transform_lookup(
        lookup="destination_airport_iata",
        from_=lookup_data,
        as_=["state", "port_latitude", "port_longitude"]
    ).transform_filter(
        (alt.datum.state != "PR") & (alt.datum.state != "VI")
    ).add_selection(
        select_city
    )
    return points


def init_flights(flight_df, select_flight, interval):
    points = alt.Chart(flight_df).mark_square().encode(
        latitude="latitude:Q",
        longitude="longitude:Q",
        tooltip=["number:N", "origin_airport_iata:N", "destination_airport_iata:N"],
        color=alt.condition(interval, alt.value("red"), alt.value("grey")),
    ).add_selection(select_flight)
    # todo: connect brush with extra flight information to display...
    # return points, scatter, hist
    return points


def init_scatter_and_hist(flight_df, field, to_show, lookup_data):
    if to_show == "flight":
        # Note: interval selection directly on map is not feasible: https://github.com/altair-viz/altair/issues/1232
        interval = alt.selection(type='interval')
        scatter = alt.Chart(flight_df).mark_point(size=2.0).encode(
            alt.X("latitude", scale=alt.Scale(zero=False)),
            alt.Y("longitude", scale=alt.Scale(zero=False)),
            color = alt.condition(interval, alt.value("purple"), alt.value("grey")),
            opacity = alt.condition(interval, alt.value(1), alt.value(0.2))
        ).add_selection(interval)
        hist = alt.Chart(flight_df).mark_bar(tooltip=True
                ).encode(
                        alt.X(field, bin=True),
                        alt.Y(aggregate="count", type='quantitative')
                ).transform_filter(interval)
    else: # "airport"
        interval = alt.selection(type='interval', empty='none')
        scatter = alt.Chart(flight_df).mark_point(size=2.0).encode(
                alt.X("port_latitude:Q", scale=alt.Scale(zero=False)),
                alt.Y("port_longitude:Q", scale=alt.Scale(zero=False)),
                color = alt.condition(interval, alt.value("purple"), alt.value("grey")),
                opacity = alt.condition(interval, alt.value(1), alt.value(0.2))
                ).transform_lookup(
                    lookup=field,
                    from_=lookup_data,
                    as_=["state", "port_latitude", "port_longitude"]
                ).add_selection(interval)
        # Actually a bar chart
        hist = alt.Chart(flight_df).mark_bar(tooltip=True
                ).encode(
                        x = field,
                        y = 'count()'
                ).transform_lookup(
                    lookup=field,
                    from_=lookup_data,
                    as_=["state", "port_latitude", "port_longitude"]
                ).transform_filter(interval)
    return scatter, hist, interval

# @st.cache
def create_map(flight_df, field, to_show):
    '''
    flight_df: real time flight dataframe from AirData
    '''

    # Prepare data
    airports, flights_airport, states = get_static_data()
    lookup_data = lookup(airports)
    select_flight = alt.selection_single(
        on="mouseover", fields = ['id'], empty="none"
    )
    select_airport = alt.selection_single(
        on="mouseover", fields = ["destination_airport_iata"], empty="none"
    )

    
    # The map consists of background US map, connections between airports, 
    # airport points, and flight points
    background = init_background(states)
    # airport_connections = init_airport_connect_airport(flights_airport, lookup_data, select_city)

    scatter, hist, interval = init_scatter_and_hist(flight_df, field, to_show, lookup_data)
    flights_pts = init_flights(flight_df, select_flight, interval)
    airport_pts = init_airports(flight_df, lookup_data, select_airport, interval)
    flight_from = init_flight_connect_airport(flight_df, lookup_data, select_flight, select_airport)
    airports_to = init_airport_connect_flight(flight_df, lookup_data, select_airport)

    map_view = alt.layer(background, flight_from, airports_to,
                            airport_pts, flights_pts)
    map_stat_view = alt.hconcat(scatter, hist)
    map_airport = alt.vconcat(map_view, map_stat_view).configure_view(stroke=None)
    return map_airport

