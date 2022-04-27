from FlightRadar24.api import FlightRadar24API
import pandas as pd
import streamlit as st


st_title = st.empty()
st_progress_bar = st.empty()

class tqdm:
    def __init__(self, iterable, title=None):
        if title:
            st_title.write(title)
        self.prog_bar = st_progress_bar.progress(0)
        self.iterable = iterable
        self.length = len(iterable)
        self.i = 0

    def __iter__(self):
        for obj in self.iterable:
            yield obj
            self.i += 1
            current_prog = self.i / self.length
            self.prog_bar.progress(current_prog)




class AirData:
    '''
    This is a wrapper class to the FlightRadarAPI.
    '''
    def __init__(self) -> None:
        self.fr_api = FlightRadar24API()
        flights_all = self.fr_api.get_flights()


        # Read a dataframe that has only US airport data
        airport_df = pd.read_csv("airports.csv", usecols=['iata'])
        self.us_airport_iatas = set(airport_df['iata'].tolist())

        # Keep only the flights in the U.S
        self.flights = self._get_US_flights(flights_all)

    def get_flights(self):
        return self.flights

    def get_flights_df(self):
        flights_df = pd.DataFrame([ft.__dict__ for ft in self.flights])
        return flights_df

    def _get_US_flights(self, flights_all):
        flights_us = []
        for flight in flights_all:
            if flight.origin_airport_iata in self.us_airport_iatas \
                and flight.destination_airport_iata in self.us_airport_iatas:
                flights_us.append(flight)
        return flights_us

    def get_flight_details(self, flight_id):
        return self.fr_api.get_flight_details(flight_id)

    def add_time_to_df(self, flights_df):
        # Could take about 3 - 5 minutes
        flights_ids = flights_df['id']
        scheduled_depart = []
        scheduled_arrive = []
        real_depart = []
        real_arrive = []
        estimated_depart = []
        estimated_arrive = []
        eta = []
        delayed = []

        for fid in tqdm(flights_ids, title="Fetching new data"):
            detail = self.get_flight_details(fid)
            if type(detail) != dict: # errorenous return value: bytes class
                scheduled_depart.append(None)
                scheduled_arrive.append(None)
                real_depart.append(None)
                real_arrive.append(None)
                estimated_depart.append(None)
                estimated_arrive.append(None)
                eta.append(None)
                delayed.append(None)
                continue

            time_info = detail['time']
            
            scheduled_depart.append(time_info['scheduled']['departure'])
            scheduled_arrive.append(time_info['scheduled']['arrival'])
            real_depart.append(time_info['real']['departure'])
            real_arrive.append(time_info['real']['arrival'])
            estimated_depart.append(time_info['estimated']['departure'])
            estimated_arrive.append(time_info['estimated']['arrival'])
            eta.append(time_info['other']['eta'])

            # Delay or not?
            actual_arrival_time = time_info['real']['arrival']
            if not actual_arrival_time:
                actual_arrival_time = time_info['estimated']['arrival']
            scheduled_arrival_time = time_info['scheduled']['arrival']
            if actual_arrival_time and scheduled_arrival_time and actual_arrival_time > scheduled_arrival_time:
                delayed.append(True)
            else:
                delayed.append(False)

        flights_df['scheduled_depart'] = scheduled_depart
        flights_df['scheduled_arrive'] = scheduled_arrive
        flights_df['real_depart'] = real_depart
        flights_df['real_arrive'] = real_arrive
        flights_df['estimated_depart'] = estimated_depart
        flights_df['estimated_arrive'] = estimated_arrive
        flights_df['eta'] = eta
        flights_df['is_delay'] = delayed

        st_title.empty()
        st_progress_bar.empty()

        return flights_df


