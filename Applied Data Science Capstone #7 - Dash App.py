# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()


# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                # dcc.Dropdown(id='site-dropdown',...)
                                dcc.Dropdown(id="site-dropdown", options=[
                                {"label":"All Sites", "value":"ALL"},
                                {"label":"CCAFS LC-40", "value":"CCAFS LC-40"},
                                {"label":"CCAFS SLC-40", "value":"CCAFS SLC-40"},
                                {"label":"KSC LC-39A", "value":"KSC LC-39A"},
                                {"label":"VAFB SLC-4E", "value":"VAFB SLC-4E"}], value="ALL",
                                placeholder="Select a launch site", searchable=True),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                #dcc.RangeSlider(id='payload-slider',...)
                                dcc.RangeSlider(id='payload-slider', min=0, max=10000, step=1000,
                                                marks={0: '0', 100:'100'}, value=[min_payload, max_payload]),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site):
    filtered_df = spacex_df
    if entered_site == "ALL":
        fig = px.pie(filtered_df, values='class', names='Launch Site', title='Total Successful Launches by Launch Site')
        return fig
    else:
        filtered_df = filtered_df[filtered_df["Launch Site"] == entered_site]
        success_counts = filtered_df[filtered_df['class'] == 1].groupby('Launch Site')['class'].count()
        failure_counts = filtered_df[filtered_df['class'] == 0].groupby('Launch Site')['class'].count()
        fig = px.pie(
            names=['Success', 'Failure'],
            values=[success_counts[entered_site], failure_counts[entered_site]],
            title='Success Rate by Launch Site',
            hole=.3,
            labels={'class': 'Success'})

        return fig
                        
# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(Output(component_id='success-payload-scatter-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'),
              Input(component_id='payload-slider', component_property='value'))
def payload_scatter(site_entered, payload_range):
    filtered_df = spacex_df
    payload_min = int(payload_range[0])
    payload_max = int(payload_range[1])
    if site_entered == "ALL":
      filtered_df = filtered_df[filtered_df["Payload Mass (kg)"].between(payload_min, payload_max)]
      fig = px.scatter(filtered_df, x="Payload Mass (kg)", y="class", color="Booster Version Category", title="Successful vs Unsuccessful for Payload Range")
      fig.update_layout(xaxis_title="Payload Mass", yaxis_title="Class")
      return fig
    else:
      filtered_df = filtered_df[(filtered_df["Launch Site"] == site_entered) & (filtered_df["Payload Mass (kg)"].between(payload_min, payload_max))]
      fig = px.scatter(filtered_df, x="Payload Mass (kg)", y="class", color="Booster Version Category", title="Successful vs Unsuccessful for Payload Range and Selected Site")
      fig.update_layout(xaxis_title="Payload Mass", yaxis_title="Class")
      return fig
      
    
# Run the app
if __name__ == '__main__':
    app.run_server(port=8061)