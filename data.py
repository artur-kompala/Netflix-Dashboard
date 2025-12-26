import pandas as pd

NETFLIX_RED = '#E50914'


def load_and_process_data():
    try:
        df = pd.read_csv('netflix_titles.csv')

        # 1. Konwersja dat
        df['date_added'] = pd.to_datetime(df['date_added'].str.strip(), format='mixed', errors='coerce')
        df = df.dropna(subset=['date_added'])
        df['year_added'] = df['date_added'].dt.year

        # 2. Uzupełnienie braków
        df['country'] = df['country'].fillna('Unknown')
        df['rating'] = df['rating'].fillna('Unknown')
        df['director'] = df['director'].fillna('Unknown')
        df['cast'] = df['cast'].fillna('Unknown')


        def extract_minutes(x):
            if isinstance(x, str) and 'min' in x:
                return int(x.split(' ')[0])
            return None

        def extract_seasons(x):
            if isinstance(x, str) and 'Season' in x:
                return int(x.split(' ')[0])
            return None

        df['duration_min'] = df['duration'].apply(extract_minutes)
        df['seasons_count'] = df['duration'].apply(extract_seasons)

        return df
    except FileNotFoundError:
        print("BŁĄD: Nie znaleziono pliku 'netflix_titles.csv'.")
        return pd.DataFrame()


def get_data_date(df):
    if not df.empty and 'date_added' in df.columns:
        return df['date_added'].max().strftime('%Y-%m-%d')
    return "N/A"