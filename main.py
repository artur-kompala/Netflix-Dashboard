from app import app
from data import load_and_process_data
from layout import create_layout
from callbacks import register_callbacks
import dash_bootstrap_components as dbc

# Wczytaj dane
df = load_and_process_data()

app.layout = create_layout(df)
register_callbacks(app, df)

if __name__ == '__main__':
    app.run(debug=True)