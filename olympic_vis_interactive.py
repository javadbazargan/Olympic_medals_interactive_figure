import pandas as pd 
import numpy as np


data_medals = pd.read_csv('olympic_medals.csv')


""" # preparing dataframe 

*first we want to add seasons to medal data frame

*secondly,for making year range slider , I need a column just for years attributed to medals.

thirdly ,in this dataset for GameTeams there is an issue which should be addressed ; As an example if we have two athletes in a team , the data frame have considered two medals but for every team we should count them as one medal, so we must to revise it to have an accurate hist plot of medals .
"""


""" ### Adding seasons column to data frame
we need olympic games with seasons which is accessible on another data frame , 'olympic_hosts'"""
data_hosts=pd.read_csv('olympic_hosts.csv')
summers = list(data_hosts[data_hosts['game_season']=='Summer']['game_slug'])
winters =list( data_hosts[data_hosts['game_season']=='Winter']['game_slug'])


data_medals.insert(2 ,'seasons' ,data_medals['slug_game'] , True) 
data_medals['seasons']=data_medals['seasons'].isin(winters)
data_medals['seasons']=np.where(data_medals['seasons']==True , 'Winter' , 'Summer')
''' I've employed game_slug column from data_hosts and set a new column in data_medals 
to which game_slugs were in winters category in data_host then put it True and after that replace True by Winter in data_medals  '''


''' ### Adding a column just for years'''
years = data_medals['slug_game'].str.extract('(\d+)', expand=False)
data_medals.insert(3 ,'Years' ,years , True)


''' in this dataset,  for some past years ,Germany country name came in two different names
We replace them with "Germany" as the Olympic aspect '''
Germany_names = {
     'German Democratic Republic (Germany)':'Germany', 
     'Federal Republic of Germany':'Germany' }
data_medals['country_name'] = data_medals['country_name'].replace(Germany_names)
 

'''### Revising repeated medals in Game Teams

we have two types participants :'Athlete' , 'GameTeam' and for athletes we know their exact name ,
but there are two categories in 'GameTeam' ,some whome have named team member
in each row by the same medal and we're going to reform them as one medal because 
they were in one team so one medal should be counted ,the others are NAN vlaues and if we notice
for any NAN values in participants have just one medal . so the second category doesn't need to be fixed .
'''
team = data_medals[data_medals['participant_type']=='GameTeam']
dt_columns =list(data_medals.columns)
basis =['athlete_full_name' , 'athlete_url']
l = [ele for ele in dt_columns if ele not in basis]
team_grouped = team[team['athlete_full_name'].notna()].groupby(l)['athlete_full_name'].agg(lambda x :set(x)).reset_index()
team_grouped['athlete_full_name']=team_grouped['athlete_full_name'].apply( lambda x : list(x))

solo = data_medals[data_medals['participant_type']=='Athlete']
team_grouped_nan=team = data_medals[data_medals['athlete_full_name'].isna()]
data_m = pd.concat([team_grouped_nan,team_grouped , solo], axis=0).reset_index(drop=True)

