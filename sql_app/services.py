from abc import ABC, abstractmethod

import requests
import pandas as pd


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

        self.races_in_competition_df.columns = self.races_in_competition_df.columns.str.replace(".", "")
        self.races_in_competition_df.columns = self.races_in_competition_df.columns.map(lambda col: col[0].lower() + col[1:])

    def load(self):
        """Загрузка в уже существующую модель"""
        ...


class InitDataRaceBoatModel(AbstractETL):
    def __init__(self, competition_id, model):
        self.competition_id = competition_id
        self.model = model

        super().__init__()

    def extract(self):
        """Загрузка из API"""
        ...

    def trasform(self):
        """Убираем столбцы, при необходимости преобразуем данные"""
        ...

    def load(self):
        """Загрузка в уже существующую модель"""
        ...


class InitDataRaceBoatIntermediateModel(AbstractETL):
    def __init__(self, competition_id, model):
        self.competition_id = competition_id
        self.model = model

        super().__init__()

    def extract(self):
        """Загрузка из API"""
        ...

    def trasform(self):
        """Убираем столбцы, при необходимости преобразуем данные"""
        ...

    def load(self):
        """Загрузка в уже существующую модель"""
        ...


if __name__ == '__main__':
    competition = "ccb6e115-c342-4948-b8e6-4525ff6d7832"  # WorldRowingCup III
    races = InitDataRaceModel(competition, "test_model")
    print(races.races_in_competition_df)
