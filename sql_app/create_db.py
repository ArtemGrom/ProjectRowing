import sqlite3
import pandas as pd
import requests
from sql_app.models import Race, RaceBoat, RaceBoatIntermidiate


competition_id = "ccb6e115-c342-4948-b8e6-4525ff6d7832"  # WorldRowingCup III
url_races_in_competition = f"https://world-rowing-api.soticcloud.net/stats/api/race/?include=racePhase," \
                           f"event.competition.competitionType,event.competition.competitionType.competitionCategory," \
                           f"event.boatClass&filter[event.competitionId]={competition_id}&sort[date]=asc"

resp = requests.get(url_races_in_competition)
races_in_competition = resp.json()["data"]

races_in_competition_df = pd.json_normalize(races_in_competition)

list_race_id = [i for i in races_in_competition_df["id"]]

columns = [
    "id",
    "DateString",
    "Progression",
    "racePhase.DisplayName",
    "event.DisplayName",
    "event.boatClass.DisplayName",
]
races_in_competition_df = races_in_competition_df[columns]

race_id = list_race_id[71]

url_race_boat_final_result = f"https://world-rowing-api.soticcloud.net/stats/api/race/{race_id}" \
                             f"?include=racePhase%2CraceBoats.raceBoatAthletes.person%2" \
                             f"CraceBoats.invalidMarkResultCode%2CraceBoats.raceBoatIntermediates.distance&" \
                             f"sortInclude%5BraceBoats.raceBoatIntermediates.ResultTime%5D=asc"

response = requests.get(url_race_boat_final_result)
race_boat_final_result = response.json()["data"]

race_boats_df = pd.json_normalize(race_boat_final_result, "raceBoats")

race_boat_intermediate_df = pd.concat(
    [pd.json_normalize(row) for row in race_boats_df["raceBoatIntermediates"]],
    ignore_index=True)

columns_race_boats = [
    "id",
    "raceId",
    "DisplayName",
    "Rank",
    "Lane",
    "ResultTime",
]
race_boats_df = race_boats_df[columns_race_boats]


columns_race_boats_intermediate = [
    "id",
    "raceBoatId",
    "Rank",
    "ResultTime",
    "distance.DisplayName"
]
race_boat_intermediate_df = race_boat_intermediate_df[columns_race_boats_intermediate]


if __name__ == '__main__':
    # create db all races WRC III
    conn = sqlite3.connect(Race.__tablename__)
    races_in_competition_df.to_sql(
        name=Race.__tablename__,
        con=conn,
        if_exists="replace",
        index=False
    )

    # create db 1 competition
    conn_race_boat = sqlite3.connect(RaceBoat.__tablename__)
    race_boats_df.to_sql(
        name=RaceBoat.__tablename__,
        con=conn_race_boat,
        if_exists="replace",
        index=False
    )
    
    # create db 1 phase
    conn_race_boat_intermediate = sqlite3.connect(RaceBoatIntermidiate.__tablename__)
    race_boat_intermediate_df.to_sql(
        name=RaceBoatIntermidiate.__tablename__,
        con=conn_race_boat_intermediate,
        if_exists="replace",
        index=False
    )
