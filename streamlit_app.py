import streamlit as st
import pandas as pd
import altair as alt
import pickle
import numpy as np

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
    rb_lower = pickle.load(open('gb_lower.sav', 'rb'))
    rb_mean = pickle.load(open('gb_mean.sav', 'rb'))
    rb_upper = pickle.load(open('gb_upper.sav', 'rb'))
    lb = rb_lower.predict(X)
    mean = rb_mean.predict(X)
    ub = rb_upper.predict(X)
    return (round(np.exp(lb[0]),2), round(np.exp(mean[0]),2), round(np.exp(ub[0]),2))


# load data for non ML visual
def load_data():
    return pd.read_csv('train_viz.csv').iloc[:,:]
    

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

        
# ------------------------ Flight price prediction starts ------------------------------    
## Price Prediction 
st.title("Flight Price Prediction")

# 1. ML prediction
X_train=pd.read_csv('X_train.csv')
features = list(X_train.columns)
del X_train
df_pred = pd.DataFrame(0, index=np.arange(1), columns=features)

col1, col2 = st.columns([3, 2])
with col2:
    og = st.selectbox('Origin', np.array(origin))
    de = st.selectbox('Destination', np.array(dest))
    season = st.selectbox('Season', ['Spring','Summer','Fall','Winter'])
    airline = st.selectbox('Airline Company', np.array(air))
    numT = st.slider('Number of tickets', 1, 15, 1)
    if og != "Virgin Islands":
        df_pred[f'o{og}'] = 1
    else:
        df_pred['oU.S. Virgin Islands']=1
    if de != "Virgin Islands":
        df_pred[f'd{de}'] = 1
    else:
        df_pred['dU.S. Virgin Islands']=1
    
    if season!='Spring':
        df_pred[quarter_dic[season]] = 1
    
    if airline[-3:-1]!='AA':
        df_pred[airline[-3:-1]] = 1  
    
    df_pred['NumTicketsOrdered'] = numT


    if og!=de:
        try:
            miles = miles_dic[(og,de)]
        except:
            miles = miles_dic[(de,og)]
        df_pred['log_miles']=np.log(miles)
    else:
        st.markdown(" ")
    
 
if og!=de:
    low, mean, high = get_pi(pd.DataFrame(df_pred))
    with col1:
        st.metric("Low", f'${low}',"+$",delta_color="inverse")
        st.metric("Mean", f'${mean}')
        st.metric("High", f'${high}',"-$",delta_color="inverse")
        df_interval = pd.DataFrame([[low,mean,high]],columns=['Low','Mean','High'])

    with st.expander("See price distribution"):
        # plot price dist
        bar = alt.Chart(df_viz).mark_bar(opacity=0.3,tooltip = True).encode(
            alt.X('PricePerTicket:Q',title="Price per Ticket ($)"),#scale=alt.Scale(type='log')),
            alt.Y('count()',title='Raw Frequency Count')
        ).properties(
            title='Unit Price Distribution'
        #).transform_filter(
        ).interactive()

        mean = alt.Chart(df_interval).mark_rule(color='purple',tooltip=True).encode(
            x='Mean:Q',
            size=alt.value(4),
            
        )

        low = alt.Chart(df_interval.sample(1)).mark_rule(color='darkblue',tooltip=True).encode(
            x='Low:Q',
            size=alt.value(2),
            #strokeDash='Quarter'
        )

        high = alt.Chart(df_interval.sample(1)).mark_rule(color='darkblue',tooltip=True).encode(
            x='High:Q',
            size=alt.value(2),
            #tooltip = 'PricePerTicket'
            #strokeDash='Quarter'
        )
        price_chart = bar + mean + low+ high

        selection = alt.selection_interval()
        hist = alt.Chart(df_viz.sample(5000,random_state=216)).mark_bar(
            tooltip=True
        ).encode(
            alt.Y("Quarter:O"),
            alt.X('PricePerTicket:Q'),
            #alt.Color("AirlineCompany", scale=alt.Scale(domain=air, range=[
                #"orangered", "purple", "seagreen",'yellow','red','blue','pink','salmon','orange','green','violet','gold'])
        )

        price_interaction = bar.add_selection(selection).encode(
         #color=alt.condition(selection, "PricePerTicket:O", alt.value("grey"))
        ) + low+mean+high| hist.encode(
            alt.Color("AirlineCompany")
        ).transform_filter(selection) 

        #st.altair_chart(price_interaction)
        st.altair_chart(price_chart)
else:
    with col1:
        st.metric(" ", 'Not Available')
        st.markdown("**Please choose a different origin or destination!**")
        
# ------------------------ Flight price prediction ends ------------------------------       
        
    
    
# ------------------------ Flight price comparison starts ------------------------------           
## Price comparison
st.title("Choose the flight you are interested in")
df = load_data()


cols = st.columns(3)
with cols[0]:
    ogstate = st.selectbox('Origin State', sorted(df['OriginState'].unique()))
    slice_ogstates = get_slice_ogstate(df,ogstate)
    ogcity = st.multiselect('Origin City', sorted(df[slice_ogstates]['ogCity'].unique()))

with cols[1]:  
    destate = st.selectbox('Destination State', sorted(df['DestState'].unique()))
    slice_destates = get_slice_destate(df,destate)
    destcity = st.multiselect('Destination City', sorted(df[slice_destates]['destCity'].unique()))


with cols[2]:
    quarter = st.multiselect('Quarter',sorted(df['Quarter'].unique()))
    airline = st.multiselect('Airline Company', sorted(df['AirlineCompany'].unique()))

slice_labels = get_slice_membership(df, ogstate, destate, ogcity, destcity, quarter, airline)
slice_labels.name = "slice_membership"

df_show = df[slice_labels].iloc[:,:][['PricePerTicket','og','dest','Quarter','AirlineCompany']].sort_values(by='PricePerTicket')
df_show = df_show.rename(columns={'PricePerTicket':'Price per Ticket ($)','og':'Origin','dest':'Destination'}).reset_index(drop=True)
df_show['Price per Ticket ($)'] = df_show['Price per Ticket ($)'].apply(lambda x: "{:.2f}".format(x))
if df_show.empty:
    st.metric(" ", "No Data Available")
else:
    st.write(df_show)

#-------------------- Price Heat Map-------------------------------------------
def load_data(url):
    file = url
    df = pd.read_csv(file)

    return df

df = load_data('train_viz.csv')
st.title("Choose the season you want to travel, find the most economical route and airline")

def get_season(df, quarter):
    sub = df[df['Quarter']== quarter]

    return sub

quarter = st.selectbox('Season(Quarter)', sorted(df['Quarter'].unique()))
season_df = get_season(df,quarter)


# Take top 20 frequency states
statelist = ['California','Florida','Texas','New York','Georgia','Illinois','Nevada','Virginia','Massachusetts',
             'Washington','Pennsylvania','Arizona','New Jersey','Minnesota','Michigan','Missouri','Maryland','Hawaii']
heat_price = season_df[season_df['OriginState'].isin(statelist) ]
heat_price = heat_price[heat_price['DestState'].isin(statelist) ]
# Take average price and miles per route
heat_price = heat_price.groupby(['OriginState','DestState'])[['PricePerTicket','Miles']].mean().reset_index()
# Drop the invalid value(origin = destination)
heat_price = heat_price[heat_price['OriginState'] != heat_price['DestState']]

heatmap = alt.Chart(heat_price).mark_rect().encode(
    x='OriginState:O',
    y='DestState:O',
    color='PricePerTicket:Q',
    tooltip=['OriginState', 'DestState', 'PricePerTicket','Miles']
)
st.altair_chart(heatmap)

box = alt.Chart(season_df).mark_boxplot(extent='min-max').encode(
    x='AirlineCompany:O',
    y='PricePerTicket:Q',
    color=alt.Color('AirlineCompany')
    
).properties(
    width=500,
    height=300)
st.altair_chart(box)


