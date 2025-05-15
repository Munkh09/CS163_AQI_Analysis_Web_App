import dash
from dash import html, dcc, Output, Input, State, callback


# Initialize the app
app = dash.Dash(__name__, use_pages=True)
server = app.server

navbar = html.Nav([
    dcc.Store(id='menu-state', data=False),

    html.Div([
        html.P("AQI Analysis", className="brand"),
        html.Div("☰", id="menu-toggle", className="menu-icon", n_clicks=0),
    ], className="navbar-header"),

    html.Ul([
        html.Li(dcc.Link("Main", href="/")),
        html.Li(dcc.Link("Objectives", href="/objectives")),
        html.Li(dcc.Link("Major Findings", href="/major-findings")),
        html.Li(dcc.Link("Analytical Methods", href="/analytical-methods")),
        html.Li(dcc.Link("Predict Future PM 2.5 AQI", href="/predict-future-aqi")),
        html.Li(dcc.Link("Predict AQI at Unsampled Locations", href="/predict-at-unsampled-locations"))
    ], id="nav-links", className="navlinks")
], className="navbar")


app.layout = html.Div([
    navbar,
    dash.page_container
])


@callback(
    Output('menu-state', 'data'),
    Input('menu-toggle', 'n_clicks'),
    State('menu-state', 'data'),
    prevent_initial_call=True
)
def toggle_menu_state(n_clicks, current_state):
    return not current_state

@callback(
    Output('nav-links', 'className'),
    Input('menu-state', 'data')
)
def update_nav_class(open_state):
    return "navlinks show" if open_state else "navlinks"

if __name__ == '__main__':
    app.run(debug=True)