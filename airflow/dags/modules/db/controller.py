from sqlalchemy import create_engine
from sqlalchemy import func
from sqlalchemy.orm import sessionmaker

from datetime import datetime

from modules.db.model import FusionSolarData, EnergaData

from modules.utils import util

class Controller:
    def __init__(self, data_list, pv_source=None):

        if data_list == None or not isinstance(data_list, list) or data_list[0] == None:
            raise Exception(
                'data_list must be non empty list')

        self._pv_source = pv_source

        if isinstance(data_list[0], EnergaData):
            self._energa_data_list = data_list
            self._fs_data_list = None
        elif isinstance(data_list[0], FusionSolarData):
            self._fs_data_list = data_list
            self._energa_data_list = None

    def _set_source_id_in_data(self, source_id):
        if self._energa_data_list != None:
            for energa_data in self._energa_data_list:
                energa_data.source_id = source_id

        if self._fs_data_list != None:
            for fs_data in self._fs_data_list:
                fs_data.source_id = source_id

    def _get_session(self):
        username = util.get_config_param("postgresql_username")
        password = util.get_config_param("postgresql_password")
        db_name = util.get_config_param("postgresql_database")
        server = util.get_config_param("postgresql_server")
        port = util.get_config_param("postgresql_port")

        engine = create_engine(
            f'postgresql://{username}:{password}@{server}:{port}/{db_name}', echo=True)
        Session = sessionmaker(bind=engine)
        return Session()

    def save(self):
        if self._energa_data_list == None and self._fs_data_list == None:
            raise AttributeError(
                "Either EnergaDataList or FsDataList must be given")

        session = self._get_session()
        session.add(self._pv_source)
        session.commit()

        pv_source_id = self._pv_source.id
        self._set_source_id_in_data(pv_source_id)

        if self._energa_data_list != None:
            session.add_all(self._energa_data_list)
        if self._fs_data_list != None:
            session.add_all(self._fs_data_list)

        session.commit()
        session.close()

    def get_last_process_date(self):
        session = self._get_session()

        if self._fs_data_list != None:
            result = session.query(func.max(FusionSolarData.time)).first()
        elif self._energa_data_list != None:
            result = session.query(func.max(EnergaData.time)).first()

        if result[0] != None and len(result) != 0:
            return result[0]
        else:
            return datetime(2022, 8, 10)
