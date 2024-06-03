import dash
from dash import Dash, dcc, html, Input, Output, callback
import plotly.express as px
import pandas as pd

dash.register_page(__name__)


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
    html.Nav([
        html.Ul([
            html.Li(html.A("Overview", href="#page-1")),
            html.Li(html.A("Detailed Visualizations", href="#page-2")),
        ])
    ]),

    html.Div([
        html.H1("Airbnb Data Overview", id="page-1"),
        html.Div([
            html.Div([
                html.H2("Average Rate per Night"),
                dcc.Graph(id='avg_rate_per_night'),
            ], className="six columns"),
            html.Div([
                html.H2("Bedrooms Count"),
                dcc.Graph(id='bedrooms_count'),
            ], className="six columns"),
        ], className="row"),
    ], id='page-1-container'),

    html.Div([
        html.H1("Detailed Visualizations", id="page-2"),
        dcc.Dropdown(
            id='city-dropdown',
            options=[{'label': city, 'value': city} for city in data['city'].unique()],
            value=data['city'].unique()[0]
        ),
        dcc.Graph(id='map-plot'),
        html.Div(id='selected-property')
    ], id='page-2-container'),
])

@callback(
    [Output('avg_rate_per_night', 'figure'),
     Output('bedrooms_count', 'figure')],
    [Input('city-dropdown', 'value')]
)
def update_overview(city):
    filtered_data = data[data['city'] == city]
    avg_rate_fig = px.histogram(filtered_data, x='average_rate_per_night_dollar', title='Average Rate per Night Distribution')
    bedrooms_count_fig = px.bar(filtered_data, x='bedrooms_count', title='Bedrooms Count Distribution')
    return avg_rate_fig, bedrooms_count_fig


@callback(
    [Output('map-plot', 'figure'),
     Output('selected-property', 'children')],
    [Input('city-dropdown', 'value')]
)
def update_map(city):
    filtered_data = data[data['city'] == city]
    map_fig = px.scatter_mapbox(filtered_data, lat='latitude', lon='longitude', hover_name='title', zoom=10)
    map_fig.update_layout(mapbox_style="open-street-map")

    selected_property_info = filtered_data.iloc[0] 
    selected_property_html = html.Div([
        html.H3("Selected Property Information"),
        html.P(f"Title: {selected_property_info['title']}"),
        html.P(f"Description: {selected_property_info['description']}"),
        html.P(f"URL: {selected_property_info['url']}")
    ])

    return map_fig, selected_property_html