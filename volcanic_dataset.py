#libraries needed
import streamlit as st
import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
import seaborn as sns
import folium

import datetime

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
    df = pd.read_csv("https://raw.githubusercontent.com/ritmandotpy/volcanic_eruptions/master/eruption_list.csv", skiprows=1)

    df['Start Date'] = df.apply(lambda x: time_parser(x['Start Year'],x['Start Month'],x['Start Day']) , axis = 1)
    df['End Date'] = df.apply(lambda x: time_parser(x['End Year'],x['End Month'],x['End Day']) , axis = 1)
    df['lat']=df['Latitude']
    df['lon']=df['Longitude']
    #df['Eruption Duration'] =  df.apply(lambda x:eruption_duration(x['Start Date'],x['End Date']), axis = 1)


    df = df[['Volcano Number',
              'Volcano Name',
              'Eruption Number',
              'Eruption Category',
              'VEI',
              'Start Date',
              'End Date',
             # 'Eruption Duration',
              'Evidence Method (dating)',
              'Latitude',
              'Longitude',
              'lat',
              'lon']]

    return df

def main():
    df = load_data()
    page = st.sidebar.selectbox('Selecciona una casilla:',['Data','Mapa'])


    st.title('Data de erupciones volcánicas')

    ms = st.sidebar.multiselect("Columnas", df.columns.tolist(), default=['Volcano Name',
                                                                  'Eruption Category',
                                                                  'VEI',
                                                                  'Start Date',
                                                                  'End Date',
                                                                  #'Eruption Duration',
                                                                  'Evidence Method (dating)',
                                                                  'Latitude',
                                                                  'Longitude'])
    ms_pais= st.sidebar.multiselect("Filtrar por", ['País', 'Siglo', 'Tipo de volcán'])
    paises = st.sidebar.multiselect("Elije un volcán:", df['Volcano Name'].unique())
    filtered_df = df[ms].loc[df['Volcano Name'].isin(paises)]

    if page == 'Data':

        st.table(filtered_df)
        filtered_df['Latitude'][12]

    if page == 'Mapa':

        st.map(filtered_df)



if __name__ == '__main__':
    main()
