from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship

from .database import Base


class Race(Base):
    ___tablename__ = "races"

    id = Column(Integer, primary_key=True, index=True)
    dateString = Column(DateTime, name="DateTime")
    progression = Column(String, name="Progression")
    racePhase_DisplayName = Column(String, name="Display race phase")
    event_DisplayName = Column(String, name="Display race event")
    event_boatClass_DisplayName = Column(String, name="Display boat class")


class RaceBoat(Base):
    ___tablename__ = "race_boat"

    id = Column(Integer, primary_key=True, index=True)
    raceId = Column(Integer, ForeignKey("races.id"))
    displayName = Column(String, name="Display Name")
    racePhase_DisplayName = Column(String, name="Display race phase")
    event_DisplayName = Column(String, name="Display race event")
    event_boatClass_DisplayName = Column(String, name="Display boat class")

