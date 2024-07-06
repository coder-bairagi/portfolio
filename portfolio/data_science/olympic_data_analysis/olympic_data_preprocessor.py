import pandas as pd
import numpy as np
import os

# Get current working directory path
cwd_path = os.path.dirname(os.path.abspath(__file__))

# Reading csv files
athlete_events = pd.read_csv(os.path.join(cwd_path, "athlete_events.csv"))
noc_regions = pd.read_csv(os.path.join(cwd_path, "noc_regions.csv"))

def get_preprocess_data():
    # Extracting only summer olympic data
    global athlete_events, noc_regions
    athlete_events = athlete_events[athlete_events['Season'] == 'Summer']
    df = pd.merge(athlete_events, noc_regions, on='NOC',how='left')
    df.rename(columns={'region': 'Region', 'notes': 'Notes'}, inplace=True)
    df.drop_duplicates(inplace=True)
    df = pd.concat([df, pd.get_dummies(df['Medal'])], axis=1)
    return df

def extract_medal_tally(df, year="Overall", country="Overall"):
    flag = 0
    heading = ''
    df = df.drop_duplicates(subset=['Team', 'NOC', 'Games', 'Year', 'City', 'Sport', 'Event', 'Medal'])

    if year == "Overall" and country != "Overall":
        flag = 1
        df = df[df['Region'] == country]
    elif year != "Overall" and country == "Overall":
        df = df[df["Year"] == int(year)]
    elif year != "Overall" and country != "Overall":
        df = df[(df["Year"] == int(year)) & (df["Region"] == country)]

    if flag == 0:
        df = df.groupby('Region').sum()[['Gold', 'Silver', 'Bronze']].sort_values(by='Gold', ascending=False).reset_index()
    else:
        df = df.groupby('Year').sum()[['Gold', 'Silver', 'Bronze']].sort_values(by='Year').reset_index()

    df['Total'] = df[['Gold', 'Silver', 'Bronze']].sum(axis=1)
    return df

def extract_years_countries(df):
    years = df['Year'].unique().tolist()
    years.sort()
    years.insert(0, 'Overall')
    years_dict = []
    for year in years:
        years_dict.append({
            "label": year,
            "value": year
        })
    countries = df['Region'].dropna().unique().tolist()
    countries.sort()
    countries.insert(0, 'Overall')
    countries_dict = []
    for country in countries:
        countries_dict.append({
            "label": country,
            "value": country
        })
    return years_dict, countries_dict

def extract_top_stats(df):
    edition = df['Year'].nunique() - 1
    host = df['City'].nunique()
    sport = df['Sport'].nunique()
    event = df['Event'].nunique()
    nation = df['Region'].nunique()
    athlete = df['Name'].nunique()
    return {
        "edition": edition,
        "host": host,
        "sport": sport,
        "event": event,
        "nation": nation,
        "athlete": athlete,
    }

def get_data_over_yrs(df, col):
    region_over_yrs = df.drop_duplicates(subset=['Year', col])['Year'].value_counts().reset_index().sort_values('Year')
    region_over_yrs.rename(columns={'Year': 'Edition', 'count': 'Number of ' + col}, inplace=True)
    return region_over_yrs

def get_heatmap_data(df):
    temp_df = df.drop_duplicates(['Year', 'Event'])[['Year', 'Sport', 'Event']].sort_values('Year')
    temp_df = temp_df.groupby(['Year'])['Sport'].value_counts().reset_index()
    temp_df.rename(columns={'count': 'Number of Events'}, inplace=True)
    pivot_df = temp_df.pivot(index='Sport', columns='Year', values='Number of Events')
    pivot_df.fillna(0, inplace=True)
    return pivot_df

def get_medal_over_yrs(df, country):
    temp_df = df[df['Region'] == country]
    temp_df = temp_df.drop_duplicates(subset=['Year', 'City', 'Sport', 'Event', 'Medal', 'NOC', 'Team', 'Games'])
    # temp_df = temp_df.dropna(subset=['Medal'])
    temp_df = temp_df.groupby('Year')['Medal'].count().reset_index().sort_values('Year')
    return temp_df

def get_medal_heatmap_data(df, country):
    temp_df = df[df['Region'] == country]
    temp_df = temp_df.drop_duplicates(subset=['Year', 'City', 'Sport', 'Event', 'Medal', 'NOC', 'Team', 'Games'])
    # temp_df = temp_df.dropna(subset=['Medal'])
    temp_df = temp_df.pivot_table(index='Sport', columns='Year', values='Medal', aggfunc='count').fillna(0)
    return temp_df

def get_most_successful(df, country):
    temp_df = df[df['Region'] == country]
    temp_df = temp_df.dropna(subset=['Medal'])
    temp_df = temp_df.pivot_table(index='Name', columns='Medal', aggfunc='size', fill_value=0)
    for medal in ['Gold', 'Silver', 'Bronze']:
        if medal not in temp_df.columns:
            temp_df[medal] = 0
    temp_df['Medal'] = temp_df.sum(axis=1)
    temp_df = temp_df.sort_values(by=['Medal', 'Gold', 'Silver', 'Bronze'], ascending=[False, False, False, False]).reset_index()
    temp_df = temp_df.rename(columns={'Name': 'Athlete Name', 'Bronze': 'Bronze Medal', 'Gold': 'Gold Medal', 'Silver': 'Silver Medal', 'Medal': 'Total Medal'})
    temp_df = temp_df[['Athlete Name', 'Gold Medal', 'Silver Medal', 'Bronze Medal', 'Total Medal']][0:10]
    return temp_df

def get_winner_df(df):
    winner_df = df.dropna(subset=['Medal'])
    winner_df = winner_df.dropna(subset=['Age'])
    return winner_df

def get_age_probdist(winner_df):
    x = [winner_df[winner_df['Medal'] == 'Gold']['Age'].tolist(), winner_df[winner_df['Medal'] == 'Silver']['Age'].tolist(), winner_df[winner_df['Medal'] == 'Bronze']['Age'].tolist()]
    medals = winner_df['Medal'].unique().tolist()
    return x, medals

def get_winners_age_bysport(df, sports):
    x = []
    sports_list = []
    for sport in sports:
        winners_age = df[df['Sport'] == sport]['Age'].tolist()
        if len(winners_age) > 5:
            # Only taking list with suitable data points to create kde
            x.append(winners_age)
            sports_list.append(sport)
    return {
        'winners_age': x,
        'sports_list': sports_list
    }

def age_sport_probdist(winner_df):
    gold_winners_df = winner_df[winner_df['Medal'] == 'Gold']
    sports_list = gold_winners_df['Sport'].unique().tolist()
    x = get_winners_age_bysport(gold_winners_df, sports_list)
    return x

def fill_height_weight(winner_df):
    h_mean = round(winner_df['Height'].mean(), 2)
    w_mean = round(winner_df['Weight'].mean(), 2)
    winner_df['Height'] = winner_df['Height'].replace(np.nan, h_mean)
    winner_df['Weight'] = winner_df['Weight'].replace(np.nan, w_mean)
    return winner_df

def get_male_female(df):
    mf = pd.get_dummies(df['Sex'])
    yr_df = df['Year'].to_frame()
    temp_df = pd.concat([yr_df, mf], axis=1)
    temp_df = temp_df.groupby('Year').agg({'F': 'sum', 'M': 'sum'}).reset_index()
    temp_df.columns = ['Year', 'Female', 'Male']
    return temp_df