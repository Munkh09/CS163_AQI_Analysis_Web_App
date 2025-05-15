import dash
from dash import Dash, html, dash_table
from dash import dcc, callback
import pandas as pd
from google.cloud import storage
from io import StringIO
from tensorflow.keras.models import load_model
import numpy as np
import plotly.graph_objs as go
from datetime import datetime, timedelta
from dash.dependencies import Input, Output
import joblib
import os
import tempfile
import io

# Set up page route
dash.register_page(__name__, path="/predict-future-aqi")

def get_h5_model_from_gcs(bucket_name, file_name):
    """Download a .h5 Keras model file from GCS and load it."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(file_name)

    if not blob.exists():
        raise FileNotFoundError(f"The file {file_name} does not exist in bucket {bucket_name}")

    # Save to a temporary .h5 file
    with tempfile.NamedTemporaryFile(suffix=".h5", delete=False) as tmp_file:
        blob.download_to_filename(tmp_file.name)
        model_path = tmp_file.name

    # Load the model
    model = load_model(model_path, compile=False)

    # Optionally delete the temp file
    os.remove(model_path)

    return model

fresno_pm25_lstm_model = get_h5_model_from_gcs("munkh_models_lstm", "rigorous_fresno_pm25_lstm_model.h5")

def get_numpy_from_gcs(bucket_name, file_name):
    """Downloads a specific .npy file from the bucket and loads it."""
    
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(file_name)

    if not blob.exists():
        print("File does not exist")

    data = blob.download_as_string()
    np_data = np.load(io.BytesIO(data), allow_pickle=True)  # Load numpy array from byte stream
    
    return np_data

fresno_pm25_lstm_last_60_days = get_numpy_from_gcs("munkh_models_lstm", "rigorous_fresno_pm25_last_60_scaled.npy")
three_year_predictions = get_numpy_from_gcs("munkh_models_lstm", "three_year_predictions.npy")


def get_joblib_from_gcs(bucket_name, file_name):
    """Downloads a specific .pkl file from the bucket and loads it using joblib."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(file_name)

    if not blob.exists():
        raise FileNotFoundError(f"{file_name} not found in bucket {bucket_name}")

    data = blob.download_as_bytes()  # use .download_as_bytes() instead of .download_as_string()
    scaler = joblib.load(io.BytesIO(data))  # load with joblib
    return scaler

fresno_pm25_lstm_scaler = get_joblib_from_gcs("munkh_models_lstm", "rigorous_fresno_pm25_scaler.pkl")

# Last training date for the fresno pm 2.5 model
last_train_date = datetime(2025, 3, 31)



# Define AQI breakpoints and colors
bounds = [0, 50, 100, 150, 200, 300, 500]
aqi_colors = ['#00E400', '#FFFF00', '#FF7E00', '#FF0000', '#8F3F97', '#7E0023']

# Helper function to map AQI value to a color
def get_aqi_color(value):
    for i in range(len(bounds) - 1):
        if bounds[i] <= value < bounds[i + 1]:
            return aqi_colors[i]
    return aqi_colors[-1]  # fallback for AQI >= 500


def create_figure(predictions, prediction_dates, title):
    fig = go.Figure()

    for i in range(len(predictions) - 1):
        x0, x1 = prediction_dates[i], prediction_dates[i + 1]
        y0, y1 = predictions[i], predictions[i + 1]
        avg_y = (y0 + y1) / 2

        # Customize the color based on AQI
        color = get_aqi_color(avg_y)

        fig.add_trace(go.Scatter(
            x=[x0, x1],
            y=[y0, y1],
            mode='lines',
            line=dict(color=color, width=3),
            showlegend=False
        ))

    fig.update_layout(
        title=f"Predicted Daily PM 2.5 AQI for the Next {title}",
        xaxis=dict(title="Date"),
        yaxis=dict(title="Predicted Daily PM 2.5 AQI"),
        showlegend=False
    )

    return fig

three_year_dates = [pd.to_datetime('2025-04-01') + timedelta(days=i) for i in range(1, 1096)]

three_year_figure = create_figure(three_year_predictions, three_year_dates, '3 Years Forward')


layout = html.Div([
    html.H2("Predict the Future Average Daily PM 2.5 AQI for Fresno County Using an LSTM Model", style={
        "textAlign": "center",
        "marginTop": "30px",
        "color": "#2c3e50",
        "fontSize": "32px"
    }),

    html.Div([
        html.H3("Model Overview", style={"color": "#34495e"}),
        html.P(
            "The model was trained on daily PM 2.5 data from January 1st, 1999 to March 31st, 2025. "
            "To learn more about how this model was developed, please visit the Methodology section below.",
            style={'fontSize': '17px', 'lineHeight': '1.6'}
        ),
    ], style={"marginBottom": "40px"}),

    html.Div([
        html.H3("Real-Time Prediction (Until 08/01/2025)", style={"color": "#34495e"}),
        html.P(
            "To predict PM 2.5 AQI in real time up until August 1, 2025, please select a date below:",
            style={'fontSize': '17px', 'lineHeight': '1.6'}
        ),

        dcc.DatePickerSingle(
            id='date-picker',
            min_date_allowed=last_train_date.date(),
            max_date_allowed=datetime(2025, 8, 1).date(),
            initial_visible_month=last_train_date.date(),
            date=last_train_date.date(),
            display_format='YYYY-MM-DD',
            style={"marginBottom": "20px"}
        ),

        html.H4("AQI Color Legend", style={'color': '#2c3e50', "marginTop": "20px"}),
        html.Ul([
            html.Li("0 - 50: Good", style={'color': '#00E400'}),
            html.Li("51 - 100: Moderate", style={'color': '#FFFF00'}),
            html.Li("101 - 150: Unhealthy for Sensitive Groups", style={'color': '#FF7E00'}),
            html.Li("151 - 200: Unhealthy", style={'color': '#FF0000'}),
            html.Li("201 - 300: Very Unhealthy", style={'color': '#8F3F97'}),
            html.Li("301 - 500: Hazardous", style={'color': '#7E0023'}),
        ], style={"marginBottom": "30px", 'fontSize': '17px', 'lineHeight': '1.6'}),
    ], style={"marginBottom": "40px"}),

    html.Div([
        dcc.Graph(id='aqi-plot'),
    ], style={"marginBottom": "40px"}),

    html.Div([
        html.H4("3-Year Forward Forecast (Precomputed for Speed)", style={'color': '#2c3e50'}),
        dcc.Graph(id='aqi-3-year-plot', figure=three_year_figure),
    ], style={"marginBottom": "40px"}),

    html.Div([
        html.H3("Model Interpretation", style={"color": "#34495e"}),
        html.P(
            "The LSTM model effectively captured multiple seasonal patterns (weekly, monthly, yearly) "
            "and a long-term downward trend in PM 2.5 levels in Fresno County through the use of engineered temporal features.",
            style={'fontSize': '17px', 'lineHeight': '1.6'}
        ),

        html.P(
            "It recognized lower AQI values in recent years and consistently predicted seasonal wintertime spikes.",
            style={'fontSize': '17px', 'lineHeight': '1.6'}
        ),

        html.P(
            "These results suggest the model was well-trained and is reasonably suitable for practical use.",
            style={'fontSize': '17px', 'lineHeight': '1.6'}
        ),

        html.Div([
            html.A(
                html.Button("View Methodology", style={
                    "padding": "10px 20px",
                    "fontSize": "16px",
                    "backgroundColor": "#4CAF50",
                    "color": "white",
                    "border": "none",
                    "borderRadius": "5px",
                    "cursor": "pointer"
                }),
                href="/analytical-methods"
            )
        ], style={"marginTop": "30px", "textAlign": "center"})
    ], style={"marginBottom": "40px"}),
],
    style={
        "width": "90%",
        "margin": "0 auto",
        "paddingBottom": "50px",
        "fontFamily": "Arial, sans-serif",
        "backgroundColor": "#f9f9f9",
        "padding": "40px"
    }
)


def predict_future(model, last_60_scaled, days_to_predict, scaler):
    # Start from the last known date
    last_date = pd.to_datetime('2025-03-31')
    last_time_index = 9586

    # Initialize
    predictions = []
    prediction_dates = []

    current_input = last_60_scaled.copy()

    current_time_index = last_time_index

    for i in range(days_to_predict):  # Predict 2 years ahead
        # Predict next AQI
        pred = model.predict(current_input.reshape(1, 60, -1), verbose=0)
  
        predicted_aqi_scaled = pred[0, 0]
        predictions.append(predicted_aqi_scaled)

        # Update date and time index
        current_time_index += 1
        current_date = last_date + timedelta(days=i + 1)
        prediction_dates.append(current_date)

        # Compute new temporal features
        day_of_year = current_date.timetuple().tm_yday
        day_of_year_sin = np.sin(2 * np.pi * day_of_year / 365)
        day_of_year_cos = np.cos(2 * np.pi * day_of_year / 365)

        month = current_date.month
        month_sin = np.sin(2 * np.pi * month / 12)
        month_cos = np.cos(2 * np.pi * month / 12)

        day_of_week = current_date.weekday()
        day_of_week_sin = np.sin(2 * np.pi * day_of_week / 7)
        day_of_week_cos = np.cos(2 * np.pi * day_of_week / 7)

        # Normalize time_index using the same scaler as during training
        time_features = np.array([[0, current_time_index, day_of_year_sin, day_of_year_cos,
                               month_sin, month_cos, day_of_week_sin, day_of_week_cos]])
        time_features_scaled = scaler.transform(time_features)
        time_features_scaled[0, 0] = predicted_aqi_scaled  # replace dummy AQI with predicted one

        # Add to the sequence
        current_input = np.append(current_input[1:], [time_features_scaled[0]], axis=0)

        # Inverse transform only AQI predictions
        aqi_predictions_scaled = np.array(predictions).reshape(-1, 1)
        aqi_predictions = scaler.inverse_transform(
            np.hstack([aqi_predictions_scaled, np.zeros((len(aqi_predictions_scaled), scaler.n_features_in_ - 1))])
        )[:, 0]

    return aqi_predictions


@callback(
    Output('aqi-plot', 'figure'),
    Input('date-picker', 'date')
)
def update_prediction(selected_date):
    try: 
        if selected_date is None:
            return go.Figure()
    
        selected_date = datetime.strptime(selected_date, '%Y-%m-%d')
        num_days = (selected_date - last_train_date).days

        if num_days <= 0:
            return go.Figure()
    
        predictions = predict_future(
            fresno_pm25_lstm_model,
            fresno_pm25_lstm_last_60_days,
            num_days,
            fresno_pm25_lstm_scaler
        )

        predicted_dates = [last_train_date + timedelta(days=i) for i in range(1, num_days + 1)]

        fig = go.Figure()

        for i in range(len(predictions) - 1):
            x0, x1 = predicted_dates[i], predicted_dates[i + 1]
            y0, y1 = predictions[i], predictions[i + 1]
            avg_y = (y0 + y1) / 2
            color = get_aqi_color(avg_y)

            fig.add_trace(go.Scatter(
                x=[x0, x1],
                y=[y0, y1],
                mode='lines',
                line=dict(color=color, width=3),
                showlegend=False
            ))

        fig.update_layout(
            title=f"Predicted Daily PM 2.5 AQI in Fresno County from {last_train_date.date()} to {selected_date.date()}",
            xaxis=dict(title="Date"),
            yaxis=dict(title="Predicted Daily PM 2.5 AQI"),
            showlegend=False
        )
        return fig
    except Exception as e:
        print("Error in update_prediction:", str(e))
        return go.Figure()








