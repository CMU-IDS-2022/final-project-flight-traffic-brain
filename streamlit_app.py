import streamlit as st
import pandas as pd
import altair as alt
import pickle
import numpy as np

from map import create_map
from airdata import AirData
from utils import parse_time, parse_time_hms
from vega_datasets import data

# Getting data ready, Refresh every hour (same data when user refreshes within an hour)
@st.cache(ttl=60 * 60, suppress_st_warning=True)
def get_AD_data():
    ad = AirData()
    flight_df = ad.get_flights_df()
    flight_df = ad.add_time_to_df(flight_df)
    return ad, flight_df

# Cache to prevent computation on every rerun
@st.cache
def save_AD_data(df):
    return df.to_csv().encode('utf-8')


ad, flight_df = get_AD_data()


# Definitions for flight delay

## Prepare data
# load in files
origin = pickle.load(open('DestState.sav','rb'))
dest = pickle.load(open('DestState.sav','rb'))
air = pickle.load(open('AirlineCompany.sav','rb'))
miles_dic = pickle.load(open('miles_dic.sav','rb'))
quarter_dic= {'Spring':'Q1','Summer':'Q2','Fall':'Q3','Winter':'Q4'}
df_viz = pd.read_csv('df_viz.csv').iloc[:,:]



# fit the prediction model, get prediction and prediction interval
def get_pi(X):
    all_models = pickle.load(open('all_models.sav', 'rb'))
    lb = all_models[0].predict(X)
    pred = all_models[2].predict(X)
    ub = all_models[1].predict(X)
    return (round(np.exp(lb[0]),2), round(np.exp(pred[0]),2), round(np.exp(ub[0]),2))




# load data for non ML visual
def load_data_ml():
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


def get_slice_membership(df, ogstate=None, destate=None, quarter=None,airline=None):
    labels = pd.Series([1] * len(df), index=df.index)
    if ogstate:
        labels &= df['OriginState'] == ogstate
    if destate is not None:
        labels &= df['DestState'] == destate
    if quarter:
        labels &= df['Quarter'].isin(quarter)
    if airline:
        labels &= df['AirlineCompany'].isin(airline)
    return labels

#-------------------- Price Heat Map-------------------------------------------
def load_data(url):
    file = url
    df = pd.read_csv(file)

    return df

def get_season(df, quarter):
    sub = df[df['Quarter']== quarter]

    return sub

menu_selection =  st.sidebar.radio("Menu", ["Flight Map", "Flight Delay Analysis", 
                                            "Flight Price Analysis"])
if menu_selection == "Flight Map":

    st.title("Real-time Flight Data Visualization")
    # ------------ Map starts ---------------------

    with st.sidebar.expander("Analysis for flights/airports"):
        st.write("This is an analysis tool from the perspective of flights or airports")
        to_show = st.selectbox("Data to look at", ["flight", "airport"])
        if to_show == "flight":
            field = st.selectbox("Variable of interest", ["heading", "altitude", "ground_speed"])
        else:
            field = st.selectbox("Variable of interest", ["origin_airport_iata", "destination_airport_iata"])

    st.write("This is a map of real-time flights and airports. The blue circles are \
            the airport, while the red squares are the flights. You can utilize \
            the tool bar on the left tab to explore the data. You can also \
            move your mouse over the map to see more information.")
    map_air = create_map(flight_df, field, to_show)

    st.altair_chart(map_air)

    st.sidebar.title("Note")

    st.sidebar.write("This visualization consists of three components.\
        The first component is a map that shows real-time flights and airports\
        in the U.S. The second component, linked to the first component, \
        is an analysis tool for the real-time flight and airport data. \
        The third component displays the time information of a flight.")

    st.sidebar.download_button("Download real-time data", data=save_AD_data(flight_df),
                        file_name='airdata.csv', mime='text/csv')

    # ------------ Map ends ---------------------


    # ------------ Flight time starts ---------------------

    st.write("Here we display the time information of a flight.")

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

# Note that some flights are not displayed due to... so the number of routes
# may appear larger than...

# ------------ Flight time ends ---------------------


elif menu_selection == "Flight Delay Analysis":

    # ------------ Delay Analysis starts ---------------------


    st.title("Flight Delay Analysis")

    ad = AirData()
    flight_df = ad.get_flights_df()

    st.header("Slice Data")
    st.write("You can filter the airline data by choosing the different departure airport.")
    with st.expander("Airports"):
        origin_airport_list = flight_df['origin_airport_iata'].drop_duplicates()
        option1 = st.selectbox("Departure Airport:",
                                (origin_airport_list))
        flight_df_selected1 = flight_df[(flight_df['origin_airport_iata'] == option1)]

    st.header("Data Visualization")
    with st.expander("Flight delay from different departure airports"):
        st.write("This data indicates all the current flights coming from the departure airport and their related delay times.")
        index = 0
        for row in flight_df_selected1.iterrows():
            flight_number = flight_df_selected1['number'].values[index]
            option_id = flight_df_selected1['id'].values[index]
            option_detail = ad.get_flight_details(option_id)
            option_time = option_detail['time']
            if option_time['real']['departure'] is None:
                continue
            elif option_time['real']['arrival'] is None:
                depart_delta = option_time['real']['departure'] - option_time['scheduled']['departure']
                arrive_delta = None
                col1, col2, col3 = st.columns(3)
                col1.metric("Flight number",
                            flight_number)
                col2.metric("Departure delay",
                            parse_time_hms(depart_delta))
                col3.metric("Arrival delay",
                            arrive_delta)
            else:
                depart_delta = option_time['real']['departure'] - option_time['scheduled']['departure']
                arrive_delta = option_time['real']['arrival'] - option_time['scheduled']['arrival']
                col1, col2, col3 = st.columns(3)
                col1.metric("Flight number",
                            flight_number)
                col2.metric("Departure delay",
                            parse_time_hms(depart_delta))
                col3.metric("Arrival delay",
                            parse_time_hms(arrive_delta))   
            index = index + 1 

    with st.expander("Flight delay of different airlines"):
        st.write("This data compares the punctuality and departure delay times between different airlines.")
        depart_delay = []
        index = 0
        for row in flight_df_selected1.iterrows():
            option_id = flight_df_selected1['id'].values[index]
            option_detail = ad.get_flight_details(option_id)
            option_time = option_detail['time']
            if option_time['real']['departure'] is None:
                continue
            else:
                depart_delta = option_time['real']['departure'] - option_time['scheduled']['departure']
                depart_delta = parse_time_hms(depart_delta)
                depart_delay.append(depart_delta)
                index = index + 1    
        flight_df_selected1['depart_delay'] = depart_delay
        stripplot = alt.Chart(flight_df_selected1, width=640).mark_circle(size=30).encode(
            x=alt.X(
                'depart_delay',
                title='Departure delay',
                scale=alt.Scale()),
            y=alt.Y(
                'airline_iata',
                title='Airline iata'),
            color=alt.Color('airline_iata', legend=alt.Legend(orient="right")),
            tooltip=['number', 'airline_iata', 'depart_delay']
        ).transform_calculate(
            jitter='sqrt(-2*log(random()))*cos(2*PI*random())'
        ).configure_facet(
            spacing=0
        ).configure_view(
            stroke=None
        )

        stripplot

    with st.expander("Compare average departure delay of different airlines"):
        depart_delay = []
        index = 0
        for row in flight_df_selected1.iterrows():
            option_id = flight_df_selected1['id'].values[index]
            option_detail = ad.get_flight_details(option_id)
            option_time = option_detail['time']
            if option_time['real']['departure'] is None:
                continue
            else:
                depart_delta = option_time['real']['departure'] - option_time['scheduled']['departure']
                # depart_delta = parse_time_hms(depart_delta)
                depart_delay.append(depart_delta)
                index = index + 1    
        flight_df_selected1['depart_delay'] = depart_delay

        average_delay = []
        airline_average_delay_parsed = []
        index = 0
        for row in flight_df_selected1.iterrows():
            ite_airline = flight_df_selected1['airline_iata'].values[index]
            airline_data = flight_df_selected1[flight_df_selected1['airline_iata'] == ite_airline]
            airline_average_delay = airline_data['depart_delay'].mean()
            average_delay_parsed = parse_time_hms(airline_average_delay)
            average_delay_parsed = str(average_delay_parsed).rstrip(':0')
            airline_average_delay = round(airline_average_delay, 2)
            # airline_average_delay = parse_time_hms(airline_average_delay)
            average_delay.append(airline_average_delay)
            airline_average_delay_parsed.append(average_delay_parsed)
            index = index + 1
        flight_df_selected1['airline_average_delay'] = average_delay
        flight_df_selected1['average_delay_parsed'] = airline_average_delay_parsed
        flight_df_selected2 = flight_df_selected1.drop_duplicates(subset=['airline_iata'], keep='first')
        flight_df_selected2 = flight_df_selected2.sort_values(by=['airline_average_delay'], ascending=False)

        barchart = alt.Chart(flight_df_selected2, width=640).mark_bar().encode(
            x=alt.X('airline_average_delay', axis=alt.Axis(labels=False)),
            y=alt.Y('airline_iata', sort=alt.EncodingSortField(field="airline_average_delay", op="count", order='ascending')),
            tooltip=['airline_iata', 'average_delay_parsed']
        )
        text = barchart.mark_text(
            align='left',
            baseline='middle',
            dx=3  # Nudges text to right so it doesn't appear on top of the bar
        ).encode(
            text='average_delay_parsed'
        )
        (barchart + text).properties(height=900)
        barchart + text

        index = 0
        for row in flight_df_selected2.iterrows():
            ite_airline = flight_df_selected2['airline_iata'].values[index]
            ite_delay = flight_df_selected2['average_delay_parsed'].values[index]
            # ite_delay = parse_time_hms(ite_delay)
            ite_delay = str(ite_delay).rstrip(':0')
            col1, col2 = st.columns(2)
            col1.metric("Airline",
                        ite_airline)
            col2.metric("Average departure delay",
                        ite_delay)
            index = index + 1

    # ------------ Delay Analysis ends ---------------------


else:

    # ------------------------ Flight price prediction starts ------------------------------    
    ## Price Prediction 
    st.title("Flight Price Analysis")
    
    # 1. ML prediction
    st.header("Flight Price Prediction")
    st.write("Tell us your intended flight information and get predicted flight price value and range.")
    

    X_train=pd.read_csv('X_train.csv')
    features = list(X_train.columns)
    del X_train
    df_pred = pd.DataFrame(0, index=np.arange(1), columns=features)

    col1, col2 = st.columns([3, 2])
    
    with col2:        
        og = st.selectbox('Origin', np.array(origin),index=30)
        de = st.selectbox('Destination', np.array(dest),index=4)
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
            st.subheader("Predicted Price per Ticket")
            st.metric("Low", f'${low}',"+$",delta_color="inverse")
            st.metric("Mean", f'${mean}')
            st.metric("High", f'${high}',"-$",delta_color="inverse")
            df_interval = pd.DataFrame([[low,mean,high]],columns=['Low','Mean','High'])
            
        st.write("See where your flight falls in the historical price distribution (2018)")
        with st.expander("See price distribution"):
            # plot price dist
            bar = alt.Chart(df_viz).mark_bar(opacity=0.3,tooltip = True).encode(
                alt.X('PricePerTicket:Q',title="Price per Ticket ($)"),#scale=alt.Scale(type='log')),
                alt.Y('count()',title='Raw Frequency Count')
            ).properties(
                title='Unit Price Distribution',
                width=600, 
                height=400
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
          
                #strokeDash='Quarter'
            )
            price_chart = bar + mean + low+ high
            
            
            st.altair_chart(price_chart)
        
    else:
        with col1:
            st.metric(" ", 'Not Available')
            st.markdown("**Please choose a different origin or destination!**")
            
    # ------------------------ Flight price prediction ends ------------------------------       
            
        
        
    # ------------------------ Flight price comparison starts ------------------------------           
    ## Price comparison
    st.header("Check the historical information of the flight you are interested in")
    st.write('We will look at some historical data in 2018.')
    df = load_data_ml()


    cols = st.columns(4)
    with cols[0]:
        ogs = sorted(df['OriginState'].unique())
        ogstate = st.selectbox('Origin State', ogs,index=ogs.index('New York'))
        
    with cols[1]:  
        des = sorted(df['DestState'].unique())
        destate = st.selectbox('Destination State', des,index=des.index('California'))


    with cols[2]:
        quarter = st.multiselect('Quarter',sorted(df['Quarter'].unique()))
        
    with cols[3]:
        airline = st.multiselect('Airline Company', sorted(df['AirlineCompany'].unique()))

       

    slice_labels = get_slice_membership(df, ogstate, destate, quarter,airline)
    slice_labels.name = "slice_membership"

    df_show = df[slice_labels].iloc[:,:][['PricePerTicket','og','dest','Quarter','AirlineCompany']].sort_values(by='PricePerTicket')
    df_show = df_show.rename(columns={'PricePerTicket':'Price per Ticket ($)','og':'Origin','dest':'Destination'}).reset_index(drop=True)
    df_show['Price per Ticket ($)'] = df_show['Price per Ticket ($)'].apply(lambda x: "{:.2f}".format(x))
    if df_show.empty:
        st.metric(" ", "No Historical Data Available")
        st.write("Please deselect some quarter/airline options or change origin/destination state.") 
    else:
        st.write(df_show)

    # ------------------------ Flight price comparison starts ------------------------------ --------

        
    df = load_data('train_viz.csv')
    st.header("Choose the season you want to travel, find the most economical route and airline")

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
    
    pts = alt.selection(type="multi", encodings=['x','y'])

    heat = alt.Chart(heat_price).mark_rect().encode(
        x='OriginState:O',
        y='DestState:O',
        color=alt.condition(pts,'PricePerTicket:Q', alt.ColorValue("grey")),
        tooltip=['OriginState', 'DestState', 'PricePerTicket','Miles']
    ).add_selection(pts)


    box = alt.Chart(df).mark_boxplot(extent='min-max').encode(
        x='AirlineCompany:O',
        y='PricePerTicket:Q',
        color=alt.Color('AirlineCompany')

    ).properties(
        width=500,
        height=300,
    ).transform_filter(
        pts
    )
    
    

    st.altair_chart(alt.vconcat(heat,box))
    
    st.header("Compare the price of different destination based on the origin you choose")

    origin = st.selectbox('Origin', sorted(df['OriginState'].unique()))
    def origin_data(origin,df):
        subset = df[df['OriginState']==origin]
        subset = subset.groupby(['OriginState','DestState'])[['PricePerTicket','Miles']].mean().reset_index()
        merged = subset.merge(data.income().groupby('name').mean().reset_index(), how = 'inner', left_on ='DestState', right_on= 'name')
        return merged

    subset = origin_data(origin,df)
    pts = alt.selection(type="multi", encodings=['x','y'])

    heat_bar = alt.Chart(subset).mark_rect().encode(
        x='DestState:O',
        y='OriginState:O',
        color=alt.condition(pts,'PricePerTicket:Q', alt.ColorValue("grey")),
        tooltip=['DestState']
    ).add_selection(pts)


    states = alt.topo_feature(data.us_10m.url, 'states')
    
    background = alt.Chart(states).mark_geoshape(
        fill='lightgray',
        stroke='white'
    ).properties(
        width=600,
        height=400
    ).project('albersUsa')
    
    foreground = alt.Chart(subset).mark_geoshape().encode(
        shape='geo:G',
        color=alt.condition(pts, 'name:N', alt.value('lightgray')),
        tooltip=['OriginState', 'DestState', 'PricePerTicket','Miles']
    ).transform_lookup(
        lookup='id',
        from_=alt.LookupData(data=states, key='id'),
        as_='geo'
    ).properties(
        width=600,
        height=400,
    ).project(
        type='albersUsa'
    )
    
    map = background + foreground
    
    st.altair_chart(alt.vconcat(heat_bar, map))

