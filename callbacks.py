from dash import Input, Output, State, ctx
import plotly.express as px
import pandas as pd
import numpy as np
from data import NETFLIX_RED


def register_callbacks(app, df):
    # --- KONFIGURACJA WSPÓLNA DLA WYKRESÓW ---
    layout_settings = dict(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white')
    )

    def apply_grid(fig):
        grid_style = dict(showgrid=True, gridcolor='rgba(255, 255, 255, 0.2)', zerolinecolor='rgba(255, 255, 255, 0.2)')
        fig.update_xaxes(**grid_style)
        fig.update_yaxes(**grid_style)
        return fig

    # 1. CALLBACK KPI + MAPA
    @app.callback(
        [Output('kpi-total', 'children'),
         Output('kpi-movie-perc', 'children'),
         Output('kpi-tv-perc', 'children'),
         Output('map-graph', 'figure')],
        [Input('type-filter', 'value'),
         Input('map-type', 'value')]
    )
    def update_kpi_and_map(selected_type, map_type):
        filtered = df if selected_type == 'All' else df[df['type'] == selected_type]
        total = len(filtered)
        if selected_type == 'All':
            m_perc = (len(df[df['type'] == 'Movie']) / len(df)) * 100
            t_perc = (len(df[df['type'] == 'TV Show']) / len(df)) * 100
            kpi2 = f"{m_perc:.1f}%"
            kpi3 = f"{t_perc:.1f}%"
        else:
            kpi2 = "-"
            kpi3 = "-"

        country_df = filtered[['show_id', 'country']].copy()
        country_df['country'] = country_df['country'].str.split(', ')
        country_df = country_df.explode('country')
        counts = country_df['country'].value_counts().reset_index()
        counts.columns = ['country', 'count']
        counts = counts[counts['country'] != 'Unknown']

        if map_type == 'area':
            fig = px.choropleth(
                counts, locations="country", locationmode='country names',
                color="count", hover_name="country",
                color_continuous_scale=px.colors.sequential.Reds,
                template='plotly_dark'
            )
        else:
            fig = px.scatter_geo(
                counts, locations="country", locationmode='country names',
                size="count", hover_name="country",
                color="count", color_continuous_scale=px.colors.sequential.Reds,
                template='plotly_dark', projection="natural earth"
            )

        fig.update_layout(**layout_settings, margin={"r": 0, "t": 0, "l": 0, "b": 0})
        fig.update_geos(bgcolor='rgba(0,0,0,0)', lakecolor='#1f1f1f', landcolor='#2b2b2b', subunitcolor='#141414')
        return total, kpi2, kpi3, fig

    # 2. CALLBACK TREND CZASOWY
    @app.callback(
        Output('trend-graph', 'figure'),
        [Input('type-filter', 'value'),
         Input('trend-interval', 'value'),
         Input('trend-split', 'value'),
         Input('trend-agg', 'value')]
    )
    def update_trend(selected_type, interval, view, agg):
        dff = df.copy()
        if selected_type != 'All':
            dff = dff[dff['type'] == selected_type]
        dff = dff.set_index('date_added')

        if view == 'split':
            grouped = dff.groupby([pd.Grouper(freq=interval), 'type']).size().reset_index(name='count')
            color_arg = 'type'
        else:
            grouped = dff.groupby(pd.Grouper(freq=interval)).size().reset_index(name='count')
            color_arg = None

        if agg == 'cumsum':
            if view == 'split':
                grouped['count'] = grouped.groupby('type')['count'].cumsum()
            else:
                grouped['count'] = grouped['count'].cumsum()

        fig = px.line(
            grouped, x='date_added', y='count', color=color_arg,
            markers=True, template='plotly_dark',
            color_discrete_map={'Movie': NETFLIX_RED, 'TV Show': '#ffffff'}
        )
        if color_arg is None: fig.update_traces(line_color=NETFLIX_RED)
        fig.update_layout(**layout_settings, title=None)

        apply_grid(fig)
        return fig

    @app.callback(
        [Output('month-pie-graph', 'figure'),
         Output('country-comparison-graph', 'figure')],
        [Input('type-filter', 'value'),
         Input('country-1', 'value'),
         Input('country-2', 'value')]
    )
    def update_new_charts(selected_type, c1, c2):

        dff = df if selected_type == 'All' else df[df['type'] == selected_type]


        dff_month = dff.copy()
        dff_month['month'] = dff_month['date_added'].dt.month_name()

        month_counts = dff_month['month'].value_counts().reset_index()
        month_counts.columns = ['month', 'count']

        fig_month = px.pie(
            month_counts, values='count', names='month',
            template='plotly_dark',
            color_discrete_sequence=px.colors.sequential.RdBu
        )
        fig_month.update_traces(textposition='inside', textinfo='percent+label')
        fig_month.update_layout(**layout_settings, margin={"r": 0, "t": 0, "l": 0, "b": 0})


        dff_country = dff[['date_added', 'year_added', 'country']].copy()
        dff_country['country'] = dff_country['country'].str.split(', ')
        dff_country = dff_country.explode('country')
        dff_country['country'] = dff_country['country'].str.strip()


        dff_compare = dff_country[dff_country['country'].isin([c1, c2])]


        comp_counts = dff_compare.groupby(['year_added', 'country']).size().reset_index(name='count')


        if comp_counts.empty:
            fig_comp = px.line(template='plotly_dark')
            fig_comp.add_annotation(text="Brak danych", showarrow=False)
        else:
            fig_comp = px.line(
                comp_counts, x='year_added', y='count', color='country',
                markers=True, template='plotly_dark'
            )
            apply_grid(fig_comp)

        fig_comp.update_layout(**layout_settings,
                               legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))

        return fig_month, fig_comp

    @app.callback(
        [Output('genre-bar-graph', 'figure'),
         Output('genre-hierarchy-graph', 'figure')],
        [Input('type-filter', 'value'),
         Input('genre-top-n', 'value'),
         Input('hierarchy-type', 'value'),
         Input('hierarchy-n', 'value')]
    )
    def update_genres(selected_type, bar_n, hier_type, hier_n):
        filtered = df if selected_type == 'All' else df[df['type'] == selected_type]
        genres = filtered[['show_id', 'listed_in']].copy()
        genres['listed_in'] = genres['listed_in'].str.split(', ')
        genres_exp = genres.explode('listed_in')
        counts = genres_exp['listed_in'].value_counts().reset_index()
        counts.columns = ['genre', 'count']

        bar_data = counts.head(int(bar_n))
        fig_bar = px.bar(
            bar_data, x='count', y='genre', orientation='h',
            text='count', template='plotly_dark'
        )
        fig_bar.update_traces(marker_color=NETFLIX_RED, textposition='outside')
        fig_bar.update_layout(**layout_settings, yaxis={'categoryorder': 'total ascending'})
        apply_grid(fig_bar)

        hier_data = counts.head(int(hier_n))
        if hier_type == 'treemap':
            fig_hier = px.treemap(hier_data, path=['genre'], values='count',
                                  color='count', color_continuous_scale='Reds', template='plotly_dark')
        else:
            fig_hier = px.sunburst(hier_data, path=['genre'], values='count',
                                   color='count', color_continuous_scale='Reds', template='plotly_dark')
        fig_hier.update_layout(**layout_settings, margin={"r": 0, "t": 0, "l": 0, "b": 0})
        return fig_bar, fig_hier


    @app.callback(
        [Output('duration-hist', 'figure'),
         Output('seasons-bar', 'figure')],
        [Input('type-filter', 'value')]
    )
    def update_duration_seasons(selected_type):

        movies = pd.DataFrame()
        if selected_type in ['All', 'Movie']:
            movies = df[df['type'] == 'Movie'].dropna(subset=['duration_min']).copy()

        if not movies.empty:
            bins = [0, 90, 120, 150, 9999]
            labels = ['< 90 min', '90-119 min', '120-149 min', '150+ min']
            movies['duration_cat'] = pd.cut(movies['duration_min'], bins=bins, labels=labels, right=False)

            dur_counts = movies['duration_cat'].value_counts().sort_index().reset_index()
            dur_counts.columns = ['category', 'count']

            fig_dur = px.bar(dur_counts, x='category', y='count', template='plotly_dark',
                             text='count', color_discrete_sequence=[NETFLIX_RED])
            fig_dur.update_traces(textposition='outside')
            fig_dur.update_layout(**layout_settings, xaxis_title=None, yaxis_title="Liczba filmów")
            apply_grid(fig_dur)
        else:
            fig_dur = px.bar(template='plotly_dark')
            fig_dur.update_layout(**layout_settings, title="Brak danych dla wybranego filtra")


        shows = pd.DataFrame()
        if selected_type in ['All', 'TV Show']:
            shows = df[df['type'] == 'TV Show'].dropna(subset=['seasons_count']).copy()

        if not shows.empty:
            def categorize_seasons(s):
                if s >= 5: return '5+'
                return str(int(s))

            shows['season_cat'] = shows['seasons_count'].apply(categorize_seasons)
            cat_order = ['1', '2', '3', '4', '5+']

            sea_counts = shows['season_cat'].value_counts().reset_index()
            sea_counts.columns = ['category', 'count']

            fig_sea = px.bar(sea_counts, x='category', y='count', template='plotly_dark',
                             text='count', color_discrete_sequence=['white'])
            fig_sea.update_layout(**layout_settings, xaxis={'categoryorder': 'array', 'categoryarray': cat_order},
                                  xaxis_title="Liczba sezonów")
            apply_grid(fig_sea)
        else:
            fig_sea = px.bar(template='plotly_dark')
            fig_sea.update_layout(**layout_settings, title="Brak danych dla wybranego filtra")

        return fig_dur, fig_sea


    @app.callback(
        [Output('director-graph', 'figure'),
         Output('rating-graph', 'figure'),
         Output('cast-graph', 'figure')],
        [Input('type-filter', 'value'),
         Input('director-slider', 'value'),
         Input('cast-slider', 'value')]
    )
    def update_people_ratings(selected_type, dir_n, cast_n):
        filtered = df if selected_type == 'All' else df[df['type'] == selected_type]


        dirs = filtered[['show_id', 'director']].copy()
        dirs = dirs[dirs['director'] != 'Unknown']
        dirs['director'] = dirs['director'].str.split(', ')
        dirs = dirs.explode('director')
        dir_counts = dirs['director'].value_counts().head(dir_n).reset_index()
        dir_counts.columns = ['director', 'count']

        fig_dir = px.bar(dir_counts, x='count', y='director', orientation='h',
                         template='plotly_dark', text='count')
        fig_dir.update_traces(marker_color=NETFLIX_RED)
        fig_dir.update_layout(**layout_settings, yaxis={'categoryorder': 'total ascending'})
        apply_grid(fig_dir)


        rat_counts = filtered.groupby(['rating', 'type']).size().reset_index(name='count')
        total_per_rating = rat_counts.groupby('rating')['count'].sum().sort_values(ascending=True)
        rating_order = total_per_rating.index.tolist()

        fig_rat = px.bar(rat_counts, x='count', y='rating', color='type',
                         orientation='h',
                         template='plotly_dark',
                         color_discrete_map={'Movie': NETFLIX_RED, 'TV Show': '#ffffff'},
                         barmode='stack')

        fig_rat.update_layout(**layout_settings, yaxis={'categoryorder': 'array', 'categoryarray': rating_order})
        apply_grid(fig_rat)


        casts = filtered[['show_id', 'cast']].copy()
        casts = casts[casts['cast'] != 'Unknown']
        casts['cast'] = casts['cast'].str.split(', ')
        casts = casts.explode('cast')
        cast_counts = casts['cast'].value_counts().head(cast_n).reset_index()
        cast_counts.columns = ['actor', 'count']

        fig_cast = px.bar(cast_counts, x='count', y='actor', orientation='h',
                          template='plotly_dark', text='count')
        fig_cast.update_traces(marker_color='white')
        fig_cast.update_layout(**layout_settings, yaxis={'categoryorder': 'total ascending'})
        apply_grid(fig_cast)

        return fig_dir, fig_rat, fig_cast


    @app.callback(
        [Output("modal-map", "is_open"),
         Output("modal-trend", "is_open"),
         Output("modal-month", "is_open"),
         Output("modal-country", "is_open"),
         Output("modal-genre", "is_open"),
         Output("modal-hierarchy", "is_open"),
         Output("modal-duration", "is_open"),
         Output("modal-seasons", "is_open"),
         Output("modal-director", "is_open"),
         Output("modal-rating", "is_open"),
         Output("modal-cast", "is_open")],
        [Input("open-modal-map", "n_clicks"), Input("close-modal-map", "n_clicks"),
         Input("open-modal-trend", "n_clicks"), Input("close-modal-trend", "n_clicks"),
         Input("open-modal-month", "n_clicks"), Input("close-modal-month", "n_clicks"),
         Input("open-modal-country", "n_clicks"), Input("close-modal-country", "n_clicks"),
         Input("open-modal-genre", "n_clicks"), Input("close-modal-genre", "n_clicks"),
         Input("open-modal-hierarchy", "n_clicks"), Input("close-modal-hierarchy", "n_clicks"),
         Input("open-modal-duration", "n_clicks"), Input("close-modal-duration", "n_clicks"),
         Input("open-modal-seasons", "n_clicks"), Input("close-modal-seasons", "n_clicks"),
         Input("open-modal-director", "n_clicks"), Input("close-modal-director", "n_clicks"),
         Input("open-modal-rating", "n_clicks"), Input("close-modal-rating", "n_clicks"),
         Input("open-modal-cast", "n_clicks"), Input("close-modal-cast", "n_clicks")],
        [State("modal-map", "is_open"),
         State("modal-trend", "is_open"),
         State("modal-month", "is_open"),
         State("modal-country", "is_open"),
         State("modal-genre", "is_open"),
         State("modal-hierarchy", "is_open"),
         State("modal-duration", "is_open"),
         State("modal-seasons", "is_open"),
         State("modal-director", "is_open"),
         State("modal-rating", "is_open"),
         State("modal-cast", "is_open")]
    )
    def toggle_modals(*args):
        ctx_msg = ctx.triggered_id
        num_modals = 11
        if not ctx_msg:
            return [False] * num_modals

        current_states = list(args[-num_modals:])

        ids = ["map", "trend", "month", "country", "genre", "hierarchy", "duration", "seasons", "director", "rating",
               "cast"]

        for i, uid in enumerate(ids):
            if f"open-modal-{uid}" == ctx_msg or f"close-modal-{uid}" == ctx_msg:
                current_states[i] = not current_states[i]
                return current_states

        return current_states