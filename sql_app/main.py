import sqlite3

from dash.dependencies import Input, Output
from dash import Dash, dcc, html
import pandas as pd
import plotly.express as px

from sql_app.crud import dict_country
from sql_app.models import RaceBoatIntermidiate, Race, RaceBoat
from sql_app.services import InitDataRaceBoatIntermediateModel, InitDataRaceModel, InitDataRaceBoatModel, \
    load_to_sql_competition

conn_first = sqlite3.connect("races")
data_races_first_connection = pd.read_sql_query("select * from races", conn_first)

conn_to_race_boat_first = sqlite3.connect("race_boat")
conn_to_race_boat_intermediate_first = sqlite3.connect("race_boat_intermediate")

data_races_boat_first_connection = pd.read_sql_query("select * from race_boat", conn_to_race_boat_first)
data_races_boat_intermediate_first_connection = pd.read_sql_query(
    "select * from race_boat_intermediate",
    conn_to_race_boat_intermediate_first
)


def _connect(data_races_boat, data_races_boat_intermediate):
    list_countries_done = []
    list_rank_country = []

    for i in range(len(data_races_boat_intermediate["raceBoatId"])):
        for j in range(len(data_races_boat["id"])):
            if data_races_boat_intermediate["raceBoatId"][i] == data_races_boat["id"][j]:
                list_countries_done.append(data_races_boat["DisplayName"][j])
                if data_races_boat['Rank'][j] == 1:
                    list_rank_country.append(data_races_boat_intermediate["Rank"][i])

    list_distance = [i for i in data_races_boat_intermediate["distance.DisplayName"]]
    list_rank = [i for i in data_races_boat_intermediate["Rank"]]
    list_all = [list_distance, list_rank, list_countries_done]
    return list_all


data_df = pd.DataFrame({
    "Дистанция": _connect(data_races_boat_first_connection, data_races_boat_intermediate_first_connection)[0],
    "Место": _connect(data_races_boat_first_connection, data_races_boat_intermediate_first_connection)[1],
    "Страны": _connect(data_races_boat_first_connection, data_races_boat_intermediate_first_connection)[2]
})
figure_init = px.bar(
    data_df,
    x="Дистанция",
    y="Место",
    color="Страны",
    barmode="group",
    title="График заезда с отображением места на каждой из промежуточных точек",
)

list_result = [i for i in data_races_boat_first_connection["ResultTime"]]
list_rank_boat = [i for i in data_races_boat_first_connection["Rank"]]
list_countries_boat = [i for i in data_races_boat_first_connection["DisplayName"]]
data_df_boat = pd.DataFrame({
    "Время на финише": list_result,
    "Место на финише": list_rank_boat,
    "Страны": list_countries_boat,
})
fig_boat = px.bar(
    data_df_boat,
    x="Время на финише",
    y="Место на финише",
    color="Страны",
    barmode="group",
    title="График заезда с отображением конечного результата по времени",
)

for i in range(len(data_races_boat_first_connection['Rank'])):
    if data_races_boat_first_connection['Rank'][i] == 1:
        country = data_races_boat_first_connection['DisplayName'][i]

races_in_competition = load_to_sql_competition.transform()

set_names_races = {i for i in races_in_competition["event.DisplayName"]}
list_names_races = list(set_names_races)
list_names_races = [{'label': i, 'value': i} for i in list_names_races]

external_stylesheets = [
    {
        "href": "https://fonts.googleapis.com/css2?"
                "family=Lato:wght@400;700&display=swap",
        "rel": "stylesheet",
    },
]

app = Dash(__name__, external_stylesheets=external_stylesheets)
app.title = "Аналитика соревнований по гребле"
server = app.server

app.layout = html.Div(
    children=[
        html.Div(
            children=[
                html.H1(
                    children="Аналитика гребли",
                    className="header-title"
                ),
                html.P(
                    children="Графики представлены для анализа данных по "
                             "определенному заезду по гребле",
                    className="header-description",
                ),
            ],
            className="header",
        ),
        html.Div(
            children=[
                html.Div(children="Соревнование", className="menu-title"),
                dcc.Dropdown(
                    id="competition",
                    options=list_names_races,
                    value="Men's Single Sculls",
                    clearable=False,
                    className="dropdown",
                ),
            ]
        ),
        # html.Div(
        #    children=[
        #        html.P(
        #            children=f"Страна {country}, занявшая 1 место проплыла со следующими результатами "
        #                     f"контрольные отметки {list_rank_country[0]} место на 500 м. - {list_rank_country[1]} "
        #                     f"место на 1000 м. - {list_rank_country[2]} место на 1500 м. - "
        #                     f"{list_rank_country[3]} место на 2000 м.",
        #            style={"fontSize": "18px", "color": "black", "text-align": "center"},
        #        ),
        #    ],
        # ),
        html.Div(
            children=[
                html.Div(
                    children=dcc.Graph(
                        id='plot',
                        figure=figure_init,
                        config={"displayModeBar": False},
                    ),
                    className="card",
                ),
                html.Div(
                    children=dcc.Graph(
                        figure=fig_boat,
                        config={"displayModeBar": False},
                    ),
                    className="card",
                ),
            ],
            className="wrapper",
        ),
        html.Div(id='my-output', ),
    ],
)
list_id = []


@app.callback(Output('plot', 'figure'),
              [Input('competition', 'value')])
def update_figure(competition):
    for row in dict_country.keys():
        if competition == row:
            list_id.append(dict_country[competition])

    init_race_names = InitDataRaceBoatModel(list_id[-1], RaceBoat)
    init_race_names.extract()
    init_race_names.transform()
    init_race_names.load()

    init_race_phase_names = InitDataRaceBoatIntermediateModel(list_id[-1], RaceBoatIntermidiate)
    init_race_phase_names.extract()
    init_race_phase_names.transform()
    init_race_phase_names.load()

    conn_to_race_boat_second = sqlite3.connect("race_boat")
    conn_to_race_boat_intermediate_second = sqlite3.connect("race_boat_intermediate")

    data_races_boat_second = pd.read_sql_query("select * from race_boat", conn_to_race_boat_second)
    data_races_boat_intermediate_second = pd.read_sql_query(
        "select * from race_boat_intermediate",
        conn_to_race_boat_intermediate_second
    )

    data_fig_df = pd.DataFrame({
        "Дистанция": _connect(data_races_boat_second, data_races_boat_intermediate_second)[0],
        "Место": _connect(data_races_boat_second, data_races_boat_intermediate_second)[1],
        "Страны": _connect(data_races_boat_second, data_races_boat_intermediate_second)[2]
    })
    fig = px.bar(
        data_fig_df,
        x="Дистанция",
        y="Место",
        color="Страны",
        barmode="group",
        title="График заезда с отображением места на каждой из промежуточных точек",
    )
    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
