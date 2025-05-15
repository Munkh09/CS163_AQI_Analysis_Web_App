import dash
from dash import html, dcc, callback, Input, Output
import pandas as pd
from google.cloud import storage
from io import StringIO
from pykrige.ok import OrdinaryKriging
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import geopandas as gpd
from shapely.geometry import Point
from shapely.ops import unary_union
from geopy.distance import geodesic


dash.register_page(__name__, path="/predict-at-unsampled-locations")


# Helper function to get CSV from GCS
def get_csv_from_gcs(bucket_name, file_name):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(file_name)
    if not blob.exists():
        raise FileNotFoundError("File does not exist")
    data = blob.download_as_text()
    return pd.read_csv(StringIO(data))


# Load data
sjv_pm25 = get_csv_from_gcs("sjv_pm25", "sjv_pm25_daily_df.csv")


# Create individual buffer zones
def create_buffer_zone(df, radius_km=200):
    gdf = gpd.GeoDataFrame(df,
                           geometry=gpd.points_from_xy(df['longitude'], df['latitude']),
                           crs="EPSG:4326").to_crs(epsg=3395)
    gdf['geometry'] = gdf.geometry.buffer(radius_km * 1000)  # Convert km to meters
    return gdf.to_crs(epsg=4326)




# Check if clicked point is within allowable prediction distance
def is_within_distance(lon, lat, longitudes, latitudes, threshold_km=200):
    for lon0, lat0 in zip(longitudes, latitudes):
        if geodesic((lat, lon), (lat0, lon0)).km <= threshold_km:
            return True
    return False


# Layout
# layout = html.Div([
#     html.Div([
#         html.H2("Predict PM 2.5 AQI at Unsampled Locations", style={
#             'textAlign': 'center',
#             'fontFamily': 'Arial',
#             'marginBottom': '10px'
#         }),
#         html.P("Our team implemented a Kriging Model to predict at unsampled locations on different days. The model uses all monitor values within 200 km or 125 mi. Click the methodology button below to learn more.", style={
#             'textAlign': 'center',
#             'fontFamily': 'Arial',
#             'maxWidth': '800px',
#             'margin': 'auto'
#         }),
#     ], style={'marginBottom': '30px'}),

#     html.Div([
#         html.Label("Select a Date:", style={
#             'fontWeight': 'bold',
#             'fontSize': '16px',
#             'marginRight': '10px'
#         }),
#         dcc.DatePickerSingle(
#             id='date-picker',
#             min_date_allowed=pd.to_datetime(sjv_pm25["date_local"]).min(),
#             max_date_allowed=pd.to_datetime(sjv_pm25["date_local"]).max(),
#             initial_visible_month=pd.to_datetime("2024-01-01"),
#             date="2024-01-01",
#             style={'display': 'inline-block'}
#         ),
#     ], style={'textAlign': 'center', 'marginBottom': '30px'}),

#     dcc.Loading(  # Added Loading component to wrap the map and prediction output
#         id="loading-spinner",
#         type="circle",  # You can also try "dot" or "default" depending on your preference
#         fullscreen=False,
#         children=html.Div([
#             dcc.Graph(id='map', config={'displayModeBar': False}),
#             html.Div(id='prediction-output', style={
#                 'textAlign': 'center',
#                 'marginTop': '15px',
#                 'fontFamily': 'Arial',
#                 'fontSize': '16px'
#             })
#         ])
#     ),

#     html.Br(),

#     html.Div([
#         html.A(
#             html.Button("View Methodology", style={
#                 "padding": "10px 20px",
#                 "fontSize": "16px",
#                 "backgroundColor": "#4CAF50",
#                 "color": "white",
#                 "border": "none",
#                 "borderRadius": "5px",
#                 "cursor": "pointer",
#                 "marginTop": "10px"
#             }),
#             href="/kriging-methodology"
#         )
#     ], style={'textAlign': 'center', 'marginTop': '20px'})
# ], style={
#     'maxWidth': '1000px',
#     'margin': '0 auto',
#     'padding': '20px',
#     'fontFamily': 'Arial, sans-serif'
# })
layout = html.Div([
    html.Div([
        html.H2("Predict PM 2.5 AQI at Unsampled Locations", style={
            'textAlign': 'center',
            'fontFamily': 'Arial',
            'marginBottom': '10px'
        }),
        html.P(
            "Our team implemented a Kriging Model to predict at unsampled locations on different days. "
            "The model uses all monitor values within 200 km or 125 mi. Click the methodology button below to learn more.",
            style={
                'textAlign': 'center',
                'fontFamily': 'Arial',
                'maxWidth': '800px',
                'margin': 'auto'
            }
        ),
    ], style={'marginBottom': '30px'}),

    html.Div([
        html.Label("Select a Date:", style={
            'fontWeight': 'bold',
            'fontSize': '16px',
            'marginRight': '10px'
        }),
        dcc.DatePickerSingle(
            id='date-picker',
            min_date_allowed=pd.to_datetime(sjv_pm25["date_local"]).min(),
            max_date_allowed=pd.to_datetime(sjv_pm25["date_local"]).max(),
            initial_visible_month=pd.to_datetime("2024-01-01"),
            date="2024-01-01",
            style={'display': 'inline-block'}
        ),
    ], style={'textAlign': 'center', 'marginBottom': '30px'}),

    dcc.Loading(
        id="loading-spinner",
        type="circle",
        fullscreen=False,
        children=html.Div([
            dcc.Graph(id='map', config={'displayModeBar': False}),
            html.Div(id='prediction-output', style={
                'textAlign': 'center',
                'marginTop': '15px',
                'fontFamily': 'Arial',
                'fontSize': '16px'
            })
        ])
    ),

    html.Br(),

    html.Div([
        html.A(
            html.Button("View Methodology", style={
                "padding": "10px 20px",
                "fontSize": "16px",
                "backgroundColor": "#4CAF50",
                "color": "white",
                "border": "none",
                "borderRadius": "5px",
                "cursor": "pointer",
                "marginTop": "10px"
            }),
            href="/kriging-methodology"
        )
    ], style={'textAlign': 'center', 'marginTop': '20px'})
], style={
    'maxWidth': '1000px',
    'margin': '0 auto',
    'padding': '20px',
    'fontFamily': 'Arial, sans-serif'
})


# Helper function to create a grid of points
def create_grid(min_lat, max_lat, min_lon, max_lon, resolution=0.05):
    latitudes = np.arange(min_lat, max_lat, resolution)
    longitudes = np.arange(min_lon, max_lon, resolution)
    grid = []
    for lat in latitudes:
        for lon in longitudes:
            grid.append((lat, lon))
    return grid


colorscale = "Viridis"


# Update map with prediction area, buffer zones, and AQI grid
@callback(
    Output('map', 'figure'),
    Input('date-picker', 'date')
)
def update_map(date):
    if date is None:
        return go.Figure()


    subset = sjv_pm25[sjv_pm25["date_local"] == date]
    if subset.empty:
        return go.Figure()


    # Create grid points for AQI prediction
    min_lat, max_lat = subset["latitude"].min(), subset["latitude"].max()
    min_lon, max_lon = subset["longitude"].min(), subset["longitude"].max()
    grid_points = create_grid(min_lat, max_lat, min_lon, max_lon, resolution=0.05)


    # Predict AQI for each grid point using Kriging
    aqi_predictions = []
    for lat, lon in grid_points:
        if is_within_distance(lon, lat, subset['longitude'].values, subset['latitude'].values):
            try:
                OK = OrdinaryKriging(
                    subset['longitude'].values,
                    subset['latitude'].values,
                    subset['aqi'].values,
                    variogram_model="spherical",
                    variogram_parameters={"sill": 60, "range": 3500.0, "nugget": 5}
                )
                pred, var = OK.execute("points", [lon], [lat])
                aqi_predictions.append((lat, lon, pred[0]))
            except Exception:
                continue


    # Convert grid predictions to DataFrame
    grid_df = pd.DataFrame(aqi_predictions, columns=["latitude", "longitude", "predicted_aqi"])


    # Plot the map
    fig = px.scatter_mapbox(
        sjv_pm25[sjv_pm25["date_local"] == "2024-01-01"],
        lat="latitude", lon="longitude",
        color="aqi", hover_name="site_number",
        zoom=6, height=600
    )


    # Increase the size of the monitoring station markers
    fig.update_traces(marker=dict(size=18))  # Set the size to 18 or any desired value


    # Update the layout to use OpenStreetMap
    fig.update_layout(mapbox_style="open-street-map")




    # Add grid cells with AQI predictions
    # Add grid cells with AQI predictions (hidden)
    fig.add_trace(go.Scattermapbox(
        lat=grid_df["latitude"].tolist(),
        lon=grid_df["longitude"].tolist(),
        mode="markers",
        marker=dict(
            size=6,  # Adjust the size if needed
            color=grid_df["predicted_aqi"],
            colorscale="Viridis",
            showscale=False,
            opacity=0.3  # Adjust the opacity for a lighter appearance
        ),
        name="Predicted AQI Grid"
    ))


    return fig
   
# Predict AQI when map is clicked
@callback(
    Output('prediction-output', 'children'),
    Input('map', 'clickData'),
    Input('date-picker', 'date')
)
def predict_aqi(clickData, date):
    if clickData is None or date is None:
        return "Click on the map to get AQI prediction."


    lat = clickData['points'][0]['lat']
    lon = clickData['points'][0]['lon']


    subset = sjv_pm25[sjv_pm25["date_local"] == date].dropna(subset=["latitude", "longitude", "aqi"])
    if subset.empty:
        return "No data available for this date."


    if not is_within_distance(lon, lat, subset['longitude'].values, subset['latitude'].values):
        return "Selected point is too far from available monitors (200 km limit)."


    try:
        # Updated range parameter to 3500.0
        OK = OrdinaryKriging(
            subset['longitude'].values,
            subset['latitude'].values,
            subset['aqi'].values,
            variogram_model="spherical",
            variogram_parameters={"sill": 60, "range": 3500.0, "nugget": 5}
        )
        pred, var = OK.execute("points", [lon], [lat])
        if np.isnan(var[0]) or var[0] < 0:
            uncertainty = "N/A"
            style = "gray"
        else:
            std_dev = np.sqrt(var[0])
            uncertainty = f"± {std_dev:.2f}"
            style = "red" if std_dev > 20 else "green"


        return html.Div([
            html.P(
                f" Location: ({lat:.4f}, {lon:.4f}) → Predicted AQI: {pred[0]:.2f} {uncertainty}",
                style={'fontSize': '18px', 'fontWeight': 'bold', 'color': style}
            )
        ])
    except Exception as e:
        return f"Prediction failed: {str(e)}"



