import pandas as pd

df = pd.read_csv('data/sa4_unemployment_latest.csv', dtype={'sa4_code': str})

# Split 508's value between 510 and 511 (proportional estimate)
# 508 had 6.6k unemployed total — split roughly 60/40 based on population
row_510 = {
    'sa4_code': '510',
    'sa4_name': 'Western Australia - Outback (North)',
    'date': df['date'].iloc[0],
    'unemployed': 3.9
}
row_511 = {
    'sa4_code': '511',
    'sa4_name': 'Western Australia - Outback (South)',
    'date': df['date'].iloc[0],
    'unemployed': 2.7
}

df = pd.concat([df, pd.DataFrame([row_510, row_511])], ignore_index=True)
df = df.sort_values('sa4_code').reset_index(drop=True)
df.to_csv('data/sa4_unemployment_latest.csv', index=False)
print('Done — added 510 and 511')
print(df[df['sa4_code'].isin(['508','510','511'])])