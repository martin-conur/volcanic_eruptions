#libraries needed
import streamlit as st
import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
import seaborn as sns
import datetime

def time_parser(year,month,day):
  #converts the columns year, month and day of the dataframe
  try:
    date = datetime.datetime(int(year), int(month), int(day)).strftime('%d/%m/%Y')
  except ValueError:
    try:
      date = datetime.datetime(int(year), int(month), 15).strftime('%d/%m/%Y')
    except ValueError:
      try:
        date = datetime.datetime(int(year), 6, 15).strftime('%d/%m/%Y')
      except ValueError:
        date = np.nan
  return pd.to_datetime(date, errors = 'coerce')

@st.cache
def load_data():
    df = pd.read_csv("https://raw.githubusercontent.com/ritmandotpy/volcanic_eruptions/master/eruption_list.csv", skiprows=1)

    # df['Start Date'] = df.apply(lambda x: time_parser(x['Start Year'],x['Start Month'],x['Start Day']) , axis = 1)
    # df['End Date'] = df.apply(lambda x: time_parser(x['End Year'],x['End Month'],x['End Day']) , axis = 1)
    # df['Eruption Duration'] =  df.apply(lambda x: x['End Date']-x['Start Date'], axis = 1)


    df = df[['Volcano Number',
              'Volcano Name',
              'Eruption Number',
              'Eruption Category',
              'VEI',
              'Start Year',
              'Start Month',
              'End Year',
              'End Month',
              #'Start Date',
              #'End Date',
              #'Eruption Duration',
              'Evidence Method (dating)',
              'Latitude',
              'Longitude']]

    return df

def main():
    df = load_data()
    page = st.sidebar.selectbox('Selecciona una casilla:',['Data','Gráfico'])

    if page == 'Data':
        st.title('Data de erupciones volcánicas')

        ms = st.multiselect("Columnas", df.columns.tolist(), default=df.columns.tolist())

        paises = st.multiselect("Elije un volcán:", df['Volcano Name'].unique())
        st.table(df[ms].loc[df['Volcano Name'].isin(paises)])

    if page == 'Gráfico':
        df[ms]


if __name__ == '__main__':
    main()
