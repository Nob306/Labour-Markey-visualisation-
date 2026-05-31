import pandas as pd, json

with open('data/sa4_topo.json') as f:
    topo = json.load(f)

features = topo['objects']['SA4_2021_AUST_GDA2020']['geometries']
topo_codes = set(f['properties']['SA4_CODE21'] for f in features if f.get('properties'))

df = pd.read_csv('data/sa4_unemployment_latest.csv', dtype={'sa4_code': str})
csv_codes = set(df['sa4_code'].tolist())

missing = csv_codes - topo_codes
print('Missing from TopoJSON:', sorted(missing))

for code in missing:
    row = df[df['sa4_code'] == code]
    if len(row):
        name = row['sa4_name'].values[0]
        val = row['unemployed'].values[0]
        print(f'  Code {code}: {name}, unemployed: {val}')