import dash
from dash import Dash, html, dash_table, dcc, callback, Output, Input
import pandas as pd
import plotly.express as px
from google.cloud import storage
import os
from io import StringIO
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import numpy as np
from statsmodels.tsa.stattools import ccf


dash.register_page(__name__, path="/major-findings")


# Return a Pandas Dataframe from a CGS Bucket
def get_all_csvs_from_gcs(bucket_name):
    """Downloads all blobs from the bucket."""
    
    storage_client = storage.Client()

    # List all blobs in the bucket 
    blobs = storage_client.list_blobs(bucket_name)
    
    dataframes = {}

    for blob in blobs:
        if blob.name.endswith('.csv'): 
            data = blob.download_as_text()
            df = pd.read_csv(StringIO(data))
            dataframes[blob.name] = df  # Save with filename as key

    return dataframes

# Load all data from pm25_correlation_data Bucket
pm25_correlation_dfs = get_all_csvs_from_gcs("pm25_correlation_data")

def improve_pol_label(label_name):
    """Properly Names Pollutant Labels"""
    name_splitted = ' '.join(label_name.split("_"))
    return ''.join([char.upper() if char.isalpha() else char for char in name_splitted])

# Scatter Plot
# Callback
@callback(
    Output('scatter-plot', 'figure'),
    Input('scatter-plot-dropdown', 'value')
)
def update_scatter(selected_dataset):
    """Returns a Scatter Plot of 2 Pollutants"""

    df = pm25_correlation_dfs[selected_dataset]
    x_axis = df.columns[2] # pm 25
    y_axis = df.columns[3] # the other pollutant based on the selected dataset 

    fig = px.scatter(
        df,
        x=x_axis,
        y=y_axis,
        trendline="ols",
        trendline_color_override="red", 
        labels={x_axis: improve_pol_label(x_axis), y_axis: improve_pol_label(y_axis)},
        title=f"Scatter Plot with Regression Line: {improve_pol_label(x_axis)} vs {improve_pol_label(y_axis)}"
    )
    return fig


# CCF Plot
# Callback to update the CCF plot dynamically
@callback(
    Output("ccf-plot", "figure"),
    [Input("ccf-plot-dropdown", "value")]
)
def update_ccf_plot(selected_dataset):
    df = pm25_correlation_dfs[selected_dataset]

    pollutant1_series = df.iloc[:, 2]
    pollutant2_series = df.iloc[:, 3]

    # Calculate CCF values
    ccf_values = ccf(pollutant1_series, pollutant2_series)

    # Number of observations
    N = len(pollutant1_series)
    conf_bound = 1.96 / np.sqrt(N)

    # Lags for plotting
    lags = np.arange(30)
    
    # Create the stem plot
    fig = make_subplots(rows=1, cols=1)

    # Stem trace for CCF values
    fig.add_trace(go.Scatter(
        x=lags,
        y=ccf_values[:30],
        mode='markers+lines',
        line=dict(shape='vh', width=2),
        marker=dict(symbol='line-ns-open', size=8),
        name='CCF'
    ))

    # Add horizontal lines for confidence bounds
    fig.add_trace(go.Scatter(
        x=[0, max(lags)],
        y=[conf_bound, conf_bound],
        mode='lines',
        line=dict(dash='dash', color='red'),
        name='Upper Bound'
    ))

    fig.add_trace(go.Scatter(
        x=[0, max(lags)],
        y=[-conf_bound, -conf_bound],
        mode='lines',
        line=dict(dash='dash', color='red'),
        name='Lower Bound'
    ))

    # Update layout for title, axis labels, and size
    fig.update_layout(
        title=f'Cross-Correlation Function (CCF) of {improve_pol_label(df.columns[2])} and {improve_pol_label(df.columns[3])}',
        xaxis_title='Lag (Day)',
        yaxis_title='Cross-correlation',
        height=500,
        width=800
    )
    
    return fig


# Dual Axes Plot
@callback(
    Output('dual-axes-plot', 'figure'),
    Input('dual-axes-plot-dropdown', 'value') 
)
def update_dual_axes_plot(selected_dataset):    
    df = pm25_correlation_dfs[selected_dataset]
    
    # Convert the date_local to Timestamp type for visualization
    df["date_local"] = pd.to_datetime(df["date_local"])
    
    pollutant1_series = df.iloc[:, 2]
    pollutant2_series = df.iloc[:, 3]

    # Create figure with two y-axes
    fig = go.Figure()

    # Plot Pollutant 1 on the first y-axis
    fig.add_trace(go.Scatter(
        x=df["date_local"], # Time for the x axis
        y=df.iloc[:, 2], # PM 25 for the left y axis
        mode='lines',
        name=f'{df.columns[2]}',
        line=dict(color='blue')
    ))

    # Plot Pollutant 2 on the second y-axis (secondary y-axis)
    fig.add_trace(go.Scatter(
        x=df["date_local"],
        y=df.iloc[:, 3], # other pollutant on the right axis
        mode='lines',
        name=f'{df.columns[3]}',
        line=dict(color='red'),
        yaxis='y2'  # This places the Pollutant 2 data on the second y-axis
    ))

    # Update layout for dual y-axes
    fig.update_layout(
        title=f'Dual-Axes Plot of {improve_pol_label(df.columns[2])} and {improve_pol_label(df.columns[3])} Over Time',
        xaxis=dict(
            title='Time',
            tickformat='%Y-%m-%d %H:%M',  # Date format for x-axis ticks
            rangeslider=dict(visible=False)  # Optional: adds a range slider to x-axis
        ),
        yaxis=dict(
            title=f'{improve_pol_label(df.columns[2])}',
            tickfont=dict(color='blue')
        ),
        yaxis2=dict(
            title=f'{improve_pol_label(df.columns[3])}',
            tickfont=dict(color='red'),
            overlaying='y',  # Overlay this axis on the primary y-axis
            side='right'  # Position this axis on the right side
        ),
        height=500,
        width=800
    )

    return fig


# Page layout
layout = html.Div([
    html.H2("Major Findings"),
    html.H3("1. AQI of PM 2.5 in Fresno Has Reduced Over the Last 20 Years; in terms of historical trend, it was High During Winter but Low During the Other Seasons"),
    html.Img(src="/assets/Fresno_PM25.png", style={"width": "50%"}),
    html.P("Based on this visualization, we can clearly see that AQI of PM 2.5 has significantly reduced in recent years, especially in 2023 and 2024."),
    html.P("Thus, we can deduce that the ISR Rules and other anti air pollution policies in Fresno County are effectively reducing the AQI of PM 2.5."),
    html.H3("2. The ISR Rule 9510 Was Effective in Reducing AQI of PM 2.5 and PM 10"),
    html.Img(src="/assets/ISR_9510_Effectiveness_Plot.png", style={"width": "50%"}),
    html.Br(),
    html.Img(src="/assets/T_test.png", style={"width": "50%"}),
    html.P("Based on T-Test results, we determined that the ISR Rule 9510 was effective, and we also quantified the percentage of decrease in AQI of PM 2.5 and PM 10 after the rule's adoption."),
    html.H3("3. PM 2.5 Has High Correlation with PM 10 and Carbon Monoxide (CO)"),
    html.H4("Scatter Plots with Regression Line: "),
    dcc.Dropdown(
        id="scatter-plot-dropdown",
        options=[{
        'label': ' and '.join([word for word in key.split("_")[:-1]]).replace(".csv", ""), 
        'value': key
        } for key in pm25_correlation_dfs.keys()],
        value=list(pm25_correlation_dfs.keys())[3],  # Default to the first file
    ),
    dcc.Graph(id='scatter-plot'),
    html.H4("Cross Correlation Function (CCF) Plots: "),
    dcc.Dropdown(
        id="ccf-plot-dropdown",
        options=[{
        'label': ' and '.join([word for word in key.split("_")[:-1]]).replace(".csv", ""), 
        'value': key
        } for key in pm25_correlation_dfs.keys()],
        value=list(pm25_correlation_dfs.keys())[3],
    ),
    dcc.Graph(id="ccf-plot"),
    html.H4("Dual Y-Axes Time Series Plots: "),
    dcc.Dropdown(
        id="dual-axes-plot-dropdown",
        options=[{
        'label': ' and '.join([word for word in key.split("_")[:-1]]).replace(".csv", ""), 
        'value': key
        } for key in pm25_correlation_dfs.keys()],
        value=list(pm25_correlation_dfs.keys())[3],
    ),
    dcc.Graph(id="dual-axes-plot"),
    html.H3("4. Although not directly a finding, we developed a high-performing LSTM model supported by robust preprocessing techniques"),
    html.Img(src="/assets/LSTM_Model_Visual.png", style={"width": "80%"})
])

