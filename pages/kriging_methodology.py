import dash
from dash import Dash, html, dash_table
from dash import html
import pandas as pd
from google.cloud import storage
from io import StringIO

dash.register_page(__name__, path="/kriging-methodology")

layout = html.Div([
    html.H2("Methodology for the Kriging Model", style={'marginTop': '30px', 'color': '#2c3e50'}),

    html.H3("What is Kriging Model?", style={'marginTop': '25px', 'color': '#2c3e50'}),

    html.P("It is a popular geospatial model that predicts a statistic at an unsampled location using close sampled locations' statistics.",
           style={'fontSize': '17px', 'lineHeight': '1.6'}),

    html.P("Kriging Model is similar to the concept of KNN, but it assumes spatial autocorrelation, and instead of merely taking the mean or aggregate of the neighboring locations, Kriging applies more weight to locations nearby the query point.",
           style={'fontSize': '17px', 'lineHeight': '1.6'}),

    html.H3("Does PM 2.5 AQI in San Joaquin Valley pass the Spatial Autocorrelation assumption?", 
            style={'marginTop': '25px', 'color': '#2c3e50'}),

    html.P("We found out that PM 2.5 AQI in SJV does have a strong spatial autocorrelation by applying the Global Moran's I Test for several years.",
           style={'fontSize': '17px', 'lineHeight': '1.6'}),

    html.P("The challenge with applying Moran's I is that it works on a specific time or day. For this reason, we computed the Moran's I for every day of the year and plotted the distributions.",
           style={'fontSize': '17px', 'lineHeight': '1.6'}),

    html.P("We plotted the distributions for 2022 and 2024 at the moment.",
           style={'fontSize': '17px', 'lineHeight': '1.6'}),

    html.Img(src="/assets/moran_i_sjv_2022.png", style={"width": "50%", "display": "block", "margin": "30px auto 15px auto"}),

    html.Br(),

    html.Img(src="/assets/moran_i_sjv_2024.png", style={"width":"50%", "display": "block", "margin": "15px auto 30px auto"}),

    html.P("Based on these distributions, we can see that the majority of daily Moran's I values lie above 0, and the mean is about 0.4. This means that the PM 2.5 AQI in San Joaquin Valley does have spatial autocorrelation.",
           style={'fontSize': '17px', 'lineHeight': '1.6'}),

    html.P("The p-values were always lower than 0.05, meaning that these statistics are significant (did not occur by chance).",
           style={'fontSize': '17px', 'lineHeight': '1.6'}),

    html.P("This means that the Kriging model is suitable for the PM 2.5 AQI in San Joaquin Valley data, but at the same time, given low number of the monitors (sampled locations), the model can work well only when not too far away from sampled locations.",
           style={'fontSize': '17px', 'lineHeight': '1.6'}),
],
style={
    'padding': '40px',
    'maxWidth': '1000px',
    'margin': '0 auto',
    'fontFamily': 'Arial, sans-serif',
    'backgroundColor': '#f9f9f9'
})
