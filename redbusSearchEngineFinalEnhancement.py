import streamlit as st
import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt
import altair as alt
from sqlalchemy import create_engine
import pymysql
import time
from datetime import datetime, timedelta
import pickle
from xgboost import XGBClassifier

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
    tab1,tab2 = st.tabs(["Search Buses", "Diabetes Checkup"])
    # Content for the first tab        
    with tab1:
        form = st.form(key="BusSearchInfo")        
        col1, col2, col3 = form.columns(3) 

        
        sqlQuery = "select * from oneroutebusesinfo"
        fileDs = dataBaseConnectionFunction(sqlQuery)  
        
        # Extract unique values for dropdowns
        busRouteInfo = fileDs["RouteName"].unique()
        ratingInfo = fileDs["Rating"].unique()
        #priceInfo = fileDs["Price"].unique() 
        priceInfo = ["Below 500","500 to 1000","1000 to 1500","1500 to 2000","Above 2000"]
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
            searchRequestQuery = f''

            #print(price)
            if price =="Below 500":                
                searchRequestQuery = f'select * from oneroutebusesinfo where routename="{routeInfo}"  and Rating>={ratings} and `seats Available`>={seatAvailableInfo} and price<{500} and `Bus Name` like "{busName+'%'}%" and `Departure Time` BETWEEN  "{dataStart}" and "{dataEnd}"'
            elif price =="500 to 1000":
                searchRequestQuery = f'select * from oneroutebusesinfo where routename="{routeInfo}"  and Rating>={ratings} and `seats Available`>={seatAvailableInfo} and price BETWEEN {500} and {1000} and `Bus Name` like "{busName+'%'}%" and `Departure Time` BETWEEN  "{dataStart}" and "{dataEnd}"'    
            elif price =="1000 to 1500":
                searchRequestQuery = f'select * from oneroutebusesinfo where routename="{routeInfo}"  and Rating>={ratings} and `seats Available`>={seatAvailableInfo} and price BETWEEN {1000} and {1500} and `Bus Name` like "{busName+'%'}%" and `Departure Time` BETWEEN  "{dataStart}" and "{dataEnd}"'    
            elif price =="1500 to 2000":
                searchRequestQuery = f'select * from oneroutebusesinfo where routename="{routeInfo}"  and Rating>={ratings} and `seats Available`>={seatAvailableInfo} and price BETWEEN {1500} and {2000} and `Bus Name` like "{busName+'%'}%" and `Departure Time` BETWEEN  "{dataStart}" and "{dataEnd}"'    
            else :
                searchRequestQuery = f'select * from oneroutebusesinfo where routename="{routeInfo}"  and Rating>={ratings} and `seats Available`>={seatAvailableInfo} and price>{2000} and `Bus Name` like "{busName+'%'}%" and `Departure Time` BETWEEN  "{dataStart}" and "{dataEnd}"'    

            #searchRequestQuery = f'select * from oneroutebusesinfo where routename="{routeInfo}"  and Rating>={ratings} and `seats Available`>={seatAvailableInfo} and price>={price} and `Bus Name` like "{busName+'%'}%" and `Departure Time` BETWEEN  "{dataStart}" and "{dataEnd}"'
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
        tab2.info("Free Diabetes CheckUp based on xgboost model Machine learning, It have 97% of accuracy rate")
        form = st.form(key="diabetesCheckup")
        # Initialize variables for form inputs   
        float_age = 0.0
        float_bmi = 0.0
        float_HbA1clevel = 0.0
        float_glucoseLevel = 0.0

        gender_int = 0
        bp_int = 0 
        heartDisease_int = 0
        smokingHistory_int = 0

        # Create columns for form inputs
        col1, col2, col3, col4 = form.columns(4)  

        # First column: Gender and smoking history
        with col1:
            gender = col1.selectbox("Select Your Gender", ["Female","Male"])
            smokingHistory = col1.selectbox("Smoking history",["No Info", "current", "ever", "former", "never", "not current"]) 
        # Second column: Age and BMI inputs
        with col2:
            age = col2.text_input("Enter your Age in Number")
            if not age=="":
                float_age = float(age)            
            bmi = col2.text_input("Enter your BMI")
            if not bmi=="":
                float_bmi = float(bmi)  
        # Third column: BP and HbA1c level inputs
        with col3:
            bp = col3.selectbox("Do you have BP",["No","Yes"])
            HbA1clevel = col3.text_input("Enter your HbA1c level")
            if not HbA1clevel=="":
                float_HbA1clevel = float(HbA1clevel)     
        # Fourth column: Heart disease and glucose level inputs
        with col4:
            heartDisease = col4.selectbox("Do you have Heart Disease",["No","Yes"])
            glucoseLevel = col4.text_input("Blood glucose level")    
            if not glucoseLevel=="":
                float_glucoseLevel = float(glucoseLevel)               
            
        # Form submission button
        clickToFind = form.form_submit_button("Click Here")
        # Form validation and model prediction
        if clickToFind:
            if float_age == "" or float_age == " " or float_age == 0.0:
                st.error("Please Enter Age")
            elif float_bmi == "" or float_bmi == " " or float_bmi == 0.0:
                st.error("Please Enter BMI")
            elif float_HbA1clevel == "" or float_HbA1clevel == " " or float_HbA1clevel == 0.0:
                st.error("Please Enter 'HbA1c' Level")            
            elif float_glucoseLevel == "" or float_glucoseLevel == " " or float_glucoseLevel == 0.0:
                st.error("Please Enter Glucose Level")
            else :
                # Convert gender to integer
                if gender =="Female":
                    gender_int = 0
                elif gender =="Male":
                    gender_int = 1
                # Convert BP to integer
                if bp =="No":
                    bp_int = 0
                elif bp =="Yes":
                    bp_int = 1    
                # Convert heart disease to integer
                if heartDisease =="No":
                    heartDisease_int = 0
                elif heartDisease =="Yes":
                    heartDisease_int = 1

                # Convert smoking history to integer
                if smokingHistory =="No Info":
                    smokingHistory_int = 0
                elif smokingHistory =="current":
                    smokingHistory_int = 1
                elif smokingHistory =="ever":
                    smokingHistory_int = 2
                elif smokingHistory =="former":
                    smokingHistory_int = 3
                elif smokingHistory =="never":
                    smokingHistory_int = 4
                elif smokingHistory =="not current":
                    smokingHistory_int = 5

                # Use Pickle to get Trained model file
                with open("XGB.pkl","rb") as trainedFile:
                    sugerCheckup_model = pickle.load(trainedFile) 

                # Prepare the input for prediction
                sugerTestPersonInput = np.array([[gender_int,float_age,bp_int,heartDisease_int,smokingHistory_int,float_bmi,float_HbA1clevel,float_glucoseLevel]])
                checkResult = sugerCheckup_model.predict(sugerTestPersonInput)
                
                # final result position of Diabetes
                if checkResult[0] == 0:
                    st.write("Diabetes Negative")
                    st.balloons()
                    st.success("Congragulation You not have Diabetes, Still make one time medical check to become 100% confident about you medical condition")
                elif checkResult[0] == 1:
                    st.write("Diabetes Positive")
                    st.snow()
                    st.warning("Sorry You have Diabetes, still this method 97% only accurate, Better make one medical checkup to identify you have diabetes or not, Here their is a change you not have diabetes please make sure viz diabetes medical checkup")
                

