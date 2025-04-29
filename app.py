import dash
from dash import html, dcc

# Initialize the app
app = dash.Dash(__name__, use_pages=True)
server = app.server

navbar = html.Div([
    html.P("Air Quality Index Analysis"),
    html.Div([
        dcc.Link("Main", href="/"),
        dcc.Link("Objectives", href="/objectives"),
        dcc.Link("Major Findings", href="/major-findings"),
        dcc.Link("Analytical Methods", href="/analytical-methods")     
    ], className="navlinks")],
    className='navbar')

app.layout = html.Div([
    navbar,
    dash.page_container
])

if __name__ == '__main__':
    app.run(debug=True)