from FlightRadar24.api import FlightRadar24API
import pandas as pd


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

        for fid in flights_ids:
            detail = self.get_flight_details(fid)
            time_info = detail['time']
            
            scheduled_depart.append(time_info['scheduled']['departure'])
            scheduled_arrive.append(time_info['scheduled']['arrival'])
            real_depart.append(time_info['real']['departure'])
            real_arrive.append(time_info['real']['arrival'])
            estimated_depart.append(time_info['estimated']['departure'])
            estimated_arrive.append(time_info['estimated']['arrival'])
            eta.append(time_info['other']['eta'])

        flights_df['scheduled_depart'] = scheduled_depart
        flights_df['scheduled_arrive'] = scheduled_arrive
        flights_df['real_depart'] = real_depart
        flights_df['real_arrive'] = real_arrive
        flights_df['estimated_depart'] = estimated_depart
        flights_df['estimated_arrive'] = estimated_arrive
        flights_df['eta'] = eta

        return flights_df


