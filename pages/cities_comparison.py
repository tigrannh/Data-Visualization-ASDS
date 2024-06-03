import dash
from dash import Dash, dcc, html, Input, Output, callback
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import pandas as pd

dash.register_page(__name__, path="/")

data = pd.read_csv('data/Airbnb_Texas_Rentals.csv', index_col=0)
data['average_rate_per_night_dollar'] = data['average_rate_per_night'].apply(lambda row: None if pd.isna(row) else row[1:]).values
data['average_rate_per_night_dollar'] = data['average_rate_per_night_dollar'].astype('float64')
data['bedrooms_count_int'] = data['bedrooms_count'].replace('Studio', '0').astype('float64')
data['city_chng'] = data['city'].str.lower().str.strip().values
data['month'] = data['date_of_listing'].apply(lambda row: row.split(' ')[0]).astype(str).values
data['year'] = data['date_of_listing'].apply(lambda row: row.split(' ')[1]).astype(int).values
data['latitude'] = data['latitude'].astype('float64')
data['longitude'] = data['longitude'].astype('float64')

layout = html.Div([
    html.Div([
        html.H1("City Comparison", id="page-3"),
        dcc.Dropdown(
            id='city1-dropdown',
            options=[{'label': city, 'value': city} for city in data['city'].unique()],
            value=data['city'].unique()[0]
        ),
        dcc.Dropdown(
            id='city2-dropdown',
            options=[{'label': city, 'value': city} for city in data['city'].unique()],
            value=data['city'].unique()[1]
        ),
        dcc.Graph(id='city-comparison-plot'),
    ], id='page-3-container')
])


@callback(
    Output('city-comparison-plot', 'figure'),
    [Input('city1-dropdown', 'value'),
     Input('city2-dropdown', 'value')]
)
def update_city_comparison(city1, city2):
    filtered_data1 = data[data['city'] == city1].sort_values('bedrooms_count')
    filtered_data2 = data[data['city'] == city2].sort_values('bedrooms_count')

    bedroom_counts = filtered_data1['bedrooms_count'].unique()

    fig = make_subplots(rows=len(bedroom_counts), cols=1, subplot_titles=[f'Bedrooms: {count}' for count in bedroom_counts])
    fig.update_layout(height=800, width=1200, title_text=f'Cities Comparison: {city1} vs {city2}',
                      yaxis_title='Average Rate per Night (Dollar)')

    for i, count in enumerate(bedroom_counts):
        filtered_data1_bedroom = filtered_data1[filtered_data1['bedrooms_count'] == count]
        filtered_data2_bedroom = filtered_data2[filtered_data2['bedrooms_count'] == count]

        fig.add_trace(go.Bar(
            x=[city1],
            y=[filtered_data1_bedroom['average_rate_per_night_dollar'].mean()],
            name=city1,
            marker=dict(color='rgb(158,202,225)'),
        ), row=i+1, col=1)

        fig.add_trace(go.Bar(
            x=[city2],
            y=[filtered_data2_bedroom['average_rate_per_night_dollar'].mean()],
            name=city2,
            marker=dict(color='rgb(50, 171, 96)'),
        ), row=i+1, col=1)

    fig.update_xaxes(title_text='City', row=len(bedroom_counts), col=1)
    fig.update_yaxes(matches='y')

    return fig
