import dash
from dash import html, dcc

dash.register_page(__name__, path="/analytical-methods")

layout = html.Div([
    html.H2("Analytical Methods", style={
        'textAlign': 'center',
        'fontFamily': 'Arial',
        'marginBottom': '25px'
    }),

    html.H3("Preprocessing", style={
        'fontFamily': 'Arial',
        'marginBottom': '15px'
    }),

    html.H4("1. Grouping Monitor Data", style={
        'fontFamily': 'Arial',
        'marginTop': '20px',
        'marginBottom': '10px'
    }),
    html.P(
        "Because of several monitors in a county, we took the mean AQI of the monitors for each unique date.",
        style={'fontFamily': 'Arial', 'maxWidth': '800px', 'margin': 'auto', 'marginBottom': '10px'}
    ),
    html.P(
        "For instance, the PM 2.5 data for Fresno County before grouping by date is shown below: ",
        style={'fontFamily': 'Arial', 'maxWidth': '800px', 'margin': 'auto', 'marginBottom': '15px'}
    ),
    html.Img(src="/assets/PM25_Fresno_Ungrouped.png", style={"width": "30%", "display": "block", "margin": "auto", "marginBottom": "25px"}),

    html.P(
        "After applying the mean, we get the mean daily AQI for the entire Fresno County for each day: ",
        style={'fontFamily': 'Arial', 'maxWidth': '800px', 'margin': 'auto', 'marginBottom': '15px'}
    ),
    html.Img(src="/assets/PM25_Fresno_Grouped.png", style={"width": "30%", "display": "block", "margin": "auto", "marginBottom": "25px"}),

    html.H4("2. Handling Missing Values", style={
        'fontFamily': 'Arial',
        'marginTop': '20px',
        'marginBottom': '10px'
    }),
    html.P(
        "After taking grouping, the data missed some daily data for years in 1999 to 2007: ",
        style={'fontFamily': 'Arial', 'maxWidth': '800px', 'margin': 'auto', 'marginBottom': '15px'}
    ),
    html.Img(src="/assets/Missing_Values.png", style={"width": "80%", "display": "block", "margin": "auto", "marginBottom": "25px"}),

    html.P(
        ("Therefore, we interpolated the missing values based on the mean of neighboring data points. "
         "For instance, if 01/01 was 100, 01/02 was NaN, and 01/03 was 110, then we fill 01/02 with (100 "
         "+ 110) / 2 = 105. The function dynamically adjusts if the number of consecutive NaN’s is large. "
         "If the consecutive gap is large, then this model has limitations as it will fill with high uncertainty. "
         "However, because our dataset has small isolated gaps, this method works well. Furthermore, as "
         "AQI is a temporal and continuous data, this method suits well."),
        style={'fontFamily': 'Arial', 'maxWidth': '800px', 'margin': 'auto', 'marginBottom': '15px'}
    ),
    html.P(
        "The data after this step:",
        style={'fontFamily': 'Arial', 'maxWidth': '800px', 'margin': 'auto', 'marginBottom': '15px'}
    ),
    html.Img(src="/assets/Missing_Values_Handled.png", style={"width": "20%", "display": "block", "margin": "auto", "marginBottom": "25px"}),

    html.H3("3. Outlier Detection and Smoothing", style={
        'fontFamily': 'Arial',
        'marginTop': '30px',
        'marginBottom': '15px'
    }),
    html.P(
        "After the data is ready, we detected some outliers with the help of visualization: ",
        style={'fontFamily': 'Arial', 'maxWidth': '800px', 'margin': 'auto', 'marginBottom': '15px'}
    ),
    html.Img(src="/assets/Outliers.png", style={"width":"50%", "display": "block", "margin": "auto", "marginBottom": "25px"}),
    html.P(
        "Therefore, we trained an Isolation Forest to detect the outliers and the previous year AQI at the same day to smooth them.",
        style={'fontFamily': 'Arial', 'maxWidth': '800px', 'margin': 'auto', 'marginBottom': '15px'}
    ),
    html.P(
        "The data after outlier smoothing: ",
        style={'fontFamily': 'Arial', 'maxWidth': '800px', 'margin': 'auto', 'marginBottom': '15px'}
    ),
    html.Img(src="/assets/Outliers_After_Smoothing.png", style={"width": "50%", "display": "block", "margin": "auto", "marginBottom": "25px"}),

    html.H3("Assessing Model Assumptions", style={
        'fontFamily': 'Arial',
        'marginTop': '30px',
        'marginBottom': '15px'
    }),
    html.P(
        "Because LSTM assumes seasonality, we checked whether daily PM 2.5 in Fresno County was seasonal or not: ",
        style={'fontFamily': 'Arial', 'maxWidth': '800px', 'margin': 'auto', 'marginBottom': '15px'}
    ),
    html.Img(src="/assets/PM25_Fresno_Seasonality.png", style={"width": "50%", "display": "block", "margin": "auto", "marginBottom": "25px"}),
    html.P(
        "As daily PM 2.5 is clearly seasonal, we could and did train an LSTM model on it, which is shown in the Major Findings page.",
        style={'fontFamily': 'Arial', 'maxWidth': '800px', 'margin': 'auto', 'marginBottom': '15px'}
    ),
    html.P(
        "In terms of the SARIMA model, it assumes stationarity, and thus, we checked it by using the rolling mean and standard deviation:",
        style={'fontFamily': 'Arial', 'maxWidth': '800px', 'margin': 'auto', 'marginBottom': '15px'}
    ),
    html.Img(src="/assets/Stationarity_Check.png", style={"width": "50%", "display": "block", "margin": "auto", "marginBottom": "25px"}),
    html.P(
        "Because PM 2.5 is not stationary, the SARIMA could not and did not perform well.",
        style={'fontFamily': 'Arial', 'maxWidth': '800px', 'margin': 'auto', 'marginBottom': '30px'}
    ),

    html.H3("Feature Engineering with Other Pollutants such as CO and PM 10", style={
        'fontFamily': 'Arial',
        'marginBottom': '15px'
    }),
    html.P(
        "As shown in the Major Findings page, PM 2.5 had a high Correlation with PM 10 and CO.",
        style={'fontFamily': 'Arial', 'maxWidth': '800px', 'margin': 'auto', 'marginBottom': '10px'}
    ),
    html.P(
        "For this reason, we trained LSTM models to predict PM 2.5 with and without PM 10 and CO.",
        style={'fontFamily': 'Arial', 'maxWidth': '800px', 'margin': 'auto', 'marginBottom': '20px'}
    ),

    html.P(
        "LSTM with only PM 2.5 and with both PM 2.5 and PM 10 Performance: ",
        style={'fontFamily': 'Arial', 'maxWidth': '800px', 'margin': 'auto', 'marginBottom': '10px'}
    ),
    html.Img(src="/assets/LSTM_PM25_PM10_MAE.png", style={"width": "50%", "display": "block", "margin": "auto", "marginBottom": "15px"}),
    html.Br(),
    html.Img(src="/assets/LSTM_PM25_PM10_Visual.png", style={"width": "50%", "display": "block", "margin": "auto", "marginBottom": "20px"}),
    html.P(
        "Unfortunately, including PM 10 did not improve the LSTM for PM 2.5 prediction.",
        style={'fontFamily': 'Arial', 'maxWidth': '800px', 'margin': 'auto', 'marginBottom': '30px'}
    ),

    html.P(
        "Then, we tested the model performance after including CO.",
        style={'fontFamily': 'Arial', 'maxWidth': '800px', 'margin': 'auto', 'marginBottom': '10px'}
    ),
    html.P(
        "LSTM with only PM 2.5 and with both PM 2.5 and CO Performance: ",
        style={'fontFamily': 'Arial', 'maxWidth': '800px', 'margin': 'auto', 'marginBottom': '10px'}
    ),
    html.Img(src="/assets/LSTM_PM25_CO_MAE.png", style={"width": "50%", "display": "block", "margin": "auto", "marginBottom": "15px"}),
    html.Br(),
    html.Img(src="/assets/LSTM_PM25_CO_Visual.png", style={"width": "50%", "display": "block", "margin": "auto", "marginBottom": "20px"}),
    html.P(
        "Similar to PM 10, including the AQI of CO did not improve the LSTM model for PM 2.5 prediction.",
        style={'fontFamily': 'Arial', 'maxWidth': '800px', 'margin': 'auto', 'marginBottom': '30px'}
    ),

    html.H3("Feature Engineering with Meteorological Features", style={
        'fontFamily': 'Arial',
        'marginBottom': '15px'
    }),
    html.P(
        "We trained LSTM models for PM 2.5 AQI prediction with and without some of the most relevant meteorological features: wind speed, solar radiation, humidity, and temperature.",
        style={'fontFamily': 'Arial', 'maxWidth': '800px', 'margin': 'auto', 'marginBottom': '15px'}
    ),
    
    html.Img(src="/assets/lstm_pm25_only_results.png", style={"width": "50%", "display": "block", "margin": "auto", "marginBottom": "15px"}),
    html.Br(),
    html.Img(src="/assets/lstm_pm25_wind_speed_results.png", style={"width": "50%", "display": "block", "margin": "auto", "marginBottom": "15px"}),
    html.Br(),
    html.Img(src="/assets/lstm_pm25_temperature_results.png", style={"width": "50%", "display": "block", "margin": "auto", "marginBottom": "15px"}),
    html.Br(),
    html.Img(src="/assets/lstm_pm25_solar_radiation_results.png", style={"width": "50%", "display": "block", "margin": "auto", "marginBottom": "15px"}),
    html.Br(),
    html.Img(src="/assets/lstm_pm25_humidity_results.png", style={"width": "50%", "display": "block", "margin": "auto", "marginBottom": "15px"}),
    html.Br(),
    html.P(
        "Unfortunately, including these features did not improve the models significantly. Only wind speed and solar radiation improved the model performances, but at a very small scale.",
        style={'fontFamily': 'Arial', 'maxWidth': '800px', 'margin': 'auto', 'marginBottom': '25px'}
    ),
])
