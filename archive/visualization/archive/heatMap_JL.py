
import pandas as pd
import plotly
import plotly.graph_objs as go
import plotly.offline as offline
from plotly.graph_objs import *
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot

import plotly.graph_objects as go

import pandas as pd
df = pd.read_csv('data/denial_overall_jl.csv')

df = df[df.year==2017]

for col in df.columns:
  df[col] = df[col].astype(str)

df['text'] = df['year'] + df['state'] + df['denRate'] 

print(df)

fig = go.Figure(data=go.Choropleth(
  locations=df['state'],
  z=df['denRate'].astype(float),
  locationmode='USA-states',
  colorscale='Reds',
  autocolorscale=False,
  text=df['text'], # hover text
  marker_line_color='white', # line markers between states
  colorbar_title="Millions USD"
))

fig.update_layout(
  title_text='2017 Loan Denial Rate',
  geo = dict(
  scope='usa',
  projection=go.layout.geo.Projection(type = 'albers usa'),
  showlakes=True, # lakes
  lakecolor='rgb(255, 255, 255)'),
)

fig.show()
