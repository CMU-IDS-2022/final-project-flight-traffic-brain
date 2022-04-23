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



## Prepare data
# load in files
origin = pickle.load(open('OriginState.sav','rb'))
dest = pickle.load(open('DestState.sav','rb'))
air = pickle.load(open('AirlineCompany.sav','rb'))
miles_dic = pickle.load(open('miles_dic.sav','rb'))
quarter_dic= {'Spring':'Q1','Summer':'Q2','Fall':'Q3','Winter':'Q4'}
df_viz = pd.read_csv('df_viz.csv').iloc[:,:]

# fit the prediction model, get mean and prediction interval
def get_pi(X):
    rb_lower = pickle.load(open(f'D:\\Users\\tinaf\\Dropbox\\CMU\\1-Course-Related\\##S22##\\05839_IDS\\final_project\\airline_2018_us\\gb_lower.sav', 'rb'))
    rb_mean = pickle.load(open(f'D:\\Users\\tinaf\\Dropbox\\CMU\\1-Course-Related\\##S22##\\05839_IDS\\final_project\\airline_2018_us\\gb_mean.sav', 'rb'))
    rb_upper = pickle.load(open(f'D:\\Users\\tinaf\\Dropbox\\CMU\\1-Course-Related\\##S22##\\05839_IDS\\final_project\\airline_2018_us\\gb_upper.sav', 'rb'))
    lb = rb_lower.predict(X)
    mean = rb_mean.predict(X)
    ub = rb_upper.predict(X)
    return (round(np.exp(lb[0]),2), round(np.exp(mean[0]),2), round(np.exp(ub[0]),2))


# load data for non ML visual
def load_data():
    return pd.read_csv('D:\\Users\\tinaf\\Dropbox\\CMU\\1-Course-Related\\##S22##\\05839_IDS\\final_project\\airline_2018_us\\train_viz.csv').iloc[:,:]
    

# visual for price comparison
@st.cache
def get_slice_ogstate(df, ogstate=None):
    labels = pd.Series([1] * len(df), index=df.index)
    labels &= df['OriginState'] == ogstate
    return labels


def get_slice_destate(df, destate=None):
    labels = pd.Series([1] * len(df), index=df.index)
    labels &= df['DestState'] == destate
    return labels


def get_slice_ogcity(df, ogcity=None):
    labels = pd.Series([1] * len(df), index=df.index)
    labels &= df['ogCity'] == ogcity
    return labels


def get_slice_destcity(df, destcity=None):
    labels = pd.Series([1] * len(df), index=df.index)
    labels &= df['destCity'] == destcity
    return labels

def get_slice_membership(df, ogstate=None, destate=None, ogcity=None, destcity=None, quarter=None, airline=None):
    labels = pd.Series([1] * len(df), index=df.index)
    if ogstate:
        labels &= df['OriginState'] == ogstate
    if destate is not None:
        labels &= df['DestState'] == destate
    if ogcity:
        labels &= df['ogCity'].isin(ogcity)
    if destcity:
        labels &= df['destCity'].isin(destcity)
    if quarter:
        labels &= df['Quarter'].isin(quarter)
    if airline:
        labels &= df['AirlineCompany'].isin(airline)
    return labels

# ------------ Flight price prediction starts ---------------------

