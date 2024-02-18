# Import required libraries
import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the SpaceX data into a pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a Dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),
    
    dcc.Dropdown(
        id='site-dropdown',
        options=[
            {'label': 'All Sites', 'value': 'All Sites'},
            {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
            {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'},
            {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
            {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'}
        ],
        placeholder='Select a Launch Site Here',
        value='All Sites',
        searchable=True
    ),

    html.Div(dcc.Graph(id='success-pie-chart')),
    
    html.P("Payload range (Kg):"),
    
    dcc.RangeSlider(
        id='payload-slider',
        min=0,
        max=10000,
        step=1000,
        marks={i: '{}'.format(i) for i in range(0, 10001, 1000)},
        value=[min_payload, max_payload]
    ),

    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# Callback for `success-pie-chart`
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def get_pie_chart(selected_site):
    if selected_site == 'All Sites':
        fig = px.pie(
            values=spacex_df.groupby('Launch Site')['class'].mean(),
            names=spacex_df.groupby('Launch Site')['Launch Site'].first(),
            title='Total Success Launches by Launch Site'
        )
    else:
        fig = px.pie(
            values=spacex_df[spacex_df['Launch Site']==str(selected_site)]['class'].value_counts(normalize=True),
            names=spacex_df['class'].unique(),
            title='Success Launches Distribution for Launch Site {}'.format(selected_site)
        )
    return fig

# Callback for `success-payload-scatter-chart`
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')]
)
def get_payload_chart(selected_site, payload_mass):
    if selected_site == 'All Sites':
        fig = px.scatter(
            spacex_df[spacex_df['Payload Mass (kg)'].between(payload_mass[0], payload_mass[1])],
            x="Payload Mass (kg)",
            y="class",
            color="Booster Version Category",
            hover_data=['Launch Site'],
            title='Correlation Between Payload and Launch Success for All Sites'
        )
    else:
        df = spacex_df[spacex_df['Launch Site']==str(selected_site)]
        fig = px.scatter(
            df[df['Payload Mass (kg)'].between(payload_mass[0], payload_mass[1])],
            x="Payload Mass (kg)",
            y="class",
            color="Booster Version Category",
            hover_data=['Launch Site'],
            title='Correlation Between Payload and Launch Success for Launch Site {}'.format(selected_site)
        )
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server()
