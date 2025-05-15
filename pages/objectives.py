import dash
from dash import Dash, html, dash_table
from dash import html
import pandas as pd
from google.cloud import storage
from io import StringIO

dash.register_page(__name__, path="/objectives")

def get_csv_from_gcs(bucket_name, file_name):
    """Downloads a specific CSV file from the bucket."""
    
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(file_name)

    if not blob.exists():
        print("File does not exist")

    data = blob.download_as_text()
    df = pd.read_csv(StringIO(data))
    
    return df

fresno_sample_df = get_csv_from_gcs("fresno_daily_data", "sampled_fresno_df.csv")

layout = html.Div([
    html.H2("Objectives", style={'marginTop': '30px', 'color': '#2c3e50'}),
    
    html.P("For this project, the main goals were to:", style={'fontSize': '18px', 'lineHeight': '1.6'}),
    
    html.Ul([
        html.Li("Analyze trends in the AQI of major pollutants in the San Joaquin Valley (SJV) over the past 20 years"),
        html.Br(),
        html.Li("Design and implement robust data preprocessing and feature engineering pipelines for machine learning and statistical modeling"),
        html.Br(),
        html.Li("Assess model assumptions and train, test, and compare LSTM and SARIMA models"),
        html.Br(),
        html.Li("Determine the effectiveness of the ISR Rule 9510 in San Joaquin Valley"),
        html.Br(),
        html.Li("Research and train a Kriging Model")
    ], style={'fontSize': '16px', 'marginLeft': '20px', 'lineHeight': '1.8'}),
    
    html.H2("Data Sources", style={'marginTop': '30px', 'color': '#2c3e50'}),
    
    html.P("For data, we used daily summary data from the U.S. Environmental Protection Agency (EPA) AQS API.",
           style={'fontSize': '17px', 'lineHeight': '1.6'}),
    
    html.P("The DataFrame below is a sample daily summary data for Fresno County for PM2.5, PM10, CO, Ozone (Ground), NO2, and SO2:",
           style={'fontSize': '17px', 'lineHeight': '1.6'}),
    
    dash_table.DataTable(
        id='fresno_sample_df',
        columns=[{"name": i, "id": i} for i in fresno_sample_df.columns],
        data=fresno_sample_df.to_dict('records'),
        page_size=8,
        style_table={'overflowX': 'auto', 'marginBottom': '40px', 'border': '1px solid #ccc', 'borderRadius': '8px'},
        style_cell={
            'textAlign': 'left',
            'padding': '10px',
            'fontFamily': 'Arial, sans-serif',
            'fontSize': '14px',
        },
        style_header={
            'backgroundColor': '#f2f2f2',
            'fontWeight': 'bold'
        }
    )
],
style={'padding': '40px', 'maxWidth': '1000px', 'margin': '0 auto', 'fontFamily': 'Arial, sans-serif', 'backgroundColor': '#f9f9f9'})
