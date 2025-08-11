import pandas as pd
import re

def clean_spotify_data(file_path='/Users/yoyosui/Desktop/ultimate/spotify/spotify-2023.csv'):
    try:
        df = pd.read_csv(file_path)
        initial_rows = len(df)
    except FileNotFoundError:
        return

    def remove_chinese_chars(text):
        if not isinstance(text, str):
            return text
        return re.sub(r'[\u4e00-\u9fa5]', '', text).strip()
    
    if 'track_name' in df.columns:
        df['track_name'] = df['track_name'].apply(remove_chinese_chars)
    if 'artist(s)_name' in df.columns:
        df['artist(s)_name'] = df['artist(s)_name'].apply(remove_chinese_chars)

    current_rows = len(df)
    if 'streams' in df.columns:
        df['streams'] = df['streams'].astype(str)
        df = df[~df['streams'].str.contains(r'[a-zA-Z]', na=False)]
        df['streams'] = pd.to_numeric(df['streams'], errors='coerce')
        df.dropna(subset=['streams'], inplace=True)
        print(f"1:删除了 {current_rows - len(df)} ")
        current_rows = len(df)

    for col, low, high in [('released_year', 1000, 9999), ('released_month', 1, 12), ('released_day', 1, 31)]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            df.dropna(subset=[col], inplace=True)
            df = df[df[col].between(low, high)]
            print(f"for '{col}'，删除了 {current_rows - len(df)} ")
            current_rows = len(df)

    playlist_chart_cols = [
        'in_spotify_charts', 'in_apple_playlists', 
        'in_apple_charts',
    ]
    for col in playlist_chart_cols:
        if col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].str.replace(',', '', regex=False)
            df[col] = pd.to_numeric(df[col], errors='coerce')
    df.dropna(subset=[c for c in playlist_chart_cols if c in df.columns], inplace=True)
    
    for col in playlist_chart_cols:
        if col in df.columns:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            upper_bound = Q3 + 6 * IQR
            df = df[df[col] <= upper_bound]
    print(f"5: 删除了 {current_rows - len(df)} ")
    current_rows = len(df)

    if 'bpm' in df.columns:
        df['bpm'] = pd.to_numeric(df['bpm'], errors='coerce')
        df.dropna(subset=['bpm'], inplace=True)
        print(f"6:删除了 {current_rows - len(df)} ")
        current_rows = len(df)

    if 'key' in df.columns and df['key'].dtype == 'object':
        valid_keys = df['key'].str.match(r'^[A-G]#?$', na=False)
        blank_keys = pd.isna(df['key'])
        df = df[valid_keys | blank_keys]
        print(f"7，删除了 {current_rows - len(df)} ")
        current_rows = len(df)

    if 'mode' in df.columns and df['mode'].dtype == 'object':
        df = df[df['mode'].isin(['Major', 'Minor'])]
        print(f" 8: 删除了 {current_rows - len(df)} ")
        current_rows = len(df)

    percentage_cols = [
        'danceability_%', 'valence_%', 'energy_%', 'acousticness_%',
        'instrumentalness_%', 'liveness_%', 'speechiness_%'
    ]
    for col in percentage_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            df = df[df[col].between(0, 100)]
    df.dropna(subset=[c for c in percentage_cols if c in df.columns], inplace=True)
    print(f"9: 删除了 {current_rows - len(df)} ")
    
    final_rows = len(df)

    output_filename = '/Users/yoyosui/Desktop/ultimate/spotify/spotify_2023_cleaned.csv'
    df.to_csv(output_filename, index=False, encoding='utf-8-sig')
    print("done")

clean_spotify_data()

