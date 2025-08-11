import pandas as pd

df = pd.read_csv("/Users/yoyosui/Desktop/ultimate/spotify/spotify-2023.csv")
print("Columns:", df.columns.tolist())
for col in df.columns:
    print(repr(col))

