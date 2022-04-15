# Final Project Proposal

**Team:** Tina Feng, Silvia Gu, Zhiyuan Guo, Anita Sun

**GitHub Repo URL**: https://github.com/CMU-IDS-2022/final-project-flight-traffic-brain


## Overall Topic 
Flight Traffic Brain

## Track ##
Interactive Visualization/Application 
## Questions to Ask ##
**In this project we want to:**
1) Help airports better manage airlines and control airline traffic;
2) Help passengers make wiser decisions about airline flights; 

**Our exploration will be centered around 4 directions to offer help for both airports and passengers:**

1. **Design for Airports**
    1) Create a flight network graph to visualize the connections between airports and flights
    2) Develop a ML model to predict potential delay time of certain flights

2. **Design for Passengers**
    1) Develop a ML model to predict delay time (for both airports and passengers) and price of flights 
    2) Provide passengers with flight planning recommendations based on information about major airports and flights using historical data


## Data Processing

Our data srouces are from [FlightRadarAPI](https://github.com/JeanExtreme002/FlightRadarAPI) and a [Kaggle Dataset](https://www.kaggle.com/datasets/zernach/2018-airplane-flights) about flight prices from 2018.

FlightRadarAPI provides us an API to retrieve real-time air traffic data, 
including airlines list, flights list, and information regarding a flight such
as time, altitude, speed, source, destination, and so on. The data format
mostly comes in json, and we would need to do some processing to convert data
into our desired format. We plan to use real-time flight information, such as
flight locations, source and destination, and departing and landing time.
The data processing will be implemented in a class called `AirData` in 
`airdata.py`, where we request data from API and parse data into a dataframe.
Below is an example of such dataframe.

```
>>> from airdata import AirData
>>> ad = AirData()
>>> df = ad.get_flights_df()
>>> df
           id icao_24bit  latitude  ...  vertical_speed  callsign  airline_icao
0    2b6b0475     AC0D21   37.7189  ...               0   FDX1800           FDX
1    2b6b4868     A6C826   35.6307  ...               0    EJA536           EJA
2    2b6b5cdc     896464   60.7218  ...             -64    ETD93C           ETD
3    2b6b6ae7     781D6D   33.4156  ...            -960    CKK221           CKK
4    2b6b7226     896488   53.1064  ...               0    ETD11B           ETD
..        ...        ...       ...  ...             ...       ...           ...
202  2b6c2c2a     A086B4   44.2131  ...               0    DAL852           DAL
203  2b6c2c45     AD237F   30.0230  ...               0   AAL2813           AAL
204  2b6c2c8d     A14872   33.8755  ...             128    DAL768           DAL
205  2b6c2cfa     A06010   34.0600  ...               0   AAL1820           AAL
206  2b6c2d0f     A202FD   18.6110  ...            -832    FFT100           FFT

[207 rows x 19 columns]
```

TODO: kaggle dataset...

## System design

### Flight Map


### Flight Delay Visual Analysis

### Flight Price Prediction

![Sketch 1](./price-prediction-sketch_1.png)
![Sketch 2](./price-prediction-sketch_2.png)
![Sketch 3](./price-prediction-sketch_3.png)
![Sketch 4](./price-prediction-sketch_4.png)

		
## Specifics ##
Nowadays, air traffic control has become a complicated task as there are more and more flights and airlines. It becomes harder for the airports and air traffic control specialists to manage those flights coming from different locations in the world. Because of the dependencies between flights, a delay in one can cause delays in other flights if they are not properly managed. An interactive data science solution can help alleviate this problem. A real-time map of flights with interactive information such as speed and altitude can help the specialists to make better decisions. Meanwhile, an interactive network graph that shows the connections between airports and flights can also improve the handling of dependencies among the traffic.

Besides the real-time interactive network graph, we also plan to develop a ML model with historical flight data including airlines, routes, dates, departure time and arrival time in order to effectively predict the potential delay time of certain flights in real time. The predicted delay time will help airport specialists to better communicate with the airports and passengers and make better decisions in terms of resource distribution and cost reduction.

Aside from delay time, we will build a ML model using historical data to predict flight price as well. Candidate parameters include airline code, flight time (flying hours, long-haul or short-haul), point of departure, destination, etc. This model will help passengers estimate the potential fare of flight of their interest. It will also allow them to compare different flight prices by modifying parameters of interest, thus helping optimize their travel plan. 

People are provided a lot of information about airlines when they plan trips. However, these pieces of information are quite disordered, which makes it difficult to choose. We hope to design a platform and help customers design and plan trips. The interactive options include the place of departure and destination, date, price ranges they can accept, etc. We will visualize the recommended airlines in a map that mark the departure, destination, transition places, the airline routes. Users can also choose two specific airlines to compare features like price, duration, distance. We will visualize the comparison module through a jointed bar chart, in which each column represents a feature. 





