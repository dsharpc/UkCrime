import streamlit as st
import requests
import seaborn as sns
import pandas as pd
import numpy as np




def fetch_data(coordinates=None, date=None):
    """
    Function to fetch the list of individual crimes that happened in the area 
    """
    response = requests.get(f"https://data.police.uk/api/crimes-street/all-crime?date={date}&poly={coordinates}")
    if response.ok and len(response.json()) > 0:   
        df = pd.DataFrame.from_dict(response.json())
        df['latitude'] = df['location'].apply(lambda x: float(x.get('latitude')))
        df['longitude'] = df['location'].apply(lambda x: float(x.get('longitude')))
        df['last_outcome'] = df['outcome_status'].apply(lambda x: x.get('category') if type(x) is dict else None)
    else:
        df = []
    return df

@st.cache(allow_output_mutation=True)
def hist_data(dates, range, poly):
    """
    Function that fetches crimes over a set number of periods
    """
    df_t = pd.DataFrame()
    for date in dates[:range]:
        df = fetch_data(poly,date)
        df_t = df_t.append(df)
    return df_t




### MAIN PAGE
def write(postcode, poly, available, code):
    st.title(f"Crime statistics for neighbourhood around {postcode.upper()}")
    st.markdown("The most common crimes in your area for the date selected are:")

    df = hist_data(available, 10, poly)

    crime_type = st.multiselect('Select the list of crimes you\'d like to filter by',
                            list(df.category.unique()), list(df.category.unique()))

    ## Filtering dataframe for crimes selected in multiselect
    df_f = df[df['category'].isin(crime_type)].copy()

    if len(df_f) > 0:
        st.markdown(f"Total number of crimes in selected categories over 10 most recent months: {len(df_f)}")
        st.vega_lite_chart(df_f.groupby('month')['category'].count().reset_index(), {
        'title': 'Time Series of Crimes in Type',
        'width':600,
        'height':100,
        'mark': 'line',
        'encoding': {
            'x': {'field': 'month', 'type': 'ordinal', 'sort':'x',
            "axis":{"title":'Month'}
            },
            'y': {'field': 'category', 'type': 'quantitative',
            "axis":{"title":'Number of crimes'}
            }}})
        
    else:
        st.write("Lucky you, no crimes found in this are for this date")