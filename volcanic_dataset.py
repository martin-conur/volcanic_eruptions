#libraries needed
import streamlit as st
import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

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
    #eruption list
    df = pd.read_csv("https://raw.githubusercontent.com/ritmandotpy/volcanic_eruptions/master/eruption_list.csv", skiprows=1, index_col='Eruption Number')

    df['Start Date'] = df.apply(lambda x: time_parser(x['Start Year'],x['Start Month'],x['Start Day']) , axis = 1)
    df['End Date'] = df.apply(lambda x: time_parser(x['End Year'],x['End Month'],x['End Day']) , axis = 1)
    df['lat']=df['Latitude'].apply(lambda x: np.round(x,3))
    df['lon']=df['Longitude'].apply(lambda x: np.round(x,3))
    #df['Eruption Duration'] =  df.apply(lambda x:eruption_duration(x['Start Date'],x['End Date']), axis = 1)


    df = df[['Volcano Number',
              'Volcano Name',
              #'Eruption Number',
              'Eruption Category',
              'VEI',
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

    return df, events,references

def main():
    df, events, references = load_data()

    st.title('DATASET MUNDIAL DE VOLCANES Y ERUPCIONES')

    ms_filter= st.multiselect("Filtrar por", ['País', 'Periodo de tiempo', 'Tipo de volcán',''])
    if 'País' in ms_filter:
        st.multiselect('Elige un país',["Chile"])
    if 'Periodo de tiempo' in ms_filter:
        st.text("Ingresa un rango de tiempo")
        anno_min = st.number_input("Año Mínimo:", min_value=-5000, max_value=2020, value=0)
        anno_max = st.number_input("Año Máximo:", min_value=-5000, max_value=2020, value = 2020)



    volcanes = st.multiselect("Elije un volcán:", df['Volcano Name'].unique())
    filtered_df = df.loc[df['Volcano Name'].isin(volcanes)]

    def header(): #prints the names of volcanes
        texto=""
        for i,volcan in enumerate(volcanes):
            texto+= str(i+1)+') '+str(volcan)+'  '
        return texto

    st.header(header())





    mapcheck= st.button("Visualizar en mapa")
    st.table(filtered_df)
    if mapcheck == True:
        px.set_mapbox_access_token('pk.eyJ1Ijoicml0bWFuZG90cHkiLCJhIjoiY2s3ZHJidGt0MDFjNzNmbGh5aDh4dTZ0OSJ9.-SROtN91ZvqtFpO1nGPFeg')
        px.scatter_mapbox(filtered_df, lat="lat", lon="lon", text= 'Volcano Name', zoom=5).show()

    procesos_check=st.multiselect("Ingresa el índice (Número a la izquierda) para ver los procesos volcánicos asociados a esa erupción",
                                          filtered_df.index)
    st.write("Procesos volcánicos asociados a la erupción id: {}".format(procesos_check))
    st.write(events['Event Type'].loc[events['Eruption Number'].isin(procesos_check)])

    ref= st.checkbox("Mostrar referencias")

    if ref == True:
        st.table(references.loc[references['Volcano Number'].isin(filtered_df['Volcano Number'])].sort_values(by='Publication Year'))





if __name__ == '__main__':
    main()
