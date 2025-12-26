import dash
import dash_bootstrap_components as dbc
from data import load_and_process_data
from layout import create_layout
from callbacks import register_callbacks

app = dash.Dash(__name__, title="Netflix Dashboard PL", suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.DARKLY])
server = app.server


df = load_and_process_data()
app.layout = create_layout(df)
register_callbacks(app, df)

if __name__ == '__main__':
    app.run(debug=True)