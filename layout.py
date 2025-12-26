from dash import dcc, html
import dash_bootstrap_components as dbc
from data import get_data_date
import pandas as pd



def create_card(title, graph_id, modal_id, modal_title, modal_text, controls=None, extra_content=None):
    header_children = [
        html.Span(title, className="card-label align-middle"),
        dbc.Button("?", id=f"open-{modal_id}", color="link", size="sm", className="info-btn float-end p-0 ms-2")
    ]

    if controls:
        header_children.append(html.Div(controls, className="card-controls float-end me-2"))

    card_content = [
        dbc.CardHeader(header_children, className="custom-card-header"),
        dbc.CardBody([
            extra_content if extra_content else html.Div(),
            dcc.Graph(id=graph_id, className="custom-graph")
        ], className="custom-card-body")
    ]

    modal = dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle(modal_title), className="custom-modal-header"),
        dbc.ModalBody(modal_text, className="custom-modal-body"),
        dbc.ModalFooter(
            dbc.Button("Zamknij", id=f"close-{modal_id}", className="ms-auto custom-btn-close", n_clicks=0),
            className="custom-modal-footer"
        ),
    ], id=modal_id, is_open=False, className="custom-modal")

    return dbc.Card(card_content + [modal], className="custom-card mb-4")


def create_layout(df):
    last_date = get_data_date(df)

    all_countries = df['country'].str.split(', ').explode().dropna().str.strip()
    # Filter out Unknown and sort
    unique_countries = sorted(list(set(all_countries[all_countries != 'Unknown'])))
    country_options = [{'label': c, 'value': c} for c in unique_countries]

    return dbc.Container(fluid=True, className="app-container p-4", children=[

        # --- 1. HEADER (Nagłówek - Wstęp i Tytuł) ---
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.H1("Netflix Movies & TV Shows Dashboard", className="app-title"),
                    html.P([
                        "Interaktywny dashboard analizujący filmy i seriale z Netflix",
                        html.Br(),
                        html.Span("Źródło: Kaggle Netflix Movies & TV Shows | Autor: Artur Kompała", className="author-info")
                    ], className="app-description")
                ], className="header-content text-center")
            ], width=12)
        ], className="header-section mb-4"),

        # --- 2. GŁÓWNY FILTR ---
        dbc.Row([
            dbc.Col([
                html.Label("Filtruj widok:", className="filter-label fw-bold mb-1"),
                dbc.Select(
                    id='type-filter',
                    options=[
                        {'label': 'Wszystkie (All)', 'value': 'All'},
                        {'label': 'Filmy (Movies)', 'value': 'Movie'},
                        {'label': 'Seriale (TV Shows)', 'value': 'TV Show'}
                    ],
                    value='All',
                    className="main-filter-select mb-4"
                )
            ], width={'size': 4, 'offset': 4}, className="filter-wrapper")
        ]),

        # --- 3. KPI ---
        dbc.Row([
            dbc.Col(dbc.Card(dbc.CardBody([
                html.H4(id='kpi-total', className="kpi-value text-danger"),
                html.P("Łączna liczba tytułów", className="kpi-label text-muted small")
            ]), className="kpi-card"), width=4),
            dbc.Col(dbc.Card(dbc.CardBody([
                html.H4(id='kpi-movie-perc', className="kpi-value"),
                html.P("Filmy", className="kpi-label text-muted small")
            ]), className="kpi-card"), width=4),
            dbc.Col(dbc.Card(dbc.CardBody([
                html.H4(id='kpi-tv-perc', className="kpi-value"),
                html.P("Seriale", className="kpi-label text-muted small")
            ]), className="kpi-card"), width=4),
        ], className="kpi-section mb-4"),

        # --- 4. MAPA ---
        dbc.Row([
            dbc.Col(create_card(
                title="Geografia Produkcji",
                graph_id='map-graph',
                modal_id='modal-map',
                modal_title="O Mapie",
                modal_text="Ta mapa wizualizuje liczbę produkcji dostępnych na Netflix w podziale na kraje pochodzenia.",
                controls=html.Div([
                    dbc.RadioItems(
                        id="map-type",
                        options=[
                            {"label": "Obszar", "value": "area"},
                            {"label": "Bąbelki", "value": "bubble"},
                        ],
                        value="area",
                        inline=True,
                        className="custom-radio"
                    )
                ])
            ), width=12)
        ], className="mb-4"),

        # --- 5. TREND CZASOWY ---
        dbc.Row([
            dbc.Col(create_card(
                title="Dynamika dodawania treści",
                graph_id='trend-graph',
                modal_id='modal-trend',
                modal_title="O Trendach",
                modal_text="Wykres liniowy pokazujący liczbę dodawanych filmów i seriali w czasie.",
                extra_content=dbc.Row([
                    dbc.Col([
                        html.Label("Interwał:", className="control-label small text-muted"),
                        dbc.RadioItems(
                            id='trend-interval',
                            options=[{'label': 'Miesiąc', 'value': 'M'}, {'label': 'Kwartał', 'value': 'Q'},
                                     {'label': 'Rok', 'value': 'Y'}],
                            value='Y', inline=True, className="custom-radio"
                        )
                    ], width=4),
                    dbc.Col([
                        html.Label("Widok:", className="control-label small text-muted"),
                        dbc.RadioItems(
                            id='trend-split',
                            options=[{'label': 'Razem', 'value': 'total'},
                                     {'label': 'Filmy vs Seriale', 'value': 'split'}],
                            value='split', inline=True, className="custom-radio"
                        )
                    ], width=4),
                    dbc.Col([
                        html.Label("Agregacja:", className="control-label small text-muted"),
                        dbc.RadioItems(
                            id='trend-agg',
                            options=[{'label': 'Ilość', 'value': 'count'}, {'label': 'Narastająco', 'value': 'cumsum'}],
                            value='count', inline=True, className="custom-radio"
                        )
                    ], width=4),
                ], className="controls-row mb-3")
            ), width=12)
        ], className="mb-4"),

        # --- NEW: MIESIĄCE I PORÓWNANIE KRAJÓW ---
        dbc.Row([
            dbc.Col(create_card(
                title="Miesięczny rozkład premier",
                graph_id='month-pie-graph',
                modal_id='modal-month',
                modal_title="Miesiące",
                modal_text="Wykres kołowy pokazujący, w którym miesiącu pojawia się najwięcej premier.",
            ), width=6),

            dbc.Col(create_card(
                title="Porównanie Krajów",
                graph_id='country-comparison-graph',
                modal_id='modal-country',
                modal_title="Porównanie Krajów",
                modal_text="Porównanie liczby dodawanych produkcji w czasie dla dwóch wybranych państw.",
                extra_content=dbc.Row([
                    dbc.Col([
                        html.Label("Kraj 1", className="small text-muted"),
                        dcc.Dropdown(id='country-1', options=country_options, value='India', clearable=False,
                                     className="text-dark")
                    ], width=6),
                    dbc.Col([
                        html.Label("Kraj 2", className="small text-muted"),
                        dcc.Dropdown(id='country-2', options=country_options, value='United States', clearable=False,
                                     className="text-dark")
                    ], width=6)
                ], className="mb-2")
            ), width=6),
        ], className="mb-4"),

        # --- 6. GATUNKI ---
        dbc.Row([
            dbc.Col(create_card(
                title="Top Gatunki",
                graph_id='genre-bar-graph',
                modal_id='modal-genre',
                modal_title="O Gatunkach",
                modal_text="Ranking najczęściej występujących gatunków.",
                controls=html.Div([
                    dbc.Select(
                        id='genre-top-n',
                        options=[{'label': 'Top 10', 'value': 10}, {'label': 'Top 15', 'value': 15},
                                 {'label': 'Top 20', 'value': 20}],
                        value=10, size="sm", className="custom-select-sm", style={'width': '100px'}
                    )
                ])
            ), width=6),

            dbc.Col(create_card(
                title="Szczegóły Gatunków",
                graph_id='genre-hierarchy-graph',
                modal_id='modal-hierarchy',
                modal_title="Hierarchia",
                modal_text="Alternatywny widok rozkładu gatunków.",
                controls=html.Div([
                    dbc.RadioItems(
                        id='hierarchy-type',
                        options=[{'label': 'Treemap', 'value': 'treemap'}, {'label': 'Sunburst', 'value': 'sunburst'}],
                        value='treemap', inline=True, className="custom-radio me-2"
                    ),
                    dbc.Input(id="hierarchy-n", type="number", value=20, min=5, max=50, step=5, size="sm",
                              className="custom-number-input", style={'width': '60px', 'display': 'inline-block'})
                ])
            ), width=6),
        ], className="mb-4"),

        # --- 7. CZAS TRWANIA I SEZONY ---
        dbc.Row([
            dbc.Col(create_card(
                title="Czas Trwania Filmów",
                graph_id='duration-hist',
                modal_id='modal-duration',
                modal_title="Czas Trwania",
                modal_text="Podział filmów na kategorie długości.",
            ), width=6),

            dbc.Col(create_card(
                title="Liczba Sezonów",
                graph_id='seasons-bar',
                modal_id='modal-seasons',
                modal_title="Sezony",
                modal_text="Ile sezonów mają zazwyczaj seriale na Netflix?",
            ), width=6),
        ], className="mb-4"),

        # --- 8. OBSADA ---
        dbc.Row([
            dbc.Col(create_card(
                title="Top Obsada",
                graph_id='cast-graph',
                modal_id='modal-cast',
                modal_title="Aktorzy",
                modal_text="Najpopularniejsi aktorzy i aktorki.",
                extra_content=html.Div([
                    html.Label("Ile pokazać?", className="control-label small me-2"),
                    dcc.Slider(min=5, max=30, step=5, value=10, id='cast-slider',
                               marks={i: str(i) for i in range(5, 31, 5)}, className="custom-slider")
                ], className="mb-2")
            ), width=12),
        ], className="mb-4"),

        # --- 9. REŻYSERZY I RATINGI ---
        dbc.Row([
            dbc.Col(create_card(
                title="Top Reżyserzy",
                graph_id='director-graph',
                modal_id='modal-director',
                modal_title="Reżyserzy",
                modal_text="Najaktywniejsi reżyserzy.",
                extra_content=html.Div([
                    html.Label("Ile pokazać?", className="control-label small me-2"),
                    dcc.Slider(min=5, max=30, step=5, value=10, id='director-slider',
                               marks={i: str(i) for i in range(5, 31, 5)}, className="custom-slider")
                ], className="mb-2")
            ), width=6),

            dbc.Col(create_card(
                title="Kategorie Wiekowe",
                graph_id='rating-graph',
                modal_id='modal-rating',
                modal_title="Kategorie Wiekowe",
                modal_text="Rozkład kategorii wiekowych dla filmów i seriali.",
            ), width=6),
        ], className="mb-4"),


    ])