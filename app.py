import dash
import dash_bootstrap_components as dbc

app = dash.Dash(__name__, title="Netflix Dashboard PL", suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.DARKLY])
server = app.server