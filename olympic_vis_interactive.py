import pandas as pd 
import numpy as np
from  bokeh.models import Panel , Row , ColumnDataSource ,  MultiChoice
from bokeh.palettes import Category10_10
from  bokeh.plotting import Figure 
from bokeh.models.widgets import  RangeSlider , Tabs
from bokeh.layouts import Row,  WidgetBox  
from bokeh.io import curdoc 


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
data_medals['Years']=data_medals['Years'].astype(int)


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

'''FILTERING AND MAKING THE APPROPRIATE DATASET WITH md() FUNCTION TO BE DELIVERED TO mp() FUNCTION'''

def md(c , rs = 1896, re=2020 , s=['Wrestling'] , m =['GOLD']):
    
    # df3.insert(3 ,'colors',True)
    df1 = pd.DataFrame(columns =dt_columns)
    df2 = pd.DataFrame(columns =dt_columns) 
    for i , r_data in enumerate(m):
        subset= data_m[data_m['medal_type'] ==r_data]
        df1 = df1.append(subset)
    for j , f_data in enumerate(s) :
        s2ubset=df1[df1['discipline_title']==f_data]
        df2=df2.append(s2ubset)
    
    
    r = re - rs
    bin = 4
    d = pd.DataFrame(columns =[ 'proportion','left' ,'right' ,'name', 'color'])
    for k , l_data in enumerate(c) :
        p3ubset = df2[df2['country_name'] == l_data] 
        
        arr_hist , edge =np.histogram(p3ubset['Years'],  bins = int(r/bin) , range =[rs,re])
        arr_df = pd.DataFrame({'proportion':arr_hist , 'left':edge[:-1] , 'right':edge[1:]})
        arr_df['name'] = l_data
        arr_df['color'] = Category10_10[k]
        d=d.append(arr_df)
    d= d.sort_values(['name' , 'left'])    
    # type(data_medals['Years'])
    d = ColumnDataSource(d)
    return d

def mp(sh_data):

    p=Figure(height=570 , width= 570 , title='OLYMPIC MEDALSINTERACTIVE DASHBOARS BY COUNTRIES' ,  x_axis_label = 'YEARS',  y_axis_label = 'Nmuber of medals')

    p.xaxis.axis_label_text_font_size = '15pt'
    p.xaxis.axis_label_text_font_style = 'bold'
    p.yaxis.axis_label_text_font_size = '15pt'
    p.yaxis.axis_label_text_font_style = 'bold'
    p.quad(source=sh_data , bottom = 0 ,color = 'color',  fill_alpha=0.55 , top = 'proportion' , left = 'left' ,right= 'right' , legend ='name')

    
    return p

def update(attr , old , new) :
    countries =[x for x in chbox.value]
    disciplines = [s for s in chbox_s.value]
    medals = [m for m in chbox_m.value]
    nds  = md(countries ,range_slider.value[0] , range_slider.value[1] , disciplines , medals)

    src.data.update(nds.data)

cclist = list(set(data_medals['country_name']))
sslist = list(set(data_medals['discipline_title']))

chbox = MultiChoice (value=[], options=cclist , title  = 'COUNTRIES')
chbox.on_change("value", update)

chbox_s = MultiChoice(value=[] , options = sslist , title = 'DISCIPLINES')
chbox_s.on_change('value' , update)

chbox_m = MultiChoice(value=[] , options = ['GOLD' , 'BRONZE' , 'SILVER' ], title = 'MEDALS')
chbox_m.on_change('value' , update)

range_slider = RangeSlider(start = 1896 , end=2022 , value = (1896 , 2022) , step=4, title='YEARS')
range_slider.on_change('value', update)


init_data= [x for x in chbox.value] 
init_d = [s for s in chbox_s.value]
src = md(init_data , rs = 1896, re=2020 , s=['Wrestling'] , m =['GOLD'])
pp= mp(src)

w = WidgetBox(chbox, chbox_s,chbox_m,  range_slider)    

l=Row(children=[w, pp])
tab = Panel(child = l , title = 'Olympic Games')
tabs = Tabs(tabs=[tab])

# Add it to the current document (displays plot)
curdoc().add_root(tabs)