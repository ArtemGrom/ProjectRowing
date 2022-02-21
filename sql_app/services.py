from abc import ABC, abstractmethod


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
