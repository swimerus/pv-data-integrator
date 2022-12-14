from datetime import datetime, timedelta, timezone
import json

from modules.fusion_solar.client import Client
from modules.utils import util


class DataRetriever():

    def __init__(self):
        self._username = util.get_config_param('huawei_username')
        self._password = util.get_config_param('huawei_password')

        self.client = Client(user_name=self._username,
                             system_code=self._password)
        self._station_code = self._get_station_code()

    def _get_station_code(self):
        sl = self.client.get_station_list()
        station_code = sl['data'][0]['stationCode']
        return station_code

    def get_station_kpi_hour_and_save(self, date, date_to=None):
        org_data_dp = DataProcessor(subdir='org_files')
        modif_data_dp = DataProcessor()

        filename = f'fusion_solar_{date.strftime("%Y%m%d")}.json'

        if date_to == None:
            result = self.client.get_station_kpi_hour(
                station_code=self._station_code, date=date)
            org_data_dp.save_to_file(data=result, filename=filename)

            transformed_result = modif_data_dp.transform_response(data=result)
            modif_data_dp.save_to_file(
                data=transformed_result, filename=filename)

            return filename
        else:
            current_date = date
            while current_date <= date_to:
                self.get_station_kpi_hour_and_save(date=current_date)
                current_date += timedelta(days=1)


class DataProcessor():

    def __init__(self, subdir=None):

        self._file_dir = f'{util.get_config_param("file_dir")}/fusion_solar'
        if subdir != None:
            self._file_dir = f'{self._file_dir}/{subdir}'

    def _convert_unix_epoch(self, unix_epoch):
        tz = timezone(timedelta(hours=1))
        return datetime.fromtimestamp(unix_epoch/1000, tz=tz).strftime('%Y-%m-%d %H:%M')

    def save_to_file(self, data, filename):
        path = self._file_dir+'/'+filename
        json_data = json.dumps(data)

        with open(path, 'w') as f:
            f.write(json_data)

    def transform_response(self, data):
        result = {}
        result['source'] = 'fusion_solar'
        result['gatheringDate'] = self._convert_unix_epoch(
            data['params']['currentTime'])
        result['stationCode'] = data['params']['stationCodes']

        tmp_res = []
        for d in data['data']:
            tmp = {}
            tmp['collectTime'] = self._convert_unix_epoch(d['collectTime'])
            tmp['inverterPower [kWh]'] = d['dataItemMap']['inverter_power']
            tmp['powerProfit [kWh]'] = d['dataItemMap']['power_profit']

            tmp_res.append(tmp)

        result['data'] = tmp_res

        return result
