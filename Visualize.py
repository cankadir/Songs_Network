#%%
import pandas as pd
import networkx as nx
import os
from os import listdir
from os.path import isfile, join

import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
from netwulf import visualize

#import netwulf

# %% IMPORT DATA
#Data is also here 1958 - 2018 :https://raw.githubusercontent.com/cankadir/Songs_Network/main/data/results_1958.csv
mypath = r'D:\STORED\GIT_REPO\Songs_Network\data'
onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]

df = pd.DataFrame()
for _ in onlyfiles:
    temp = pd.read_csv( os.path.join(mypath,_) )
    df = df.append( temp )

df = df[df['pts_from']!='points received']
df.sample(5)
# %% Format Data
#Create Column for % of Votes received that year per country

df['pts_from'] = df['pts_from'].str.upper()
df['points_to'] = df['points_to'].str.upper()

df['pts_from'] = df['pts_from'].replace('-',' ' , regex = True )
df['points_to'] = df['points_to'].replace('-',' ' , regex = True )

total_score = df.groupby('year').sum()['pts'] #Total Points Each Year

dfn = pd.DataFrame()
for y in df['year'].unique():
    total = total_score[total_score.index == y ].tolist()[0] 
    temp = df[ df['year']== y ].copy()
    temp['n_pts'] = temp['pts'] / total
    dfn = dfn.append( temp )

dfn

#%% Geo Grouping
dfn = dfn[ ~dfn['points_to'].isin(['MONACO','MOROCCO']) ] # Joined the Competition to few times
dfn = dfn[ ~dfn['pts_from'].isin(['MONACO','MOROCCO']) ] 

#dfn['points_to'] = dfn['points_to'].replace( 'BOSNIA HERZEGOVINA' , 'BiH' )
#dfn['pts_from'] = dfn['pts_from'].replace( 'BOSNIA & HERZEGOVINA' , 'BiH' )

dfn['region'] = None
dfn.loc[ dfn['pts_from'].isin(['SWEDEN','DENMARK','NORWAY','FINLAND','ICELAND']) , 'region' ] = 'Scandinavia'
dfn.loc[ dfn['pts_from'].isin(['PORTUGAL','SPAIN','ITALY','GREECE']) , 'region' ] = 'Med'
dfn.loc[ dfn['pts_from'].isin(['TURKEY','ISRAEL','CYPRUS','MALTA']) , 'region' ] = 'EMed'
dfn.loc[ dfn['pts_from'].isin(['YUGOSLAVIA','RUSSIA','BOSNIA & HERZEGOVINA','SLOVENIA','CROATIA','POLAND','HUNGARY','ROMANIA','SLOVAKIA','NORTH MACEDONIA']) , 'region' ] = 'Eastern Eu'
dfn.loc[ dfn['pts_from'].isin(['FRANCE','BELGIUM','LUXEMBOURG','SWITZERLAND','GERMANY','AUSTRIA','THE NETHERLANDS']) , 'region' ] = 'Western Eu'
dfn.loc[ dfn['pts_from'].isin(['UNITED KINGDOM','IRELAND']) , 'region' ] = 'UK'
dfn.loc[ dfn['pts_from'].isin(['ESTONIA','LITHUANIA']) , 'region' ] = 'Baltic'

dfn

#%% Single Country Over Time
df2 = dfn[ dfn['year'] > 1970 ]

fig = go.Figure()
conts = df2['points_to'].unique().tolist()

down_list = []
for i in range(len(conts)):
    cont = conts[i]
    viz = [True if i==n else False for n in range(len(conts)) ]
    temp = df2[df2['points_to']== cont ]

    fig.add_trace(
        go.Scatter( 
            x= [temp['region'],temp['pts_from']], 
            y= temp['year'],
            mode='markers',
            text = temp['pts'],
            hovertemplate = 'Points: %{text:.0f}<extra></extra>',
            marker=dict(
                color = '#f4a261',
                opacity = 0.4,
                size= temp['pts']**1.3,
                line=dict(width=0)
            ),
            showlegend = False,
        )
    )

    down_list.append( #creates template to be used in button arguments
        dict(
            args = [dict( visible = viz)] ,
            label = cont.capitalize(),
            method="update"
        )
    )

fig.update_layout( # General Layout
    margin=dict(l=15, r=5, t=40, b=15),
    width = 600,
    height = 600,
    paper_bgcolor="#f6f6f6",
    plot_bgcolor="#f2f2f2",
    font_family="Open Sans",
    font_color="#5a5a5a",
    hoverlabel=dict( #Hover Styling
        bgcolor="#f6f6f6",
        font_size=9,
        font_family="Open Sans",
        font_color="#5a5a5a"
    )
    )

fig.update_layout( # Add dropdown
    updatemenus=[
        dict(
            active = 0,
            buttons = list(down_list) ,
            direction="down",
            pad={"r": 0, "t": 0},
            showactive=True,
            x=0.16,
            xanchor="left",
            y=1.25,
            yanchor="top"
        ),
    ],
    annotations=[
        dict(text="Select a Country:", showarrow=False,
        x=0, y=1.22, yref="paper", align="left")
        ]
    )

fig.update_yaxes(nticks=25 , range=[1965,2025])
fig.show()

# %%

import random

year = random.randint( dfn.year.min() , dfn.year.max() )
df1 = dfn[ dfn['year'] == year ]

G = nx.DiGraph()
for i,r in df1.iterrows():
    G.add_edge( r['pts_from'], r['points_to'] , weight = r['pts']**3 )

plt.figure(figsize=(18,12))
nx.draw(G, 
    pos = nx.spring_layout(G,iterations=1000), 
    with_labels=True,
    width= df['pts'].tolist() ,
    node_size= 200,
    edge_color="skyblue", style="solid",
    font_size=14,
    arrows=True,
    alpha=0.5,
    #node_color=carac['myvalue'], cmap=plt.cm.Blues 
    )

plt.title( str(year) )
plt.show()


# %%
