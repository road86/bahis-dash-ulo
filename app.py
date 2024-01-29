import dash
import dash_bootstrap_components as dbc
from components import navbar
from dash import Dash, Input, Output, dcc, html

# Connect to your app pages
# from pages import dls, ulo, reports #,bahisdashpltOLD


app = Dash(
    __name__,
    use_pages=True,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    meta_tags=[{"name": "viewport", "content": "width=device-width"}],
    suppress_callback_exceptions=True,
)

# Define the navbar
nav = navbar.Navbar()

# Define the index page layout
# app.layout = html.Div([
# #    dcc.Location(id='url', refresh=False),
# #    nav,
#     #dash.page_container,
#     #html.Div(id='page-content', children=[]),
# ]) #, fluid=True,)

app.layout = html.Div(
    [
        dcc.Location(id="url", refresh=False),
        nav,
        html.Div([]),
        html.Div(id="page-1-display-value"),
        dash.page_container,
        dcc.Store(id="cache_bahis_data", storage_type="memory"),
        dcc.Store(id="cache_bahis_dgdata", storage_type="memory"),
        dcc.Store(id="cache_bahis_geodata", storage_type="memory"),
    ]
)


@app.callback(Output("page-1-display-value", "children"), Input("nav", "value"))
def display_value(value):
    return f"You have selected {value}"


# "complete" layout
app.validation_layout = html.Div(
    [
        #     dls.layout,
        #     ulo,
        #     report,m
        #     #app,
        #     #navbar,
        #     #index.layout,
        #     #bahisdashpltOLD,
        #     #page2,
    ]
)


# Create the callback to handle mutlipage inputs
# @app.callback(Output('page-content', 'children'),
#               [Input('url', 'pathname')])
# def display_page(pathname):
#     if pathname == '/dls':
#         return dls.layout
#     if pathname == '/ulo':
#         return ulo.layout
#     if pathname == '/reports':
#         return reports.layout
#     else: # if redirected to unknown link
#         return "404 Page Error! Please choose a link"

# Run the app on localhost:8050
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=80)
else:
    server = app.server
