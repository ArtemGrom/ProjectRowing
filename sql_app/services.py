import sqlite3
from abc import ABC, abstractmethod
import requests
import pandas as pd

from sql_app.models import Race, RaceBoat, RaceBoatIntermidiate


class AbstractETL(ABC):

    def __init__(self):
        self.extract()
        self.transform()
        self.load()

    @abstractmethod
    def extract(self):
        """Загрузка из API"""
        ...

    @abstractmethod
    def transform(self):
        """Убираем столбцы, при необходимости преобразуем данные"""
        ...

    @abstractmethod
    def load(self):
        """Загрузка в уже существующую модель"""
        ...


class InitDataRaceModel(AbstractETL):
    def __init__(self, competition_id: str, model):
        self.competition_id = competition_id
        self.model = model
        super().__init__()

    def extract(self):
        url_races_in_competition = f"https://world-rowing-api.soticcloud.net/stats/api/race/?include=racePhase," \
                                   f"event.competition.competitionType," \
                                   f"event.competition.competitionType.competitionCategory," \
                                   f"event.boatClass&filter[event.competitionId]={self.competition_id}&sort[date]=asc"

        response = requests.get(url_races_in_competition)
        races_in_competition = response.json()["data"]
        return races_in_competition

    def transform(self):
        races_in_competition_df = pd.json_normalize(self.extract())
        columns = [
            "id",
            "DateString",
            "Progression",
            "racePhase.DisplayName",
            "event.DisplayName",
            "event.boatClass.DisplayName",
        ]
        races_in_competition_df = races_in_competition_df[columns]
        return races_in_competition_df

    def load(self):
        conn = sqlite3.connect(self.model.__tablename__)
        self.transform().to_sql(
            name=self.model.__tablename__,
            con=conn,
            if_exists="replace",
            index=False
        )


class InitDataRaceBoatModel(AbstractETL):
    def __init__(self, race_id: str, model):
        self.race_id = race_id
        self.model = model
        super().__init__()

    def extract(self):
        url_race_boat_final_result = f"https://world-rowing-api.soticcloud.net/stats/api/race/{self.race_id}" \
                                     f"?include=racePhase%2CraceBoats.raceBoatAthletes.person%2" \
                                     f"CraceBoats.invalidMarkResultCode%2CraceBoats.raceBoatIntermediates.distance&" \
                                     f"sortInclude%5BraceBoats.raceBoatIntermediates.ResultTime%5D=asc"

        response = requests.get(url_race_boat_final_result)
        race_boat_final_result = response.json()["data"]
        return race_boat_final_result

    def transform(self):
        race_boats_phase_df = pd.json_normalize(self.extract(), "raceBoats")
        columns_race_boats = [
            "id",
            "raceId",
            "DisplayName",
            "Rank",
            "Lane",
            "ResultTime",
        ]
        race_boats_df = race_boats_phase_df[columns_race_boats]
        return race_boats_df

    def load(self):
        conn_race_boat = sqlite3.connect(self.model.__tablename__)
        self.transform().to_sql(
            name=self.model.__tablename__,
            con=conn_race_boat,
            if_exists="replace",
            index=False
        )


class InitDataRaceBoatIntermediateModel(AbstractETL):
    def __init__(self, race_id, model):
        self.race_id = race_id
        self.model = model
        super().__init__()

    def extract(self):
        one_race_in_phase = InitDataRaceBoatModel(self.race_id, RaceBoat)
        race_phase_df = pd.json_normalize(one_race_in_phase.extract(), "raceBoats")
        race_boat_intermediate_df = pd.concat(
            [pd.json_normalize(row) for row in race_phase_df["raceBoatIntermediates"]],
            ignore_index=True)
        return race_boat_intermediate_df

    def transform(self):
        columns_race_boats_intermediate = [
            "id",
            "raceBoatId",
            "Rank",
            "ResultTime",
            "distance.DisplayName"
        ]
        race_boat_intermediate_df = self.extract()[columns_race_boats_intermediate]
        return race_boat_intermediate_df

    def load(self):
        conn_race_boat = sqlite3.connect(self.model.__tablename__)
        self.transform().to_sql(
            name=self.model.__tablename__,
            con=conn_race_boat,
            if_exists="replace",
            index=False
        )


load_to_sql_competition = InitDataRaceModel("ccb6e115-c342-4948-b8e6-4525ff6d7832", Race)
load_to_sql_competition.extract()
load_to_sql_competition.transform()
load_to_sql_competition.load()

load_to_sql_phase = InitDataRaceBoatModel('14d58044-68d8-444b-a89e-2679fe653e97', RaceBoat)
load_to_sql_phase.extract()
load_to_sql_phase.transform()
load_to_sql_phase.load()

load_to_sql_with_distance = InitDataRaceBoatIntermediateModel('14d58044-68d8-444b-a89e-2679fe653e97',
                                                              RaceBoatIntermidiate)
load_to_sql_with_distance.extract()
load_to_sql_with_distance.transform()
load_to_sql_with_distance.load()