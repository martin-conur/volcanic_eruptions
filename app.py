#libraries needed
import streamlit as st
import pandas as pd
import numpy as np

import plotly.express as px

import datetime
import glob
import re

def time_parser(year,month,day):
  #converts the columns year, month and day of the dataframe
  if year >=0:
      try:
        date = datetime.datetime(int(year), int(month), int(day)).strftime('%Y/%m/%d')
      except ValueError:
        try:
          date = datetime.datetime(int(year), int(month), 15).strftime('%Y/%m/%d')
        except ValueError:
          try:
            date = datetime.datetime(int(year), 6, 15).strftime('%Y/%m/%d')
          except ValueError:
            date = np.nan

  elif year < 0:
      date = str(int(abs(year)))+' BC'

  else:
      date = np.nan

  return date

def eruption_duration(start_date,end_date):
    try:
        duration = end_date - start_date
    except ValueError:
        duration = np.nan
    return duration

@st.cache
def load_data():
    #eruption list
    df = pd.read_csv("https://raw.githubusercontent.com/ritmandotpy/volcanic_eruptions/master/eruption_list.csv", skiprows=1)
    df['Start Date'] = df.apply(lambda x: time_parser(x['Start Year'],x['Start Month'],x['Start Day']) , axis = 1)
    df['End Date'] = df.apply(lambda x: time_parser(x['End Year'],x['End Month'],x['End Day']) , axis = 1)
    df['lat']=df['Latitude'].apply(lambda x: np.round(x,3))
    df['lon']=df['Longitude'].apply(lambda x: np.round(x,3))
    df = df.fillna('-')

    #df['Eruption Duration'] =  df.apply(lambda x:eruption_duration(x['Start Date'],x['End Date']), axis = 1)


    df = df[['Volcano Number',
              'Volcano Name',
              'Eruption Number',
              'Eruption Category',
              'VEI',
              'Start Year',
              'Start Date',
              'End Date',
             # 'Eruption Duration',
              'Evidence Method (dating)',
              'lat',
              'lon']]



    #events
    events = pd.read_csv("https://raw.githubusercontent.com/ritmandotpy/volcanic_eruptions/master/events.csv", skiprows=1)

    #references
    references = pd.read_csv("https://raw.githubusercontent.com/ritmandotpy/volcanic_eruptions/master/references.csv", skiprows=1)

    holocene = pd.read_csv(glob.glob('*Holocene*')[0], skiprows=1, engine='python' )
    #formatting holocene
    #holocene['Primary Volcano Type'] = holocene['Primary Volcano Type'].apply(lambda x: )


    return df, events,references, holocene

def main():
    df, events, references, holocene = load_data()

    st.sidebar.title("Earth's Volcanoes Library")
    page = st.sidebar.selectbox("¿Which data do you want to visualize?",['Map','Basic information','Eruptions','Volcanic Processes','References'])

    ms_filter= st.sidebar.selectbox("Filter by:", ['Region','Country','Primary Volcano Type','Elevation (m)','Tectonic Setting'])

    #filter by region (pseudo continent)
    if 'Region' in ms_filter:
        regions=st.sidebar.multiselect('Choose a region:', holocene.sort_values(by='Region')['Region'].unique())
        regions_volc_number = holocene.loc[holocene['Region'].isin(regions)]['Volcano Number']
        df = df.loc[df['Volcano Number'].isin(regions_volc_number)]

    #filter by country
    if 'Country' in ms_filter:
        countries = st.sidebar.multiselect('Choose a country:',holocene.sort_values(by='Country')['Country'].unique())
        countries_volc_number = holocene.loc[holocene['Country'].isin(countries)]['Volcano Number']
        df = df.loc[df['Volcano Number'].isin(countries_volc_number)]

    #filter by volcano type
    if 'Primary Volcano Type' in ms_filter:
        types = st.sidebar.multiselect('Choose a Primary Volcano Type:',holocene.sort_values(by='Primary Volcano Type')['Primary Volcano Type'].unique())
        types_volc_number = holocene.loc[holocene['Primary Volcano Type'].isin(types)]['Volcano Number']
        df = df.loc[df['Volcano Number'].isin(types_volc_number)]

    #filter by elevation
    if 'Elevation (m)' in ms_filter:
        #elevations as a series
        elevation = holocene['Elevation (m)']
        #default max and min value
        min_value = min(elevation)
        max_value = max(elevation)
        #slider between min and max
        elev_slider =st.sidebar.slider("Elevation (m) range:",min_value=min_value,max_value=max_value, value=[min_value,max_value])
        #selected values of the slider
        selected_min_val = elev_slider[0]
        selected_max_val = elev_slider[1]
        #filtering in the holocene dataframe and getting just the volcanic number
        elev_volc_number = holocene.loc[(holocene['Elevation (m)']>=selected_min_val)&(holocene['Elevation (m)']<=selected_max_val)]['Volcano Number']
        df = df.loc[df['Volcano Number'].isin(elev_volc_number)]


    #filter by tectonic setting
    if 'Tectonic Setting' in ms_filter:
        tectonics = st.sidebar.multiselect('Choose a Tectonic Setting:',holocene.sort_values(by='Tectonic Setting')['Tectonic Setting'].unique())
        tectonics_volc_number = holocene.loc[holocene['Tectonic Setting'].isin(tectonics)]['Volcano Number']
        df = df.loc[df['Volcano Number'].isin(tectonics_volc_number)]




    volcanes = st.sidebar.multiselect("Choose a volcano: (default: All selected)", sorted(df['Volcano Name'].unique()))

    filtered_df = df.loc[df['Volcano Name'].isin(volcanes)]
    if len(filtered_df)==0: #if there's nothing selected yet plot everything
        filtered_df = df
        zoom=1


    #plot the map
    if page == 'Map':

        #setting the zoom dending on the number of volcanoes selected
        if len(volcanes)>1:
            zoom=2
        elif len(volcanes)== 1:
            zoom=6



        px.set_mapbox_access_token('pk.eyJ1Ijoicml0bWFuZG90cHkiLCJhIjoiY2s3ZHJidGt0MDFjNzNmbGh5aDh4dTZ0OSJ9.-SROtN91ZvqtFpO1nGPFeg')
        fig = px.scatter_mapbox(filtered_df, lat="lat", lon="lon", text= 'Volcano Name', zoom=zoom, title='Volcanoes')
        fig.update_layout(
                        autosize=True,
                        width=700,
                        height=500,
                         margin=dict(
                                    l=0,
                                    r=0,
                                    b=0,
                                    t=0,
                                    pad=0
                                ))
        fig.update_yaxes(automargin=True)
        fig.update_xaxes(automargin=True)
        #plotting the map
        st.plotly_chart(fig)

    #show the dataframe
    filtered_df = filtered_df.set_index(filtered_df['Volcano Name']).drop(columns=['Volcano Name'])

    if page == 'Basic information':
        #getting the volcano(es) number(s)
        volcano_info=holocene.loc[holocene['Volcano Number'].isin(filtered_df['Volcano Number'])]
        volcano_info = volcano_info.set_index(volcano_info['Volcano Name']).drop(columns=['Volcano Name','Volcano Number'])
        #showing the dataframe
        if len(volcano_info)>5:
            st.table(volcano_info)
        else:
            st.table(volcano_info.T)



    if page == 'Eruptions':
        st.table(filtered_df.loc[:,filtered_df.columns != 'Start Year'].drop(columns=['Volcano Number','lat','lon']))#hides the Start Year column


    if page == 'Volcanic Processes':
        #event types
        procesos_check=st.multiselect("Choose the eruption's date (ALL by default)",
                                              filtered_df['Start Date'].unique())#by date of eruption

        date_to_erupnumber=filtered_df.loc[filtered_df['Start Date'].isin(procesos_check)]['Eruption Number']

        if len(procesos_check)==0:#if you havent selected anything yet
            filtered_events = events.loc[events['Volcano Number'].isin(filtered_df['Volcano Number'])]#show everything
        else:
            filtered_events = events.loc[events['Eruption Number'].isin(date_to_erupnumber)]#show selected

        if len(filtered_events.set_index(filtered_events['Volcano Name'])['Event Type'])==0:#if there's no records
            st.write("There's no information")
        else:#if there are records indeed
            unique_filtered_events = pd.unique(filtered_events.set_index(filtered_events['Volcano Name'])['Event Type'])
            st.table(sorted(unique_filtered_events))

    if page == 'References':

        refs_order_by= st.selectbox("Filter by:", ['Publication Year', 'Volcano Name'])
        filtered_refs=references.loc[references['Volcano Number'].isin(filtered_df['Volcano Number'])].sort_values(by=refs_order_by)
        filtered_refs = filtered_refs.set_index(filtered_refs['Volcano Name']).drop(columns=['Volcano Name','Volcano Number'])
        st.table(filtered_refs.fillna('-'))

    st.sidebar.markdown("...")
    st.sidebar.markdown(""">*About: This site was created and is frequently maintained by a [chilean geologist](https://twitter.com/RitmanDotpy) who loves all volcanic creatures.
                        This site and all its data is Public and Open Source.*""")
    st.sidebar.markdown("...")
    st.sidebar.markdown(">**Source**: *[Smithsonian Institution National Museum of Natural History Global Volcanism Program](http://volcano.si.edu/)* ")


if __name__ == '__main__':
    main()
