import streamlit as st
import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt
import altair as alt
from sqlalchemy import create_engine
import pymysql
import time
from datetime import datetime, timedelta

# Function to generate time intervals between start_time and end_time
def generateTimeFunction(start_time, end_time):
    intervals = []
    current_time = start_time
    while current_time < end_time:
        next_time = current_time + timedelta(hours=1)
        intervals.append(f"{current_time.strftime('%H:%M')} - {next_time.strftime('%H:%M')}")
        current_time = next_time
    intervals.append(f"{end_time.strftime('%H:%M')} - {datetime.strptime("23:59", "%H:%M").strftime('%H:%M')}")
    
    return intervals

# Function to connect to the database and execute a query
def dataBaseConnectionFunction(quary):
    engine = create_engine("mysql+pymysql://root:ES17cs74@localhost/redbusinfo")
    with engine.connect() as conn:
        df = pd.read_sql(quary,conn)
    return df

# Sidebar radio button for navigation
selcetRadioVar = st.sidebar.radio("Main Menu",["Home","Search Buses"])

# Home page
if selcetRadioVar =="Home":
    st.markdown("""<h3>RedBus Site Information</h3>""",True)
    linkCol1,linkCol2 = st.columns(2,gap="Large")
    linkCol1.markdown("[RedBus Ticket Booking Site Link](https://www.redbus.in/)")
    linkCol2.markdown("""&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp; [RedBus App Download Link](https://play.google.com/store/apps/details?id=in.redbus.android&hl=en_IN&pli=1)""",True)
    st.video("https://youtu.be/Ajaik2PxMTw?si=x0PEw522PGEx0kTN")
# Search Buses page    
elif selcetRadioVar =="Search Buses":
    st.markdown("""<h3>Search Buses</h3>""",True)
    start_time = datetime.strptime("00:00", "%H:%M")
    end_time = datetime.strptime("23:00", "%H:%M")
    hourlyValue = generateTimeFunction(start_time,end_time)
    tab1,tab2 = st.tabs(["Search Buses", "Free Sugar Checkup"])
    # Content for the first tab        
    with tab1:
        form = st.form(key="BusSearchInfo")        
        col1, col2, col3 = form.columns(3) 

        
        sqlQuery = "select * from oneroutebusesinfo"
        fileDs = dataBaseConnectionFunction(sqlQuery)  
        
        # Extract unique values for dropdowns
        busRouteInfo = fileDs["RouteName"].unique()
        ratingInfo = fileDs["Rating"].unique()
        priceInfo = fileDs["Price"].unique() 
        busNameInfo = fileDs["Bus Name"].unique()   
        seatAvailableInfo = fileDs["Seats Available"].unique()     
        

        with col1:
            routeInfo = col1.selectbox("Select the Route", busRouteInfo)
            ratings = col1.selectbox("Select the Ratings", ratingInfo)
        with col2:
            #busName = col2.selectbox("Select the Bus Name", busNameInfo)
            busName = col2.text_input("Select the Bus Name")
            time = col2.selectbox("Time between",hourlyValue)
        with col3:
            seatAvailableInfo = col3.selectbox("Select Number of Seat Availablity",seatAvailableInfo)
            price = col3.selectbox("Bus Fare Range(Start From)", priceInfo)

        
            

        submit = form.form_submit_button("Search")
         # When the form is submitted
        if submit:
            dataStart = time.split("-")[0].strip()
            dataEnd   = time.split("-")[1].strip()
            
            searchRequestQuery = f'select * from oneroutebusesinfo where routename="{routeInfo}"  and Rating>={ratings} and `seats Available`>={seatAvailableInfo} and price>={price} and `Bus Name` like "{busName+'%'}%" and `Departure Time` BETWEEN  "{dataStart}" and "{dataEnd}"'
            searchBusInfo = dataBaseConnectionFunction(searchRequestQuery)                
            
            testData = pd.DataFrame(searchBusInfo)
            

            # Convert 'Departure Time' to string and extract the time part
            testData['Departure Time'] = testData['Departure Time'].astype(str)
            testData['Departure Time'] = testData['Departure Time'].apply(lambda timeValue: str(timeValue).split()[-1])
            
            # Convert 'Arrival Time' to string and extract the time part
            testData['Arrival Time'] = testData['Arrival Time'].astype(str)
            testData['Arrival Time'] = testData['Arrival Time'].apply(lambda timeValue: str(timeValue).split()[-1])

            # Check if DataFrame is empty
            if testData.empty:
                st.warning("No Buses are available")
            else :
                st.success("Bus details are below")
                tab1.dataframe(pd.DataFrame(testData))
        
        
    # Content for the second tab
    with tab2:
        tab2.info("Development in-progress")
        