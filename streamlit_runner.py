import pandas as pd
import streamlit
import requests
import seaborn as sns
import matplotlib.pyplot as plt
from rich.console import Console
import json
import geopandas as gpd
from rich.table import Table

data_path = "dataset/input/world-university-rankings/"
cwur_data = data_path + "cwur_data.csv"
education_expenditure_supplementary_data = data_path + "education_expenditure_supplementary_data.csv"
educational_attainment_supplementary_data = data_path + "educational_attainment_supplementary_data.csv"
school_and_country_table = data_path + "school_and_country_table.csv"
shanghaiData = data_path + "shanghai_data.csv"
times_data = data_path + "times_data.csv"

geo_api_endpoint = "http://api.positionstack.com/v1/forward"

console = Console()

def uni_serialize():
    df = pd.read_csv(cwur_data)
    return df

def get_geolocation(uni_name):
    GEO_API_KEY = "7e5af99fd356a3a854e866c2f16064eb"
    try:
        target = list(json.loads(requests.get(url=geo_api_endpoint + f"?access_key={GEO_API_KEY}&query={uni_name}").text)["data"])[0]
        return {"latitude": target["latitude"], "longitude": target["longitude"]}
    except: 
        return {"latitude" : None, "longitude" : None} # проверяем есть ли в принципе данные о геолокации
    

def add_geo(df):
    geo_lat = []
    geo_lon =[]
    if ("latitude" in df.columns.values or "longitude" in df.columns.values) : return # проверяем есть ли уже данные о геолокации, чтобы не считать их дважды
    for _ in df["institution"]:
        searched = get_geolocation(_)
        geo_lat.append(searched["latitude"])
        geo_lon.append(searched["longitude"])
    df.insert(3, "Latitude", geo_lat, True)
    df.insert(4, "Longitude", geo_lon, True)
    return df

if __name__ == "__main__":
    uni_data = uni_serialize()
    uni_data = add_geo(uni_data)
    geo_Latitude_NaN_count = uni_data.Latitude.isnull().sum()
    geo_Longitude_NaN_count = uni_data.Longitude.isnull().sum()
    streamlit.write("first app")
    table = Table()
    table.add_column(header="latitude is Nan longitude is not NaN", style=" bold italic cyan")
    table.add_column(header="longitude is NaN", style=" bold italic cyan")
    table.add_row(str(geo_Latitude_NaN_count), str(geo_Longitude_NaN_count))
    streamlit.write(console.print(table))
    streamlit.write(console.print(f"both latitude and longitude is NaN\n{is_geo_both_NaN}"))
    streamlit.write(console.print(f"[bold]No geolocation count:[/] {uni_data.Longitude.isnull().sum()}"))
    pie_chart_labels = ["Without geolocation", "With geolocation"]
    chart_colors = sns.color_palette("muted")
    plt.pie([geo_Latitude_NaN_count, len(uni_data)], labels=pie_chart_labels, colors=chart_colors, autopct='%.0f%%')
    streamlit.write(plt.show())
    states = gpd.read_file("usa-states-census-2014.shp")
    states.head()
    # штаты западного и восточного побережья
    west = [states["STUSPS"][i] for i in range(len(states)) if 'est' in states["region"][i]] 
    east = [states["STUSPS"][i] for i in range(len(states)) if 'ast' in states["region"][i]] 
    usa_uni = uni_data.loc[uni_data['country'] == 'USA', ["institution","Longitude", "Latitude", 'national_rank']]


    west_uni_avg = usa_uni.loc[usa_uni['Longitude'] < -95]

    east_uni_avg = usa_uni.loc[usa_uni['Longitude'] >= -95]
    console.print(f"East coast average national rating: {east_uni_avg.national_rank.mean()}\nWest coast average national rating: {west_uni_avg.national_rank.mean()}\n")
    west = states[states['region'] == 'West']
    southwest = states[states['region'] == 'Southwest']
    southeast = states[states['region'] == 'Southeast']
    midwest = states[states['region'] == 'Midwest']
    northeast = states[states['region'] == 'Northeast']
    us_boundary_map = states.boundary.plot(figsize=(18, 12), color='Black', linewidth=.5)
    west.plot(ax=us_boundary_map,  color="MistyRose")
    southwest.plot(ax=us_boundary_map, color="MistyRose")
    southeast.plot(ax=us_boundary_map, color="Plum")
    midwest.plot(ax=us_boundary_map, color="Plum")
    final_map = northeast.plot(ax=us_boundary_map, color="Plum")
    plt.xlim(-125, -65)
    plt.ylim(25, 50)
    us_boundary_map.scatter(x=usa_uni["Longitude"], y=usa_uni["Latitude"],s=usa_uni["national_rank"][::-1]**(16/14),c=usa_uni["national_rank"], cmap="Greys"),



    streamlit.write(plt.show())