import streamlit as st
import requests
import seaborn as sns
import pandas as pd
import numpy as np



@st.cache
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




### MAIN PAGE
def write(postcode, poly, available, code):

    st.title(f"Crime statistics for neighbourhood around {postcode.upper()}")

    date = st.selectbox(
    'What month do you want to explore?',
    list(available)
    )

    st.markdown("The most common crimes in your area for the date selected are:")

    df = fetch_data(poly,date)

    # Building palette so that bar plot matches map colours. Need the colour values both in RGB and Hex. The seaborn library makes this really easy
    pal_df = pd.DataFrame({'category':df['category'].unique(),\
        'hex_palette': sns.color_palette('hls',len(df['category'].unique())).as_hex(),\
        'rgb_palette': sns.color_palette('hls',len(df['category'].unique()))})
    pal_df['rgb_palette'] = pal_df['rgb_palette'].apply(lambda x: [y*255 for y in x])

    df = df.merge(pal_df, on='category', how='left')
    df['colorR'] = [x[0] for x in df['rgb_palette']]
    df['colorG'] = [x[1] for x in df['rgb_palette']]
    df['colorB'] = [x[2] for x in df['rgb_palette']]
    bar_data = df['category'].value_counts(normalize=True).reset_index().merge(pal_df, left_on = 'index', right_on='category')
    if len(df) > 0:
        # Write bar chart
        st.markdown(f"Total number of crimes: {len(df)}")
        st.vega_lite_chart(bar_data, {
        'title': 'Percentage of total crimes per crime type',
        'width':600,
        'height':100,
        'mark': 'bar',
        'encoding': {
            'x': {'field': 'index', 'type': 'nominal', 'sort':'-y',
            "axis":{"title":'Crime Category'}
            },
            'y': {'field': 'category_x', 'type': 'quantitative',
            "axis":{"title":'Number of crimes'}
            },
            "color": {
            "field": "hex_palette", "type": "nominal", "scale" : None,
            "legend":None
        }}})

        crime_type = st.multiselect('Select the list of crimes you\'d like to filter by',
                                    list(df.category.unique()), list(df.category.unique()))

        st.markdown(f"Number of crimes in selected categories: {df[df['category'].isin(crime_type)].shape[0]}")
        st.markdown("The colours in the map below match the colour of the crime type in the bar plot")

        # Build map
        st.deck_gl_chart(
            viewport={
                'latitude':code[0],
                'longitude':code[1],
                'zoom':12
            },
            layers = [{
            'data': df[df['category'].isin(crime_type)],
            'type': 'ScatterplotLayer',
            'radiusScale':0.1,
            'pickable':True
        }])
        st.markdown('Scatterplot will not automatically centre to the new postcode as it is not currently supported, please move manually to observe the crimes in the area.')

        df_o = df[df['category'].isin(crime_type)]['last_outcome'].value_counts(normalize=True).reset_index()

        st.vega_lite_chart(df_o, {
        'title': 'Distribution of outcomes per crime type',
        'width':500,
        'height':100,
        'mark': 'bar',
        'encoding': {
            'y': {'field': 'index', 'type': 'nominal', 'sort':'-x',
            "axis":{"title":'Outcome'}
            },
            'x': {'field': 'last_outcome', 'type': 'quantitative',
            "axis":{"title":'Percentage of total'}
            }
        }})
    else:
        st.write("Lucky you, no crimes found in this are for this date")