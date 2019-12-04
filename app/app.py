import streamlit as st
import requests
import seaborn as sns
import pandas as pd
import numpy as np

# Importing pages from the pages folder
import pages.overview
import pages.trends


## Setting up the pages
PAGES = {
    "Overview": pages.overview,
    "Crime Trends" : pages.trends
}

# Radio selector to switch over the different pages
selection = st.sidebar.radio("Go to", list(PAGES.keys()))

page = PAGES[selection]

# Data loading functions
@st.cache
def match_postcodes(postcode):
    """
    Function that takes a postcode and build a polygon based on the coordinates of the area around it.
    """
    response = requests.get(f'http://api.postcodes.io/postcodes/{postcode}')
    if response.ok:
        df = [response.json()['result']['latitude'],response.json()['result']['longitude']]
        force = requests.get(f'https://data.police.uk/api/locate-neighbourhood?q={df[0]},{df[1]}').json().get('force')
        neigh = requests.get(f'https://data.police.uk/api/locate-neighbourhood?q={df[0]},{df[1]}').json().get('neighbourhood')
        boundary = requests.get(f'https://data.police.uk/api/{force}/{neigh}/boundary').json()
        boundary = pd.DataFrame.from_dict(boundary)
        polygon=f"{boundary['latitude'].max()},{boundary['longitude'].max()}:\
            {boundary['latitude'].max()},{boundary['longitude'].min()}:\
                {boundary['latitude'].min()},{boundary['longitude'].min()}:\
                    {boundary['latitude'].min()},{boundary['longitude'].max()}"
    else:
        raise Exception
    return df, polygon

@st.cache
def fetch_dates():
    """
    Function that fetches the date range of the available data
    """
    response = requests.get('https://data.police.uk/api/crimes-street-dates')
    if response.ok:
        df = pd.DataFrame.from_dict(response.json())
        df = df.explode('stop-and-search')
    else:
        df = "Data pull failed, please refresh the page"
    return df

@st.cache
def fetch_force_data(coordinates):
    """
    Function to match the postcodes coordinates to the police force of the area and the relevant people in it.
    """
    ids = requests.get(f'https://data.police.uk/api/locate-neighbourhood?q={coordinates[0]},{coordinates[1]}').json()['force']
    response = requests.get(f'https://data.police.uk/api/forces/{ids}')
    response2 = requests.get(f'https://data.police.uk/api/forces/{ids}/people')
    if response.ok and response2.ok:
        df = response.json()
        df2 = response2.json()
    else:
        df = f"Data pull failed with error{response.text}, please refresh the page"
        df2=''
    return df, df2

### SIDEBAR ELEMENTS - SELECT FORCE AND DATES

# Default settings
code = [51.509865, -0.118092]
poly = '51.5201931,-0.1284721:51.5145315,-0.1272705:51.5149054,-0.1130226:51.5206203,-0.1149109:51.5201931:-0.1284721'
st.sidebar.title("Parameter selection")
st.sidebar.markdown("Please input postcode to view crimes in area")

# Postcode input box
postcode = st.sidebar.text_input(
    'Input your full postcode',
    'WC2E 7EA'
)
try:
    code,poly = match_postcodes(postcode)
except:
    st.sidebar.error('The postcode entered could not be matched')
force_prof, force_people = fetch_force_data(code)

dates = fetch_dates()
available = dates[dates['stop-and-search'] == force_prof['id']]['date']

# Data describing police force
st.sidebar.markdown(f"## **{force_prof.get('name')}**")

st.sidebar.markdown("**Contact:**")
st.sidebar.markdown(f"[URL]({force_prof.get('url')})")
st.sidebar.markdown(f"Telephone: {force_prof.get('telephone')}")

st.sidebar.markdown("**Engagement:**")
for method in force_prof.get('engagement_methods'):
    st.sidebar.markdown(f"- [{method['title']}]({method['url']})")

if len(force_people) > 0:
    st.sidebar.markdown("**People**:")
    for person in force_people:
        st.sidebar.markdown('- '+str(person['name'])+', '+str(person['rank']))

# Actual function to write the page selected in the radio selector
with st.spinner(f"Loading {selection} ..."):
    page.write(postcode, poly, available, code)