from abc import ABC, abstractmethod

import requests
import pandas as pd

from sql_app.database import engine
from sql_app import models


class AbstractETL(ABC):
    def __init__(self):
        self.extract()
        self.transform()
        self.load()

    @abstractmethod
    def extract(self):
        """ """
        ...

    @abstractmethod
    def transform(self):
        ...

    @abstractmethod
    def load(self):
        ...

    @staticmethod
    def prepare_columns_names(df):
        df.columns = df.columns.str.replace(".", "")
        df.columns = df.columns.map(lambda col: col[0].lower() + col[1:])

        return df


class InitDataRaceModel(AbstractETL):
    def __init__(self, competition_id, model):
        self.competition_id = competition_id
        self.model = model

        self.races_in_competition_df = None

        super().__init__()

    def extract(self):
        """Загрузка из API"""
        competition_id = self.competition_id
        url_races_in_competition = f"https://world-rowing-api.soticcloud.net/stats/api/race/?include=racePhase,event.competition.competitionType,event.competition.competitionType.competitionCategory,event.boatClass&filter[event.competitionId]={competition_id}&sort[date]=asc"

        resp = requests.get(url_races_in_competition)
        races_in_competition = resp.json()["data"]

        self.races_in_competition_df = pd.json_normalize(races_in_competition)

    def transform(self):
        """Убираем столбцы, при необходимости преобразуем данные"""
        columns = [
            "id",  # uuid
            "DateString",  # datatime
            "Progression",
            "racePhase.DisplayName",
            "event.DisplayName",
            "event.boatClass.DisplayName",
        ]
        self.races_in_competition_df = self.races_in_competition_df[columns]

        self.races_in_competition_df["DateString"] = pd.to_datetime(self.races_in_competition_df["DateString"], utc=True)

        self.races_in_competition_df = self.prepare_columns_names(self.races_in_competition_df)

    def load(self):
        """Загрузка в уже существующую модель"""
        with engine.begin() as connection:  # https://docs.sqlalchemy.org/en/14/core/connections.html#using-transactions
            self.races_in_competition_df.to_sql(
                self.model.__tablename__,
                con=connection,
                if_exists="replace",
                index=False,
            )


class InitDataRaceBoatModel(AbstractETL):
    def __init__(self, races_id: list[str], model):
        self.races_id = races_id
        self.model = model

        self.race_boats_df = None
        self.race_boat_intermediates = []

        super().__init__()

    def extract(self):
        """Загрузка из API"""
        self.race_boats_df = pd.DataFrame()  # пустой датафрейм для

        for race_id in self.races_id:
            url_race_boat_final_result = f"https://world-rowing-api.soticcloud.net/stats/api/race/{race_id}?include=racePhase%2CraceBoats.raceBoatAthletes.person%2CraceBoats.invalidMarkResultCode%2CraceBoats.raceBoatIntermediates.distance&sortInclude%5BraceBoats.raceBoatIntermediates.ResultTime%5D=asc"

            resp = requests.get(url_race_boat_final_result)
            race_boat_final_result = resp.json()["data"]

            self.race_boats_df = self.race_boats_df.append(pd.json_normalize(race_boat_final_result, "raceBoats"))

    def transform(self):
        """Убираем столбцы, при необходимости преобразуем данные"""
        self.race_boat_intermediates = self.race_boats_df["raceBoatIntermediates"]

        columns = [
            "id",
            "raceId",  # Foreign Key Race model
            "DisplayName",
            "Rank",
            "Lane",
            "ResultTime",
        ]
        self.race_boats_df = self.race_boats_df[columns]

        self.race_boats_df = self.prepare_columns_names(self.race_boats_df)

    def load(self):
        """Загрузка в уже существующую модель"""
        with engine.begin() as connection:  # https://docs.sqlalchemy.org/en/14/core/connections.html#using-transactions
            self.race_boats_df.to_sql(
                self.model.__tablename__,
                con=connection,
                if_exists="replace",
                index=False,
            )


class InitDataRaceBoatIntermediateModel(AbstractETL):
    def __init__(self, race_boat_intermediates, model):
        self.model = model

        self.race_boat_intermediates = race_boat_intermediates
        self.race_boat_intermediates_df = None

        super().__init__()

    def extract(self):
        """Загрузка из API"""

        self.race_boat_intermediates_df = pd.concat([pd.json_normalize(row) for row in self.race_boat_intermediates],
                                                    ignore_index=True)

    def transform(self):
        """Убираем столбцы, при необходимости преобразуем данные"""
        columns = [
            'id',
            'raceBoatId',
            'Rank',
            'ResultTime',
            'distance.DisplayName'
        ]
        self.race_boat_intermediates_df = self.race_boat_intermediates_df[columns]

        self.race_boat_intermediates_df = self.prepare_columns_names(self.race_boat_intermediates_df)

    def load(self):
        """Загрузка в уже существующую модель"""
        with engine.begin() as connection:  # https://docs.sqlalchemy.org/en/14/core/connections.html#using-transactions
            self.race_boat_intermediates_df.to_sql(
                self.model.__tablename__,
                con=connection,
                if_exists="replace",
                index=False,
            )


if __name__ == '__main__':
    competition = "ccb6e115-c342-4948-b8e6-4525ff6d7832"  # WorldRowingCup III
    races = InitDataRaceModel(competition, model=models.Race)

    races_ids = races.races_in_competition_df["id"]
    boats = InitDataRaceBoatModel(races_ids, model=models.RaceBoat)

    boat_intermediates = InitDataRaceBoatIntermediateModel(boats.race_boat_intermediates, models.RaceBoatIntermidiate)
