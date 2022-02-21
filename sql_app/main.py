import sqlite3

from dash import Dash, dcc, html
import pandas as pd
import plotly.express as px

from sql_app.create_db import race_boat_intermediate_df, race_boats_df


external_stylesheets = [
    {
        "href": "https://fonts.googleapis.com/css2?"
                "family=Lato:wght@400;700&display=swap",
        "rel": "stylesheet",
    },
]

conn = sqlite3.connect("races")
conn_to_race_boat = sqlite3.connect("race_boat")
conn_to_race_boat_intermediate = sqlite3.connect("race_boat_intermediate")


data_races = pd.read_sql_query("select * from races", conn)
# data_races["DateString"] = pd.to_datetime(data_races["DateString"], format="%Y-%m-%d")

data_races_boat = pd.read_sql_query("select * from race_boat", conn_to_race_boat)
data_races_boat_intermediate = pd.read_sql_query("select * from race_boat_intermediate", conn_to_race_boat_intermediate)

app = Dash(__name__, external_stylesheets=external_stylesheets)
app.title = "Аналитика соревнований по гребле"
server = app.server

list_countries_done = []

for i in range(len(race_boat_intermediate_df["raceBoatId"])):
    for j in range(len(race_boats_df["id"])):
        if race_boat_intermediate_df["raceBoatId"][i] == race_boats_df["id"][j]:
            list_countries_done.append(race_boats_df["DisplayName"][j])



list_distance = [i for i in data_races_boat_intermediate["distance.DisplayName"]]
list_rank = [i for i in data_races_boat_intermediate["Rank"]]
data_df = pd.DataFrame({"Дистанция": list_distance, "Место": list_rank, "Страны": list_countries_done})
fig = px.bar(data_df, x="Дистанция", y="Место", color="Страны", barmode="group")



list_result = [i for i in data_races_boat["ResultTime"]]
list_rank_boat= [i for i in data_races_boat["Rank"]]
list_countries_boat = [i for i in data_races_boat["DisplayName"]]
data_df_boat = pd.DataFrame({"Результат финиша": list_result, "Место на финише": list_rank_boat, "Страны участники": list_countries_boat})
fig_boat = px.bar(data_df_boat, x="Результат финиша", y="Место на финише", color="Страны участники", barmode="group")


for i in range(len(data_races_boat['Rank'])):
    if data_races_boat['Rank'][i] == 1:
        country = data_races_boat['DisplayName'][i]

list_rank_country = []
for i in range(len(race_boat_intermediate_df["raceBoatId"])):
    for j in range(len(race_boats_df["id"])):
        if race_boat_intermediate_df["raceBoatId"][i] == race_boats_df["id"][j]:
            if race_boats_df['Rank'][j] == 1:
                list_rank_country.append(race_boat_intermediate_df["Rank"][i])


app.layout = html.Div(
    children=[
        html.H1(children="Аналитика гребли",),
        html.P(
            children="Графики представлены для анализа данных по "
            "определенному заезду по гребле",
        ),
        dcc.Graph(figure=fig),
        dcc.Graph(figure=fig_boat),
        html.P(children="Ниже выведена строка с местами на 500 м., 1000 м., 1500 м., 2000 м."),
        html.P(children=f"Страна {country}, занявшая 1 место проплыла со следующими результатами контрольные отметки {list_rank_country[0]} - {list_rank_country[1]} - {list_rank_country[2]} - {list_rank_country[3]}"),
    ]
)


if __name__ == '__main__':
    app.run_server(debug=True)
    # print(len(list_rank), len(list_countries), len(list_distance))"""

