from sqlalchemy import Column, Integer, String, Time, ForeignKey, Float
from sqlalchemy.orm import declarative_base, relationship

from datetime import datetime

Base = declarative_base()


class PvSource(Base):
    __tablename__ = 'pv_source'

    id = Column(Integer, primary_key=True)
    source = Column(String(15))
    collect_time = Column(Time)
    fs_station_code = Column(String(30))
    creation_date = Column(Time, default=datetime.now)

    def __repr__(self):
        return f'<PvSource(id={self.id}, source={self.source}, collect_time={self.collect_time}, fs_station_code={self.fs_station_code})>'


class FusionSolarData(Base):
    __tablename__ = 'fusion_solar_data'

    id = Column(Integer, primary_key=True)
    source_id = Column(Integer, ForeignKey('pv_source.id'))
    time = Column(Time)
    inverter_power = Column(Float)
    power_profit = Column(Float)
    creation_date = Column(Time, default=datetime.now)

    source = relationship(PvSource, primaryjoin=source_id ==
                          PvSource.id, post_update=True)

    def __repr__(self):
        return f'<FusionSolarData(id={self.id}, source_id={self.source_id}, time={self.time}, inverter_power={self.inverter_power}, power_profit{self.power_profit})>'


class EnergaData(Base):
    __tablename__ = 'energa_data'

    id = Column(Integer, primary_key=True)
    source_id = Column(Integer, ForeignKey('pv_source.id'))
    time = (Column(Time))
    energy_type = Column(String(10))
    zone_1 = Column(Float)
    zone_2 = Column(Float)
    zone_3 = Column(Float)
    creation_date = Column(Time, default=datetime.now)

    source = relationship(PvSource, primaryjoin=source_id ==
                          PvSource.id, post_update=True)

    def __repr__(self):
        return f'<EnergaData(id={self.id}, source_id={self.source_id}, time={self.time}, energy_type={self.energy_type}, zone_1={self.zone_1}, zone_2={self.zone_2}, zone_3={self.zone_3})>'
