# -*- coding: utf-8 -*-
"""
Created on Mon May 10 22:45:36 2021

@author: Carlo
"""

import pandas as pd
import numpy as np

dataset_path = 'C:/Users/Carlo/Documents/GitHub/FootPlus/Preprocessed_data/Global_Fish_Watch/Global_watch_fish_vessels_PREPROCESSED.csv'

df = pd.read_csv(dataset_path)

year_columns = [column for column in df.columns if "fishing_hours" in column]
df_years = df[year_columns]

total_hours_per_year_series= df_years.sum(axis=0)
years = [year[-4:] for year in total_hours_per_year_series.index]
total_hours = total_hours_per_year_series.values

avg_hours_per_year_series =  df_years.mean(axis=0)
avg_hours = avg_hours_per_year_series.values


#%%

vessels_df = df.groupby(by = 'mmsi').any().astype(int)

year_columns = [column for column in df.columns if "fishing_hours" in column]
vessels_df = vessels_df[year_columns]

total_vessels_per_year_series= vessels_df.sum(axis=0)
years = [year[-4:] for year in total_vessels_per_year_series.index]
total_vessels = total_vessels_per_year_series.values


#%%
    
energy_columns_list = ['CO2_2012', 'CO2_2013', 'CO2_2014', 'CO2_2015', 'CO2_2016', 'CO2_2017',
                      'CO2_2018', 'CO2_2019', 'CO2_2020']
fishing_hours_list = ['fishing_hours_2012', 'fishing_hours_2013', 'fishing_hours_2014', 'fishing_hours_2015', 'fishing_hours_2016',
                      'fishing_hours_2017', 'fishing_hours_2018', 'fishing_hours_2019', 'fishing_hours_2020']

for energy_column, fishing_hours_column in zip(energy_columns_list, fishing_hours_list):
    # https://www.epa.gov/energy/greenhouse-gases-equivalencies-calculator-calculations-and-references
    # conversion formula
    # result in metric tons of CO2 emissions 
    
    df[energy_column] = (df['engine_power_kw_gfw'].fillna(0) * df[fishing_hours_column].fillna(0)) * (7.09e-4)
    
    
    
    
CO2_columns = [column for column in df.columns if "CO2" in column]
CO2_df = df[CO2_columns]

total_CO2_per_year_series= CO2_df.sum(axis=0)
years = [year[-4:] for year in total_vessels_per_year_series.index]
print(years)
total_CO2 = total_CO2_per_year_series.values

#%%

hours_per_nation_df = df.groupby(by='flag_gfw').sum()
year_columns = [column for column in df.columns if "CO2" in column]
hours_per_nation_df = hours_per_nation_df[year_columns].reset_index()

hours_per_nation_df = pd.melt(hours_per_nation_df, id_vars = ['flag_gfw'], var_name = "year", value_name = "CO2_emission")
hours_per_nation_df['year'] = hours_per_nation_df['year'].str[-4:]

hours_per_nation_df['CO2_emission_log'] = hours_per_nation_df['CO2_emission'].apply(lambda x: np.log(x) if x!= 0 else x)
hours_per_nation_df




#%%

hours_per_nation_df = hours_per_nation_df.pivot(index="flag_gfw",columns="year", values='CO2_emission') \
       .reset_index().rename_axis(None, axis=1)
       #hours_per_nation_df = hours_per_nation_df.astype(int)


#%%

df_pop = pd.read_excel('C:/Users/Carlo/Documents/GitHub/FootPlus/Raw_Data/data.worldbank.org/API_SP.POP.TOTL_DS2_en_excel_v2_2252578.xls',
                       sheet_name='Data', skiprows=3)

df_pop_last = df_pop[['Country Name', 'Country Code', '2019']]


df_merge = pd.merge(hours_per_nation_df, df_pop_last[['Country Name', 'Country Code']], how='left', left_on='flag_gfw', right_on='Country Code')
df_merge = df_merge.rename(columns={'Country Name': 'Country'}).drop(columns='Country Code')

df_merge = df_merge.set_index('Country')

df_merge.to_excel('C:/Users/Carlo/Documents/GitHub/FootPlus/bar_race.xlsx')

#%%
import matplotlib.pyplot as plt
import bar_chart_race as bcr
import warnings
warnings.filterwarnings('ignore')


SUB = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")

# fig = plt.figure()
# ax = fig.add_subplot(1, 1, 1)
# ax.set_facecolor('white')

bcr.bar_chart_race(filename='C:/Users/Carlo/Documents/GitHub/FootPlus/ehi.mp4', 
                   df = hours_per_nation_df, 
                   title = "CO2 emissions (metric tons CO2/kWh)".translate(SUB), 
                   n_bars=10, 
                   steps_per_period = 50, 
                   interpolate_period=False, 
                   dpi=144, 
                   period_length=1500,
                   period_label={'x': .99, 'y': .2,
                                 'ha': 'right','va': 'center'},
                   cmap="paired",
                   filter_column_colors=True,
                   # fig=fig
                   )



