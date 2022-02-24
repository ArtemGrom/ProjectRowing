from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Time
from sqlalchemy.orm import relationship

from sql_app.database import Base


class Race(Base):
    __tablename__ = "races"

    id = Column(Integer, primary_key=True, index=True)
    dateString = Column(DateTime, name="DateTime")
    progression = Column(String, name="Progression")
    racePhaseDisplayName = Column(String, name="Race phase")
    eventDisplayName = Column(String, name="Race event")
    eventBoatClassDisplayName = Column(String, name="Boat class")

    boat = relationship("RaceBoat", back_populates="race")


class RaceBoat(Base):
    __tablename__ = "race_boat"

    id = Column(Integer, primary_key=True, index=True)
    raceId = Column(Integer, ForeignKey("races.id"))
    displayName = Column(String, name="Name")
    rank = Column(Integer, name="Rank")
    line = Column(Integer, name="line")
    resultTime = Column(Time, name="Time")

    race = relationship("Race", back_populates="boat")
    race_intermediate = relationship("RaceBoatIntermidiate", back_populates="race_boat")


class RaceBoatIntermidiate(Base):
    __tablename__ = "race_boat_intermediate"

    id = Column(Integer, primary_key=True, index=True)
    raceBoatId = Column(Integer, ForeignKey("race_boat.id"))
    rank = Column(Integer, name="Rank")
    resultTime = Column(Time, name="Time")
    distanceDisplayName = Column(String, name="Distance")

    race_boat = relationship("RaceBoat", back_populates="race_intermediate")
