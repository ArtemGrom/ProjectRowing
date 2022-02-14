import pandas as pd
import requests

competition_id = "ccb6e115-c342-4948-b8e6-4525ff6d7832"  # WorldRowingCup III
url_races_in_competition = f"https://world-rowing-api.soticcloud.net/stats/api/race/?include=racePhase,event.competition.competitionType,event.competition.competitionType.competitionCategory,event.boatClass&filter[event.competitionId]={competition_id}&sort[date]=asc"

resp = requests.get(url_races_in_competition)
races_in_competition = resp.json()["data"]

races_in_competition_df = pd.json_normalize(races_in_competition)



columns = [
    "id",
    "DateString",
    "Progression",
    "racePhase.DisplayName",
    "event.DisplayName",
    "event.boatClass.DisplayName",
]
races_in_competition_df = races_in_competition_df[columns]

# create db all races WRC III
races_in_competition_df.to_sql(name=models.__tablename__, con=sqlite3.Connection, if_exists="append", index=False)

