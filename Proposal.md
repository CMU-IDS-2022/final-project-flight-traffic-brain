# Final Project Proposal

**Team:** Tina Feng, Silvia Gu, Zhiyuan Guo, Anita Sun

**GitHub Repo URL**: https://github.com/CMU-IDS-2022/final-project-flight-traffic-brain

A short summary (3-4 paragraphs, about one page) of the data science problem you are addressing and what your solution will address. Feel free to include a figure or sketch to illustrate your project.

Each member of your group should submit the URL pointing to this document on your github repo.



# Description
## Overall Topic 
Flight Traffic Brain
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
		
## Specifics ##
Nowadays, air traffic control has become a complicated task as there are more and more flights and airlines. It becomes harder for the airports and air traffic control specialists to manage those flights coming from different locations in the world. Because of the dependencies between flights, a delay in one can cause delays in other flights if they are not properly managed. An interactive data science solution can help alleviate this problem. A real-time map of flights with interactive information such as speed and altitude can help the specialists to make better decisions. Meanwhile, an interactive network graph that shows the connections between airports and flights can also improve the handling of dependencies among the traffic.

Besides the real-time interactive network graph, we also plan to develop a ML model with historical flight data including airlines, routes, dates, departure time and arrival time in order to effectively predict the potential delay time of certain flights in real time. The predicted delay time will help airport specialists to better communicate with the airports and passengers and make better decisions in terms of resource distribution and cost reduction.

Aside from delay time, we will build a ML model using historical data to predict flight price as well. Candidate parameters include airline code, flight time (flying hours, long-haul or short-haul), point of departure, destination, etc. This model will help passengers estimate the potential fare of flight of their interest. It will also allow them to compare different flight prices by modifying parameters of interest, thus helping optimize their travel plan. 

People are provided a lot of information about airlines when they plan trips. However, these pieces of information are quite disordered, which makes it difficult to choose. We hope to design a platform and help customers design and plan trips. The interactive options include the place of departure and destination, date, price ranges they can accept, etc. We will visualize the recommended airlines in a map that mark the departure, destination, transition places, the airline routes. Users can also choose two specific airlines to compare features like price, duration, distance. We will visualize the comparison module through a jointed bar chart, in which each column represents a feature. 





